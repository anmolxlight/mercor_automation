from . import airtable
from .schema import *
def upsert_personal(applicant_id,personal):
    if not personal:
        return
    fields={F_APPLICANT_ID:applicant_id}
    if personal.get("name") is not None: fields[F_PERSONAL_NAME]=personal.get("name")
    if personal.get("email") is not None: fields[F_PERSONAL_EMAIL]=personal.get("email")
    if personal.get("location") is not None: fields[F_PERSONAL_LOCATION]=personal.get("location")
    if personal.get("linkedin") is not None: fields[F_PERSONAL_LINKEDIN]=personal.get("linkedin")
    airtable.upsert_by_field(PERSONAL_TABLE,F_APPLICANT_ID,applicant_id,fields)
def upsert_salary(applicant_id,salary):
    if not salary:
        return
    fields={F_APPLICANT_ID:applicant_id}
    if salary.get("preferred_rate") is not None: fields[F_SAL_RATE_PREF]=salary.get("preferred_rate")
    if salary.get("minimum_rate") is not None: fields[F_SAL_RATE_MIN]=salary.get("minimum_rate")
    if salary.get("currency") is not None: fields[F_SAL_CURRENCY]=salary.get("currency")
    if salary.get("availability") is not None: fields[F_SAL_AVAIL]=salary.get("availability")
    airtable.upsert_by_field(SALARY_TABLE,F_APPLICANT_ID,applicant_id,fields)
def sync_experience(applicant_id,experience):
    current=airtable.list_records(EXPERIENCE_TABLE,formula=f'{{{F_APPLICANT_ID}}}="{applicant_id}"')
    want=experience or []
    want_norm=[{k:v for k,v in e.items() if v is not None} for e in want]
    def key(e): return (e.get("company") or "",e.get("title") or "",e.get("start") or "",e.get("end") or "")
    current_map={key({k:v for k,v in r.get("fields",{}).items() if k in [F_EXP_COMPANY,F_EXP_TITLE,F_EXP_START,F_EXP_END]}):r for r in current}
    want_map={key({"company":e.get("company"),"title":e.get("title"),"start":e.get("start"),"end":e.get("end")}):e for e in want_norm}
    for k,r in list(current_map.items()):
        if k not in want_map:
            pass
    for e in want_norm:
        fields={F_APPLICANT_ID:applicant_id}
        if e.get("company") is not None: fields[F_EXP_COMPANY]=e.get("company")
        if e.get("title") is not None: fields[F_EXP_TITLE]=e.get("title")
        if e.get("start") is not None: fields[F_EXP_START]=e.get("start")
        if e.get("end") is not None: fields[F_EXP_END]=e.get("end")
        if e.get("technologies") is not None: fields[F_EXP_TECH]=e.get("technologies")
        airtable.create_record(EXPERIENCE_TABLE,fields)
def decompress_one(applicant_id,parsed_json):
    upsert_personal(applicant_id,parsed_json.get("personal"))
    upsert_salary(applicant_id,parsed_json.get("salary"))
    sync_experience(applicant_id,parsed_json.get("experience"))
