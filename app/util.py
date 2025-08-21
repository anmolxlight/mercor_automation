import hashlib,json,time,random
def json_dumps(obj):
    return json.dumps(obj,ensure_ascii=False,separators=(",",":"),sort_keys=True)
def json_hash(obj):
    return hashlib.sha256(json_dumps(obj).encode("utf-8")).hexdigest()
def backoff_attempts(n,base):
    t=1.0
    for i in range(n):
        yield t
        t*=base+random.random()*0.1
