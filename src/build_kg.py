import csv
from pathlib import Path
from urllib.parse import quote

from rdflib import Graph,Literal,Namespace,RDF,RDFS

kg=Namespace("http://example.org/kg/23p-0044/")


objecttype={
    "bornIn": kg.Place,
    "educatedAt": kg.Organization,
    "receivedAward": kg.Award,
    "worksAt": kg.Organization,
    "doctoralAdvisor": kg.Person,
}


def irifor(name):
    return kg[quote(name.strip().replace(" ","_"),safe="_-")]


def main():
    g=Graph()
    g.bind("kg",kg)
    g.bind("rdfs",RDFS)

    used=set()
    with open("out/triples.csv",newline="",encoding="utf-8") as f:
        for row in csv.DictReader(f):
            s,p,o=row["subject"].strip(),row["predicate"].strip(),row["object"].strip()
            if not (s and p and o) or p not in objecttype:
                continue
            if (s,p,o) in used:
                continue
            used.add((s,p,o))
            siri,oiri=irifor(s),irifor(o)
            g.add((siri,RDF.type,kg.Person))
            g.add((siri,RDFS.label,Literal(s)))
            g.add((oiri,RDF.type,objecttype[p]))
            g.add((oiri,RDFS.label,Literal(o)))
            g.add((siri,kg[p],oiri))

    Path("out").mkdir(exist_ok=True)
    g.serialize("out/kg.ttl",format="turtle")
    print(f"{len(used)} distinct facts -> {len(g)} RDF triples written to out/kg.ttl")


if __name__=="__main__":
    main()
