from pathlib import Path

from pyshacl import validate
from rdflib import Graph

data=Graph().parse("out/kg.ttl",format="turtle")
shapes=Graph().parse("shapes.ttl",format="turtle")

conforms,reportgraph,reporttext=validate(
    data,shacl_graph=shapes,inference="none",abort_on_first=False)

Path("shacl_report.txt").write_text(reporttext,encoding="utf-8")
print("Conforms:",conforms)
print(reporttext)
