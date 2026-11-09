from pathlib import Path

import requests

endpoint="http://localhost:3030/kg-23p-0044/sparql"
Path("results").mkdir(exist_ok=True)

for i in range(1,7):
    query=Path(f"queries/q{i}.rq").read_text(encoding="utf-8")
    reply=requests.post(endpoint,data={"query": query},headers={"Accept": "text/csv"},timeout=60)
    reply.raise_for_status()
    Path(f"results/q{i}.csv").write_text(reply.text,encoding="utf-8")
    rows=max(0,len(reply.text.strip().splitlines())-1)
    print(f"q{i}: {rows} result rows -> results/q{i}.csv")
