"""Invented fixtures. Never pass these off as current property listings."""
from datetime import datetime, timezone

def observations():
    result=[]
    for i,rate in enumerate([5900,6000,6200,6500,6900]):
        result.append({'title':f'Synthetic apartment {i+1}','project':f'Example project {i+1}',
          'city':'Bengaluru','locality':'Electronic City','bedrooms':2,'property_type':'apartment','transaction_type':'sale',
          'price_raw':str(rate*1200),'area_raw':'1200 sq ft','area_basis':'Super built-up','listed_at':None,
          'source_url':f'https://sample-{i%2+1}.example/property/{i+1}',
          'retrieved_at':datetime.now(timezone.utc).isoformat()})
    result.append(dict(result[0],title='Repeated example listing'))
    result.append(dict(result[0],title='Incompatible carpet area',source_url='https://sample-1.example/property/7',area_basis='Carpet'))
    result.append(dict(result[0],title='Rental example',source_url='https://sample-1.example/property/8',transaction_type='rent'))
    return result
