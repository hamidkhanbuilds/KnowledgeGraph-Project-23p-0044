import csv
import time
from pathlib import Path

import requests

contact="p230044@pwr.nu.edu.pk"
titles=["Richard Feynman","Sheldon Glashow","James Chadwick",
          "Werner Heisenberg","Erwin Schrödinger"]
props={"P19": "bornIn","P69": "educatedAt","P166": "receivedAward",
         "P108": "worksAt","P184": "doctoralAdvisor"}
endpoint="https://query.wikidata.org/sparql"

query="""
SELECT ?person ?prop ?value ?valueLabel (GROUP_CONCAT(DISTINCT ?alt; separator="|") AS ?aliases)
WHERE {
  ?article schema:about ?person ;
           schema:isPartOf <https://en.wikipedia.org/> ;
           schema:name "%s"@en .
  ?person ?prop ?value .
  FILTER (?prop IN (wdt:P19, wdt:P69, wdt:P166, wdt:P108, wdt:P184))
  ?value rdfs:label ?valueLabel . FILTER (LANG(?valueLabel) = "en")
  OPTIONAL { ?value skos:altLabel ?alt . FILTER (LANG(?alt) = "en") }
}
GROUP BY ?person ?prop ?value ?valueLabel
"""

for title in titles:
    reply=requests.get(
        endpoint,
        params={"query": query%title,"format": "json"},
        headers={"User-Agent": f"KRR-coursework/1.0 ({contact})"},
        timeout=90,
    )
    reply.raise_for_status()
    rows=reply.json()["results"]["bindings"]
    out=Path("eval")/f"wikidata_{title.replace(' ','_')}.csv"
    with open(out,"w",newline="",encoding="utf-8") as f:
        w=csv.writer(f)
        w.writerow(["person","predicate","property","value_qid","value_label","aliases"])
        for r in rows:
            pid=r["prop"]["value"].rsplit("/",1)[-1]
            w.writerow([title,props[pid],pid,r["value"]["value"].rsplit("/",1)[-1],
                        r["valueLabel"]["value"],r.get("aliases",{}).get("value","")])
    print(f"{title:20s} {len(rows):3d} Wikidata values -> {out}")
    if not rows:
        print("   (nothing found: check the title spelling, or Wikidata has no data)")
    time.sleep(2)
