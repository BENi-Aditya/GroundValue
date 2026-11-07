"""Deterministic evidence checks. No network or model-generated valuations."""
from dataclasses import dataclass, asdict
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode
from statistics import median
from math import isfinite
import re

BASES = ('Super built-up', 'Built-up', 'Carpet')
METHOD = 'comparable-asking-v4-explicit-locality'

def text(value):
    return str(value or '').strip()

def compact(value):
    return re.sub(r'[^a-z0-9]', '', text(value).lower())

def locality(value):
    v = compact(value)
    v = v.replace('electronicscity', 'electroniccity')
    return v

def within_locality(value, target):
    if locality(value)==locality(target): return True
    if locality(target)!='electroniccity': return False
    # Only explicit region labels, not "near Electronic City" or a substring match.
    labels={'electroniccity','electroniccityphase1','electroniccityphasei',
            'electroniccityphase2','electroniccityphaseii','phase1electroniccity',
            'phaseielectroniccity','phase2electroniccity','phaseiielectroniccity',
            'electroniccity1stphase','electroniccity2ndphase',
            }  # Nearby neighborhoods alone do not establish an Electronic City match.
    outer=re.sub(r'\([^)]*\)','',text(value))
    return any(locality(part) in labels for part in outer.split(','))

def safe_url(value, domains=None):
    try:
        p = urlsplit(text(value))
        host = (p.hostname or '').lower()
        if p.scheme != 'https' or not host or p.username or p.password or p.port not in (None, 443):
            return None
        if domains and not any(host == d or host.endswith('.' + d) for d in domains):
            return None
        qs = [(k,v) for k,v in parse_qsl(p.query) if not k.lower().startswith('utm_') and k.lower() not in ('gclid','fbclid')]
        return urlunsplit(('https',host,p.path.rstrip('/') or '/',urlencode(sorted(qs)),''))
    except (ValueError, TypeError):
        return None

def money(value):
    s = text(value).lower().replace(',', '')
    s = re.sub(r'^(?:inr|rs\.?|₹)\s*', '', s)
    m = re.fullmatch(r'(\d+(?:\.\d+)?)\s*(lakh|lakhs|lac|lacs|l|crore|crores|cr)?', s)
    if not m:
        raise ValueError('Missing or ambiguous asking price')
    n = float(m[1]) * ({'lakh':1e5,'lakhs':1e5,'lac':1e5,'lacs':1e5,'l':1e5,'crore':1e7,'crores':1e7,'cr':1e7}.get(m[2],1))
    if not isfinite(n) or n <= 0:
        raise ValueError('Asking price must be positive')
    return n

def area(value):
    s = text(value).lower().replace(',', '').replace('²','2')
    # First try with unit
    m = re.fullmatch(r'(\d+(?:\.\d+)?)\s*(sq\.?\s*ft\.?|sqft|square feet|ft2|sq\.?\s*m\.?|sqm|square metres|square meters|m2)', s)
    if m:
        n = float(m[1]) * (10.7639 if re.search(r'm|met',m[2]) else 1)
    else:
        raise ValueError('Missing or ambiguous area or unit')
    if not isfinite(n) or n <= 0:
        raise ValueError('Area must be positive')
    return n

@dataclass
class Property:
    city: str = 'Bengaluru'
    locality: str = 'Electronic City'
    bedrooms: int = 2
    area: float = 1200
    unit: str = 'sq ft'
    area_basis: str = 'Super built-up'

    def validate(self):
        if compact(self.city) not in ('bengaluru','bangalore') or locality(self.locality) != 'electroniccity':
            raise ValueError('This MVP supports Electronic City, Bengaluru only.')
        if type(self.bedrooms) is not int or not 1 <= self.bedrooms <= 5:
            raise ValueError('Choose 1 to 5 bedrooms.')
        if self.area_basis not in BASES or self.unit not in ('sq ft','sq m'):
            raise ValueError('Choose a supported area basis and unit.')
        if isinstance(self.area,bool) or not isinstance(self.area,(int,float)) or not isfinite(self.area) or self.area <= 0:
            raise ValueError('Enter a positive finite property area.')
        return self

    @property
    def sqft(self):
        return self.area * (10.7639 if self.unit == 'sq m' else 1)

def percentile(values, fraction):
    ordered = sorted(values)
    index = (len(ordered)-1)*fraction
    lo = int(index)
    hi = min(lo+1,len(ordered)-1)
    return ordered[lo] + (ordered[hi]-ordered[lo])*(index-lo)

def analyse(target, observations, mode, jobs=None, domains=None):
    target.validate()
    if mode not in ('sample','live'): raise ValueError('Invalid evidence mode')
    if not isinstance(observations,list): raise ValueError('Listings must be an array')
    records=[]
    for number, raw in enumerate(observations):
        rec={'id':number+1,'raw':raw,'included':False,'reason':'','warnings':[]}
        try:
            if not isinstance(raw,dict): raise ValueError('Malformed listing record')
            if any(isinstance(v,str) and len(v)>5000 for v in raw.values()): raise ValueError('Oversized listing field')
            url=safe_url(raw.get('source_url'),domains)
            if not url: raise ValueError('Missing or unapproved HTTPS source URL')
            rec.update(source_url=url,source_domain=urlsplit(url).hostname,title=text(raw.get('title')),
                       project=text(raw.get('project')),locality=text(raw.get('locality')),
                       retrieved_at=text(raw.get('retrieved_at')),listed_at=text(raw.get('listed_at')))
            if compact(raw.get('city')) not in ('bangalore','bengaluru'): raise ValueError('Wrong or unknown city')
            if not within_locality(raw.get('locality'),target.locality): raise ValueError('Wrong or unknown locality')
            if locality(raw.get('locality')) != locality(target.locality): rec['warnings'].append('Within Electronic City region; sub-locality differs')
            kind=re.sub(r'^'+str(target.bedrooms)+r'bhk','',compact(raw.get('property_type')))
            if kind not in ('apartment','flat'): raise ValueError('Not a sale apartment')
            if compact(raw.get('transaction_type')) not in ('sale','resale','forsale'): raise ValueError('Not a sale listing')
            if type(raw.get('bedrooms')) is not int or raw['bedrooms']!=target.bedrooms: raise ValueError('Bedroom count does not match')
            if compact(raw.get('area_basis')).removesuffix('area') != compact(target.area_basis): raise ValueError('Area basis missing or incompatible')
            rec['price_inr']=money(raw.get('price_raw'))
            rec['area_sqft']=area(raw.get('area_raw'))
            rec['rate_inr_sqft']=rec['price_inr']/rec['area_sqft']
            if not .75*target.sqft <= rec['area_sqft'] <= 1.25*target.sqft: raise ValueError('Area outside the 25% comparison window')
            if not raw.get('listed_at'):rec['warnings'].append('Listing date unknown')
            rec['included']=True
            rec['reason']='Matches location, type, bedrooms, area basis and size'
        except (ValueError,TypeError,OverflowError) as exc:
            rec['reason']=str(exc)
        records.append(rec)
    # A conflicting observation invalidates all eligible records for that exact URL.
    groups={}
    for r in records:
        if r['included']:groups.setdefault(r['source_url'],[]).append(r)
    for group in groups.values():
        fingerprints={(r['price_inr'],r['area_sqft']) for r in group}
        if len(fingerprints)>1:
            for r in group:r.update(included=False,reason='Conflicting price or area for the same source URL')
        else:
            for r in group[1:]:r.update(included=False,reason='Duplicate source URL')
    seen={}
    for r in records:
        if not r['included'] or not compact(r['project']):continue
        fingerprint=(compact(r['project']),locality(r['locality']),round(r['area_sqft'],1),round(r['price_inr'],0))
        previous=seen.get(fingerprint)
        if previous:
            r.update(included=False,reason='Probable duplicate property; retained one representative')
            previous['warnings'].append('Probable duplicate grouped; identity is unverified')
        else:seen[fingerprint]=r
    accepted=[r for r in records if r['included']]
    sources=len({r['source_domain'] for r in accepted})
    warnings=['Asking prices are not completed sale values. The range is an observed comparison band, not a confidence interval.']
    if mode=='sample':warnings.insert(0,'SYNTHETIC SAMPLE: invented properties and prices, not live market evidence.')
    if sources<2:warnings.append('Fewer than two independent source domains supplied usable evidence.')
    if any(not r['listed_at'] for r in accepted):warnings.append('Some listing dates are unknown. Retrieval does not establish freshness or availability.')
    jobs=jobs or []
    if any(j.get('status')!='completed' for j in jobs):warnings.append('Source coverage is incomplete. Review the source jobs below.')
    estimate=None
    if len(accepted)>=5:
        rates=[r['rate_inr_sqft'] for r in accepted]
        estimate={'value':median(rates)*target.sqft,'low':percentile(rates,.25)*target.sqft,
                  'high':percentile(rates,.75)*target.sqft,'median_rate':median(rates)}
    return {'property':asdict(target),'mode':mode,'method':METHOD,'records':records,'jobs':jobs,'estimate':estimate,
            'accepted_count':len(accepted),'source_count':sources,'warnings':warnings}
