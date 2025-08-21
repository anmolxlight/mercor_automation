import argparse,json,sys
from .compressor import write_json,build_json
from .decompressor import decompress_one
from .shortlist import apply_shortlist
from .llm import call_with_retry,build_prompt,parse_response
from . import airtable
from .schema import *
from .util import json_hash
def compress_one(applicant):
    data,h=write_json(applicant)
    return data,h
def decompress_from_applicant(applicant):
    row=airtable.find_one_by_field(APPLICANTS_TABLE,F_APPLICANT_ID,applicant)
    if not row:
        raise SystemExit("Applicant not found")
    raw=row["fields"].get(F_COMPRESSED_JSON) or "{}"
    parsed=json.loads(raw) if isinstance(raw,str) else raw
    decompress_one(applicant,parsed)
def shortlist_one(applicant):
    merged,_=write_json(applicant)
    ok,why=apply_shortlist(applicant,merged)
    return ok,why
def llm_one(applicant):
    row=airtable.find_one_by_field(APPLICANTS_TABLE,F_APPLICANT_ID,applicant)
    if not row:
        raise SystemExit("Applicant not found")
    raw=row["fields"].get(F_COMPRESSED_JSON) or "{}"
    parsed=json.loads(raw) if isinstance(raw,str) else raw
    new_hash=json_hash(parsed)
    if row["fields"].get(F_JSON_HASH)!=new_hash:
        airtable.update_record(APPLICANTS_TABLE,row["id"],{F_COMPRESSED_JSON:json.dumps(parsed),F_JSON_HASH:new_hash})
    prompt=build_prompt(parsed)
    txt=call_with_retry(prompt)
    summary,score,follow=parse_response(txt)
    fields={}
    if summary: fields[F_LLM_SUMMARY]=summary
    if score is not None: fields[F_LLM_SCORE]=score
    if follow: fields[F_LLM_FOLLOWUPS]="\n".join(f"- {x}" for x in follow)
    airtable.update_record(APPLICANTS_TABLE,row["id"],fields)
    return summary,score,follow
def iter_all_applicants():
    recs=airtable.list_records(APPLICANTS_TABLE)
    for r in recs:
        aid=r["fields"].get(F_APPLICANT_ID)
        if aid: yield aid
def main():
    p=argparse.ArgumentParser()
    sub=p.add_subparsers(dest="cmd",required=True)
    s1=sub.add_parser("compress"); s1.add_argument("--applicant",required=True)
    s2=sub.add_parser("compress_all")
    s3=sub.add_parser("decompress"); s3.add_argument("--applicant",required=True)
    s4=sub.add_parser("shortlist"); s4.add_argument("--applicant",required=True)
    s5=sub.add_parser("shortlist_all")
    s6=sub.add_parser("llm"); s6.add_argument("--applicant",required=True)
    s7=sub.add_parser("llm_all")
    s8=sub.add_parser("run_all"); s8.add_argument("--applicant",required=True)
    s9=sub.add_parser("run_all_all")
    args=p.parse_args()
    if args.cmd=="compress":
        data,h=compress_one(args.applicant); print(json.dumps({"hash":h,"json":data},ensure_ascii=False))
    elif args.cmd=="compress_all":
        out=[]
        for aid in iter_all_applicants():
            data,h=compress_one(aid); out.append({"applicant":aid,"hash":h})
        print(json.dumps(out,ensure_ascii=False))
    elif args.cmd=="decompress":
        decompress_from_applicant(args.applicant); print("ok")
    elif args.cmd=="shortlist":
        ok,why=shortlist_one(args.applicant); print(json.dumps({"shortlisted":ok,"reason":why},ensure_ascii=False))
    elif args.cmd=="shortlist_all":
        out=[]
        for aid in iter_all_applicants():
            ok,why=shortlist_one(aid); out.append({"applicant":aid,"shortlisted":ok})
        print(json.dumps(out,ensure_ascii=False))
    elif args.cmd=="llm":
        summary,score,follow=llm_one(args.applicant)
        result={
            "summary":summary,
            "score":score,
            "follow_ups":follow
        }
        print(json.dumps(result,ensure_ascii=False))
    elif args.cmd=="llm_all":
        out=[]
        for aid in iter_all_applicants():
            summary,score,follow=llm_one(aid)
            out.append({
                "applicant":aid,
                "summary":summary,
                "score":score,
                "follow_ups":follow
            })
        print(json.dumps(out,ensure_ascii=False))
    elif args.cmd=="run_all":
        compress_one(args.applicant); shortlist_one(args.applicant); llm_one(args.applicant); print("ok")
    elif args.cmd=="run_all_all":
        for aid in iter_all_applicants():
            compress_one(aid); shortlist_one(aid); llm_one(aid)
        print("ok")
if __name__=="__main__":
    main()
