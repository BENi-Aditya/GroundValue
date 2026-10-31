"""Small dependency-free OOXML export; every string is an inline string, never a formula."""
from io import BytesIO
from zipfile import ZipFile,ZIP_DEFLATED
from xml.sax.saxutils import escape
import json,re

def workbook(project,runs):
    def scalar(x):return json.dumps(x,ensure_ascii=False) if isinstance(x,(dict,list)) else x
    def safe(x):return escape(re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]','',str(scalar(x) if x is not None else '')))
    sheets={'Property Details':[['Field','Value']]+[[k,scalar(v)] for k,v in dict(name=project['name'],**project['details']).items()], 'Valuation Summary':[['Run','Status','Value INR','Low INR','High INR','Method']], 'Research Sources':[['Run','Title','URL','Retrieved','Included','Reason']], 'Research Runs':[['Run','Status','Started','Updated','Input','Error']], 'Extracted Data':[['Run','Record']], 'Activity History':[['Run','Time','Source','Kind','Message']]}
    for run in runs:
        j=run['snapshot'];r=j.get('report') or {};v=r.get('estimate') or {}
        sheets['Valuation Summary'].append([run['id'],run['status'],v.get('value'),v.get('low'),v.get('high'),r.get('method')])
        sheets['Research Runs'].append([run['id'],run['status'],run['started'],run['updated'],run['input'],j.get('error')])
        for row in r.get('records',[]):
            sheets['Research Sources'].append([run['id'],row.get('title'),row.get('source_url'),row.get('retrieved_at'),row.get('included'),row.get('reason')]);sheets['Extracted Data'].append([run['id'],row])
        for e in j.get('events',[]):sheets['Activity History'].append([run['id'],e.get('at'),e.get('source'),e.get('kind'),e.get('message')])
    out=BytesIO();ns='http://schemas.openxmlformats.org/spreadsheetml/2006/main'
    with ZipFile(out,'w',ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml','<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'+''.join(f'<Override PartName="/xl/worksheets/sheet{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>' for i in range(1,7))+'</Types>')
        z.writestr('_rels/.rels','<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>')
        z.writestr('xl/workbook.xml',f'<workbook xmlns="{ns}" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>'+''.join(f'<sheet name="{n}" sheetId="{i}" r:id="rId{i}"/>' for i,n in enumerate(sheets,1))+'</sheets></workbook>')
        z.writestr('xl/styles.xml',f'<styleSheet xmlns="{ns}"><fonts count="2"><font><sz val="11"/><name val="Calibri"/></font><font><b/><color rgb="FFFFFFFF"/><sz val="11"/></font></fonts><fills count="3"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill><fill><patternFill patternType="solid"><fgColor rgb="FF173D32"/></patternFill></fill></fills><borders count="1"><border/></borders><cellStyleXfs count="1"><xf/></cellStyleXfs><cellXfs count="2"><xf fontId="0" fillId="0" borderId="0"/><xf fontId="1" fillId="2" borderId="0" applyFont="1" applyFill="1"/></cellXfs></styleSheet>')
        z.writestr('xl/_rels/workbook.xml.rels','<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="style" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'+''.join(f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{i}.xml"/>' for i in range(1,7))+'</Relationships>')
        for i,rows in enumerate(sheets.values(),1):
            xml=f'<worksheet xmlns="{ns}"><sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" state="frozen"/></sheetView></sheetViews><cols>'+''.join(f'<col min="{c}" max="{c}" width="{24 if c<3 else 42}" customWidth="1"/>' for c in range(1,len(rows[0])+1))+'</cols><sheetData>'
            for ri,row in enumerate(rows,1):
                xml+=f'<row r="{ri}">'+''.join(f'<c r="{chr(65+ci)}{ri}" s="{1 if ri==1 else 0}"'+(f'><v>{v}</v></c>' if isinstance(v,(int,float)) and not isinstance(v,bool) else f' t="inlineStr"><is><t xml:space="preserve">{safe(v)}</t></is></c>') for ci,v in enumerate(row))+'</row>'
            z.writestr(f'xl/worksheets/sheet{i}.xml',xml+'</sheetData></worksheet>')
    return out.getvalue()
