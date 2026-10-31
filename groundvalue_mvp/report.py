import csv,html,io

def rupees(n):return f'₹{n/100000:,.2f} lakh'

def csv_report(report):
    stream=io.StringIO(newline='');w=csv.writer(stream)
    w.writerow(['evidence_mode','included','title','price_inr','area_sqft','area_basis','source_url','retrieved_at','reason'])
    for r in report['records']:
        raw=r.get('raw') if isinstance(r.get('raw'),dict) else {}
        row=[report['mode'],r['included'],r.get('title',''),r.get('price_inr',''),r.get('area_sqft',''),raw.get('area_basis',''),r.get('source_url',''),r.get('retrieved_at',''),r['reason']]
        w.writerow(["'"+v if isinstance(v,str) and v.lstrip().startswith(('=','+','-','@','\t','\r')) else v for v in row])
    return stream.getvalue()

def html_report(report):
    e=html.escape
    estimate=report['estimate']
    summary=(f"{rupees(estimate['value'])} · observed range {rupees(estimate['low'])} to {rupees(estimate['high'])}" if estimate else 'Insufficient evidence: at least five usable comparisons are required.')
    rows=[]
    for r in report['records']:
        link=f'<a href="{e(r["source_url"],quote=True)}">Source</a>' if r.get('source_url') and report['mode']=='live' else 'Synthetic sample'
        rows.append('<tr>'+''.join('<td>'+e(str(x))+'</td>' for x in [r.get('title','Invalid record'),r.get('price_inr',''),r.get('area_sqft',''),r['reason']])+f'<td>{link}</td></tr>')
    p=report['property']
    details=f"{p['bedrooms']} BHK · {p['area']:g} {p['unit']} · {p['area_basis']} · {p['locality']}, {p['city']}"
    timestamp=report.get('created_at','Not saved')
    return '<!doctype html><html><meta charset="utf-8"><title>GroundValue evidence report</title><style>body{font:16px system-ui;max-width:1050px;margin:48px auto;padding:24px;color:#16342e}table{border-collapse:collapse;width:100%}td,th{padding:12px;border:1px solid #ccd7cf;text-align:left}h1{font-size:40px}</style><h1>GroundValue</h1><p>'+e(report['mode'].upper()+' EVIDENCE')+'</p><p>'+e(details)+'</p><p>Saved: '+e(timestamp)+'</p><h2>'+e(summary)+'</h2>'+''.join('<p>'+e(w)+'</p>' for w in report['warnings'])+'<p>Method: '+e(report['method'])+'</p><table><tr><th>Property</th><th>INR</th><th>Sq ft</th><th>Decision</th><th>Evidence</th></tr>'+''.join(rows)+'</table></html>'
