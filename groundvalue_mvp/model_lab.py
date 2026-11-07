"""Reproducible research model. No bundled data or claimed external AVM accuracy."""
import csv,io,json,hashlib,uuid,math
from datetime import date
import numpy as np
import projects

NUMERIC=['area_sqft','bedrooms','age_years','latitude','longitude','metro_km']
CATEGORICAL=['city','property_type','area_basis']
FIELDS=['transaction_id','building_id','sale_date','sale_price_inr',*NUMERIC,*CATEGORICAL,'source_url']

def init(db):
    db.execute('CREATE TABLE IF NOT EXISTS datasets(id TEXT PRIMARY KEY,created TEXT,manifest TEXT,rows TEXT)')
    db.execute('CREATE TABLE IF NOT EXISTS model_versions(id TEXT PRIMARY KEY,created TEXT,artifact TEXT)')

def template(): return ','.join(FIELDS)+'\n'

def ingest(content,source,access_basis):
    if not source.strip() or not access_basis.strip(): raise ValueError('Dataset source and access basis are required.')
    from core import safe_url
    reader=csv.DictReader(io.StringIO(content))
    if not reader.fieldnames or not set(FIELDS)<=set(reader.fieldnames):
        raise ValueError('CSV must contain every column in the template.')
    rows=[]; rejected=[]; seen=set()
    for index,row in enumerate(reader,2):
        if index>10001: raise ValueError('Limit this research dataset to 10,000 rows.')
        try:
            r={k:str(row.get(k) or '').strip() for k in FIELDS}
            if any(len(v)>1000 for v in r.values()): raise ValueError('Oversized field')
            if not r['transaction_id'] or r['transaction_id'] in seen: raise ValueError('Missing or duplicate transaction ID')
            if not r['building_id'] or not r['city']: raise ValueError('Building ID and city required')
            when=date.fromisoformat(r['sale_date'])
            if when>date.today(): raise ValueError('Future transaction date')
            if r['property_type'] not in ('apartment','office','retail'): raise ValueError('Use apartment, office or retail')
            if r['area_basis'] not in ('Built-up','Super built-up','Carpet'): raise ValueError('Unknown area basis')
            if not safe_url(r['source_url']): raise ValueError('HTTPS source citation required')
            for k in NUMERIC+['sale_price_inr']:
                r[k]=float(r[k])
                if not math.isfinite(r[k]): raise ValueError('Non-finite numeric value')
            if not 50<=r['area_sqft']<=100000 or not 10000<=r['sale_price_inr']<=1e11: raise ValueError('Price or area outside supported bounds')
            if not 0<=r['bedrooms']<=20 or not 0<=r['age_years']<=200 or not 0<=r['metro_km']<=300: raise ValueError('Invalid property attributes')
            if not 6<=r['latitude']<=38 or not 68<=r['longitude']<=98: raise ValueError('Coordinates outside supported India bounds')
            seen.add(r['transaction_id']);rows.append(r)
        except (ValueError,TypeError) as exc: rejected.append({'row':index,'reason':str(exc)})
    if not rows: raise ValueError('No valid transactions. '+str(rejected[:3]))
    manifest={'id':uuid.uuid4().hex,'created':projects.now(),'source':source[:2000],
        'access_basis':access_basis[:2000],'sha256':hashlib.sha256(content.encode()).hexdigest(),
        'accepted':len(rows),'rejected_count':len(rejected),'rejected':rejected,
        'cities':sorted({r['city'] for r in rows}),'types':sorted({r['property_type'] for r in rows}),
        'label_status':'User-supplied transaction labels; not independently verified'}
    with projects.connect() as db:
        init(db);db.execute('INSERT INTO datasets VALUES(?,?,?,?)',(manifest['id'],manifest['created'],json.dumps(manifest),json.dumps(rows)))
    return manifest

def listing():
    with projects.connect() as db:
        init(db)
        datasets=[json.loads(r[0]) for r in db.execute('SELECT manifest FROM datasets ORDER BY created DESC')]
        models=[json.loads(r[0]) for r in db.execute('SELECT artifact FROM model_versions ORDER BY created DESC')]
    return {'datasets':datasets,'models':models,'template_fields':FIELDS}

def vector(row,categories):
    values=[math.log(float(row['area_sqft']))]+[float(row[k]) for k in NUMERIC[1:]]
    return values+[float(row[k]==v) for k in CATEGORICAL for v in categories[k]]

def metrics(actual,pred):
    err=np.abs(actual-pred);den=np.sum((actual-actual.mean())**2)
    return {'mae_inr':float(err.mean()),'rmse_inr':float(np.sqrt(np.mean((actual-pred)**2))),
        'median_ape_pct':float(np.median(err/actual)*100),'r2':float(1-np.sum((actual-pred)**2)/den) if den else None}

def train(dataset_id):
    with projects.connect() as db:
        init(db);item=db.execute('SELECT manifest,rows FROM datasets WHERE id=?',(dataset_id,)).fetchone()
    if not item: raise ValueError('Dataset not found.')
    manifest=json.loads(item[0]);rows=sorted(json.loads(item[1]),key=lambda r:r['sale_date'])
    if len(rows)<120: raise ValueError('At least 120 usable transactions are required for train/calibration/test splits.')
    # Strict temporal boundaries; remove building overlap instead of moving future rows into training.
    cut1=rows[int(len(rows)*.6)]['sale_date'];cut2=rows[int(len(rows)*.8)]['sale_date']
    fit=[r for r in rows if r['sale_date']<cut1];seen={r['building_id'] for r in fit}
    cal=[r for r in rows if cut1<=r['sale_date']<cut2 and r['building_id'] not in seen]
    seen.update(r['building_id'] for r in cal)
    test=[r for r in rows if r['sale_date']>=cut2 and r['building_id'] not in seen]
    if len(fit)<60 or len(cal)<20 or len(test)<20:
        raise ValueError('Need at least 60/20/20 rows after temporal splitting and building-overlap exclusions.')
    categories={k:sorted({r[k] for r in fit}) for k in CATEGORICAL}
    if sum(len(v) for v in categories.values())>100:
        raise ValueError('Use at most 100 combined city/type/area-basis categories per research dataset.')
    supported=lambda r:all(r[k] in categories[k] for k in CATEGORICAL)
    cal=[r for r in cal if supported(r)];test=[r for r in test if supported(r)]
    if len(cal)<20 or len(test)<20: raise ValueError('Not enough calibration/test rows in categories represented in training.')
    x=np.array([vector(r,categories) for r in fit]);mean=x.mean(0);std=x.std(0);std[std<1e-9]=1
    design=lambda rs: np.column_stack([np.ones(len(rs)),(np.array([vector(r,categories) for r in rs])-mean)/std])
    xx=design(fit);yy=np.log([r['sale_price_inr'] for r in fit]);penalty=np.eye(xx.shape[1])*10;penalty[0,0]=0
    coef=np.linalg.solve(xx.T@xx+penalty,xx.T@yy)
    residual=np.sort(np.abs(np.log([r['sale_price_inr'] for r in cal])-design(cal)@coef))
    q=float(residual[min(len(residual)-1,math.ceil((len(residual)+1)*.9)-1)])
    pred=np.exp(np.clip(design(test)@coef,0,30));actual=np.array([r['sale_price_inr'] for r in test])
    # Segment comparable-rate baseline computed only from training observations.
    rates={}
    for r in fit: rates.setdefault(tuple(r[k] for k in CATEGORICAL),[]).append(r['sale_price_inr']/r['area_sqft'])
    baseline=[];eligible=[]
    for i,r in enumerate(test):
        group=tuple(r[k] for k in CATEGORICAL)
        if group in rates: baseline.append(float(np.median(rates[group]))*r['area_sqft']);eligible.append(i)
    if not eligible: raise ValueError('No test rows with a training segment baseline.')
    names=['log_area_sqft',*NUMERIC[1:]]+[k+':'+v for k in CATEGORICAL for v in categories[k]]
    result={'id':uuid.uuid4().hex,'created':projects.now(),'dataset_id':dataset_id,'dataset_sha256':manifest['sha256'],
        'method':'ridge-log-price-v1','ridge_alpha':10,'feature_names':names,'categories':categories,
        'mean':mean.tolist(),'std':std.tolist(),'coefficients':coef.tolist(),'log_interval_radius':q,
        'training_segments':[list(k) for k in rates],
        'bounds':{k:[min(r[k] for r in fit),max(r[k] for r in fit)] for k in NUMERIC},
        'counts':{'train':len(fit),'calibration':len(cal),'test':len(test),'baseline_comparison':len(eligible),
                  'excluded_from_splits':len(rows)-len(fit)-len(cal)-len(test)},
        'split_dates':{'calibration_from':cut1,'test_from':cut2},
        'test_metrics':metrics(actual,pred),'baseline_metrics':metrics(actual[eligible],np.array(baseline)),
        'matched_model_metrics':metrics(actual[eligible],pred[eligible]),
        'test_interval_coverage':float(np.mean((actual>=pred*np.exp(-q))&(actual<=pred*np.exp(q)))),
        'nominal_interval_coverage':.9,
        'segments':{city:{'n':sum(r['city']==city for r in test),**metrics(actual[[r['city']==city for r in test]],pred[[r['city']==city for r in test]])} for city in sorted({r['city'] for r in test})},
        'limitations':['Research model, not approved for lending.','Transaction labels supplied by user; authenticity is not verified.',
            'No external AVM benchmark. Baseline is a training-only median transaction rate.',
            'Temporal calibration coverage is empirical; future coverage and geographic transfer are not guaranteed.']}
    with projects.connect() as db:
        init(db);db.execute('INSERT INTO model_versions VALUES(?,?,?)',(result['id'],result['created'],json.dumps(result,allow_nan=False)))
    return result

def predict(model_id,row):
    with projects.connect() as db:
        init(db);item=db.execute('SELECT artifact FROM model_versions WHERE id=?',(model_id,)).fetchone()
    if not item: raise ValueError('Model not found.')
    model=json.loads(item[0])
    if any(row.get(k) not in model['categories'][k] for k in CATEGORICAL): raise ValueError('City, property type or area basis was not represented in training.')
    if [row[k] for k in CATEGORICAL] not in model['training_segments']:
        raise ValueError('This city / property type / area basis combination was not represented in training.')
    for k in NUMERIC:
        try: value=float(row[k])
        except (ValueError,TypeError,KeyError): raise ValueError('All numeric property features are required.')
        low,high=model['bounds'][k]
        if not math.isfinite(value) or not low<=value<=high: raise ValueError(k+' is outside the training range; refer for review.')
    z=(np.array(vector(row,model['categories']))-model['mean'])/model['std']
    contributions=z*np.array(model['coefficients'][1:]);log_value=float(model['coefficients'][0]+sum(contributions))
    value=math.exp(min(30,max(0,log_value)));q=model['log_interval_radius']
    return {'model_id':model_id,'created':projects.now(),'value':value,'low':value*math.exp(-q),'high':value*math.exp(q),
        'interval_label':'90% nominal calibrated interval; research use only',
        'observed_test_coverage':model['test_interval_coverage'],
        'factors':sorted([{'feature':k,'log_price_contribution':float(v)} for k,v in zip(model['feature_names'],contributions)],key=lambda x:abs(x['log_price_contribution']),reverse=True)[:6],
        'base_log_price':model['coefficients'][0],'limitations':model['limitations'],'input':row}
