import requests,json
from .config import LLM_PROVIDER,LLM_MAX_TOKENS,LLM_RETRY_MAX,LLM_RETRY_BASE
from .util import json_dumps,backoff_attempts

def gemini_call(prompt):
    url="https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    headers={"Content-Type":"application/json"}
    params={"key":LLM_PROVIDER}
    payload={
        "contents":[{"parts":[{"text":prompt}]}],
        "generationConfig":{"maxOutputTokens":LLM_MAX_TOKENS,"temperature":0.2}
    }
    r=requests.post(url,headers=headers,params=params,json=payload,timeout=30)
    r.raise_for_status()
    j=r.json()
    text_parts=[]
    for candidate in j.get("candidates",[]):
        for part in candidate.get("content",{}).get("parts",[]):
            if "text" in part:
                text_parts.append(part["text"])
    return "\n".join(text_parts)

def call_with_retry(prompt):
    last=None
    for t in backoff_attempts(LLM_RETRY_MAX,LLM_RETRY_BASE):
        try:
            return gemini_call(prompt)
        except Exception as e:
            last=e
            import time; time.sleep(t)
    raise last

def build_prompt(app_json):
    return f"You are a recruiting analyst. Given this JSON applicant profile, do four things:\n1. Provide a concise 75-word summary.\n2. Rate overall candidate quality from 1-10.\n3. List any data gaps or inconsistencies.\n4. Suggest up to three follow-up questions.\nReturn exactly:\nSummary: <text>\nScore: <integer>\nIssues: <comma-separated list or 'None'>\nFollow-Ups: <bullet list>\n\nJSON:\n{json_dumps(app_json)}"

def parse_response(txt):
    lines=txt.strip().splitlines()
    summary=""
    score=None
    issues=""
    follow=[]
    cur=None
    for ln in lines:
        if ln.lower().startswith("summary:"):
            summary=ln.split(":",1)[1].strip()
            cur=None
        elif ln.lower().startswith("score:"):
            v=ln.split(":",1)[1].strip()
            try: score=int(v)
            except: score=None
            cur=None
        elif ln.lower().startswith("issues:"):
            issues=ln.split(":",1)[1].strip()
            cur=None
        elif ln.lower().startswith("follow-ups:"):
            cur="fu"
        else:
            if cur=="fu":
                s=ln.strip(" -•*\t ")
                if s: follow.append(s)
    return summary,score,follow if follow else []
