import argparse
import csv
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path


fppositions=[8,17,18,20]
fnpositions=[9,10,16,17]
predicates=["bornIn","educatedAt","receivedAward","worksAt","doctoralAdvisor"]


def norm(text):
    text=unicodedata.normalize("NFKD",text)
    text="".join(c for c in text if not unicodedata.combining(c)).lower()
    text=re.sub(r"[^a-z0-9]+"," ",text).strip()
    return re.sub(r"^the ","",text)


def wrap(position,length):
    return ((position-1)%length)+1


def loadwikidata():
    people={}
    for path in sorted(Path("eval").glob("wikidata_*.csv")):
        rows=list(csv.DictReader(open(path,encoding="utf-8")))
        title=path.stem.replace("wikidata_","").replace("_"," ")
        people[title]=rows
    return people


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--run",default="before")
    args=ap.parse_args()

    wd=loadwikidata()
    if not wd:
        sys.exit("No eval/wikidata_*.csv files found. Run eval/fetch_wikidata.py first.")

    extracted=defaultdict(set)
    sentenceof={}
    for r in csv.DictReader(open("out/triples.csv",encoding="utf-8")):
        if r["predicate"] in predicates:
            extracted[(r["subject"],r["predicate"])].add(r["object"])
            sentenceof.setdefault((r["subject"],r["predicate"],r["object"]),r["sentence"])


    wdbyfold={norm(t): t for t in wd}
    counts={p: {"TP": 0,"FP": 0,"FN": 0} for p in predicates}
    fps,fns=[],[]

    for (subj,pred),objs in extracted.items():
        title=wdbyfold.get(norm(subj))
        if title is None:
            continue
        values=[v for v in wd[title] if v["predicate"]==pred]
        forms=[{norm(v["value_label"])}|{norm(a) for a in v["aliases"].split("|") if a} for v in values]
        for o in objs:
            if any(norm(o) in f for f in forms):
                counts[pred]["TP"]+=1
            else:
                counts[pred]["FP"]+=1
                fps.append((subj,pred,o))

    for title,rows in wd.items():
        for pred in predicates:
            objsnorm=set()
            for (subj,p),objs in extracted.items():
                if p==pred and norm(subj)==norm(title):
                    objsnorm|={norm(o) for o in objs}
            for v in [x for x in rows if x["predicate"]==pred]:
                forms={norm(v["value_label"])}|{norm(a) for a in v["aliases"].split("|") if a}
                if not (forms&objsnorm):
                    counts[pred]["FN"]+=1
                    fns.append((title,pred,v["value_label"]))

    fps.sort(key=lambda t: tuple(x.lower() for x in t))
    fns.sort(key=lambda t: tuple(x.lower() for x in t))


    path=Path("eval/metrics.csv")
    old=[]
    if path.exists():
        old=[r for r in csv.DictReader(open(path,encoding="utf-8")) if r["run"]!=args.run]
    new=[]
    tot={"TP": 0,"FP": 0,"FN": 0}
    for p in predicates+["ALL"]:
        c=counts[p] if p!="ALL" else tot
        if p!="ALL":
            for k in tot:
                tot[k]+=c[k]
        prec=c["TP"]/(c["TP"]+c["FP"]) if c["TP"]+c["FP"] else 0.0
        rec=c["TP"]/(c["TP"]+c["FN"]) if c["TP"]+c["FN"] else 0.0
        new.append({"run": args.run,"predicate": p,"TP": c["TP"],"FP": c["FP"],"FN": c["FN"],
                    "precision": f"{prec:.3f}","recall": f"{rec:.3f}"})
    with open(path,"w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=["run","predicate","TP","FP","FN","precision","recall"])
        w.writeheader()
        w.writerows(old+new)
    print(f"--- run '{args.run}' ---")
    for r in new:
        print(f"{r['predicate']:16s} TP={r['TP']:3d} FP={r['FP']:3d} FN={r['FN']:3d} "
              f"P={r['precision']} R={r['recall']}")


    for name,entries in (("false_positives",fps),("false_negatives",fns)):
        with open(f"eval/{name}_{args.run}.csv","w",newline="",encoding="utf-8") as f:
            w=csv.writer(f)
            w.writerow(["position","subject","predicate","object"])
            for i,r in enumerate(entries,start=1):
                w.writerow([i,*r])


    lines=[f"# Error analysis (run: {args.run})","",
             f"False-positive list length: {len(fps)}.  False-negative list length: {len(fns)}.",
             "Lists are sorted alphabetically (case-insensitive) by (subject, predicate, object);",
             "positions are 1-based, with wrap-around (position mod length) for short lists.","",
             "Error codes: E1 wrong span | E2 pronoun | E3 alias split | E4 direction/role | "
             "E5 negation/time | E6 source gap (my triple is right, Wikidata lacks it) | E7 other",""]
    for label,items,positions in (("False positive",fps,fppositions),("False negative",fns,fnpositions)):
        for pos in positions:
            if not items:
                lines+=[f"## {label} at position {pos}","(list is empty -- nothing to analyse)",""]
                continue
            real=wrap(pos,len(items))
            subj,pred,obj=items[real-1]
            lines+=[f"## {label} at position {pos}"+(f" (wrapped to {real})" if real!=pos else ""),
                      f"- Triple: ({subj}, {pred}, {obj})"]
            if label=="False positive":
                lines.append(f"- Sentence: {sentenceof.get((subj,pred,obj),'?')}")
            else:
                lines.append("- Sentence: (find the sentence in data/raw that mentions this, or write 'not in the text')")
            lines+=["- Error code: ","- Why it happened: ","- What would fix it: ",""]
    Path(f"eval/error_analysis_draft_{args.run}.md").write_text("\n".join(lines),encoding="utf-8")
    print(f"wrote eval/error_analysis_draft_{args.run}.md")


if __name__=="__main__":
    main()
