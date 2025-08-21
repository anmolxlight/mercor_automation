from . import airtable
from .schema import *
from .util import json_dumps,json_hash
def build_json(applicant_id):
    a=airtable.find_one_by_field(APPLICANTS_TABLE,F_APPLICANT_ID,applicant_id)
    if not a:
        raise ValueError("Applicant not found")
    pid=a["fields"].get(F_APPLICANT_ID)
    pers=airtable.find_one_by_field(PERSONAL_TABLE,F_APPLICANT_ID,pid)
    sal=airtable.find_one_by_field(SALARY_TABLE,F_APPLICANT_ID,pid)
    exps=airtable.list_records(EXPERIENCE_TABLE,formula=f'{{{F_APPLICANT_ID}}}="{pid}"')
    personal={}
    salary={}
    experience=[]
    if pers:
        pf=pers.get("fields",{})
        personal={
            "name":pf.get(F_PERSONAL_NAME),
            "email":pf.get(F_PERSONAL_EMAIL),
            "location":pf.get(F_PERSONAL_LOCATION),
            "linkedin":pf.get(F_PERSONAL_LINKEDIN)
        }
    if sal:
        sf=sal.get("fields",{})
        salary={
            "preferred_rate":sf.get(F_SAL_RATE_PREF),
            "minimum_rate":sf.get(F_SAL_RATE_MIN),
            "currency":sf.get(F_SAL_CURRENCY),
            "availability":sf.get(F_SAL_AVAIL)
        }
    for e in exps:
        ef=e.get("fields",{})
        experience.append({
            "company":ef.get(F_EXP_COMPANY),
            "title":ef.get(F_EXP_TITLE),
            "start":ef.get(F_EXP_START),
            "end":ef.get(F_EXP_END),
            "technologies":ef.get(F_EXP_TECH)
        })
    data={"personal":personal,"experience":experience,"salary":salary}
    return data
def write_json(applicant_id):
    data=build_json(applicant_id)
    h=json_hash(data)
    airtable.upsert_by_field(APPLICANTS_TABLE,F_APPLICANT_ID,applicant_id,{F_COMPRESSED_JSON:json_dumps(data),F_JSON_HASH:h})
    return data,h
