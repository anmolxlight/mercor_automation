import requests,urllib.parse
from .config import AIRTABLE_API_KEY,AIRTABLE_BASE_ID,AIRTABLE_API_URL,AIRTABLE_TIMEOUT
def _headers():
    return {"Authorization":f"Bearer {AIRTABLE_API_KEY}","Content-Type":"application/json"}
def _url(table):
    return f"{AIRTABLE_API_URL}/{AIRTABLE_BASE_ID}/{urllib.parse.quote(table)}"
def list_records(table,formula=None,fields=None,page_size=100):
    params={}
    if formula:
        params["filterByFormula"]=formula
    if fields:
        for i,f in enumerate(fields):
            params[f"fields[{i}]"]=f
    offset=None
    out=[]
    while True:
        if offset:
            params["offset"]=offset
        r=requests.get(_url(table),headers=_headers(),params=params,timeout=AIRTABLE_TIMEOUT)
        r.raise_for_status()
        data=r.json()
        out.extend(data.get("records",[]))
        offset=data.get("offset")
        if not offset:
            break
    return out
def find_one_by_field(table,field,value):
    v=str(value).replace('"','\"')
    recs=list_records(table,formula=f'{{{field}}}="{v}"',page_size=1)
    return recs[0] if recs else None
def create_record(table,fields):
    r=requests.post(_url(table),headers=_headers(),json={"fields":fields},timeout=AIRTABLE_TIMEOUT)
    r.raise_for_status()
    return r.json()
def update_record(table,record_id,fields):
    r=requests.patch(f"{_url(table)}/{record_id}",headers=_headers(),json={"fields":fields},timeout=AIRTABLE_TIMEOUT)
    r.raise_for_status()
    return r.json()
def upsert_by_field(table,uniq_field,uniq_value,fields):
    ex=find_one_by_field(table,uniq_field,uniq_value)
    if ex:
        return update_record(table,ex["id"],fields)
    return create_record(table,fields)
