import requests

dataset="kg-23p-0044"
url=f"http://localhost:3030/{dataset}/data?default"

with open("out/kg.ttl","rb") as f:
    reply=requests.put(url,data=f.read(),headers={"Content-Type": "text/turtle"},timeout=60)
print("HTTP",reply.status_code,reply.text[:200])
reply.raise_for_status()
