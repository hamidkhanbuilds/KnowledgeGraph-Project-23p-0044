import argparse
import csv
import re
import unicodedata
from collections import Counter
from pathlib import Path

import spacy

nlp=spacy.load("en_core_web_sm")


titles={"dr","prof","professor","sir","mr","mrs","ms","lord","mx"}
male={"he","him","his","himself"}
female={"she","her","hers","herself"}
negwords={"not","n't","never","no","neither","nor","nobody","hardly"}
hedgewords={"rumour","rumor","rumoured","rumored","allegedly",
               "falsely","wrongly","mistakenly","myth"}

orgwords={"university","college","institute","school","academy",
             "laboratory","laboratories","observatory","centre","center",
             "company","corporation","foundation","project","polytechnic",
             "faculty","department","society","lab","labs","hospital"}
awardwords={"prize","medal","award","fellowship","scholarship",
               "honour","honor","lectureship","citation"}
rolewords={"professor","lecturer","researcher","fellow","director",
              "dean","instructor","chair","head","staff","assistant"}
degreewords={"degree","phd","doctorate","bachelor","master","diploma",
                "licentiate","habilitation"}
advisorwords={"advisor","adviser","supervisor"}
doctoralwords={"doctoral","doctorate","phd","thesis","dissertation",
                  "doctor"}
badplaceents={"DATE","TIME","CARDINAL","ORDINAL","PERSON","MONEY",
                  "PERCENT","QUANTITY"}
stopheadings={"references","further reading","external links","notes",
                 "bibliography","see also","sources","footnotes"}


def fold(text):
    text=unicodedata.normalize("NFKD",text)
    return "".join(c for c in text if not unicodedata.combining(c)).lower()


def cleanlines(raw):
    lines=[]
    for ln in raw.splitlines():
        ln=ln.strip()
        if not ln:
            continue
        if ln.startswith("=="):
            if ln.strip("= ").lower() in stopheadings:
                break
            continue
        for _ in range(2):
            ln=re.sub(r"\([^()]*\)","",ln)
        ln=re.sub(r"\b(Dr|Prof|Mr|Mrs|Ms)\.",r"\1",ln)
        ln=re.sub(r"\s+([,.;:])",r"\1",ln)
        ln=re.sub(r"\s{2,}"," ",ln).strip()
        if ln:
            lines.append(ln)
    return lines


def striptitles(name):
    words=name.replace("'s","").split()
    while words and words[0].lower().rstrip(".") in titles:
        words.pop(0)
    return " ".join(words)


def sameperson(a,b):
    ta,tb=fold(a).split(),fold(b).split()
    if not ta or not tb or ta[-1]!=tb[-1]:
        return False
    if len(ta)==1 or len(tb)==1:
        return True
    fa,fb=ta[0].rstrip("."),tb[0].rstrip(".")
    if len(fa)==1 or len(fb)==1:
        return fa[0]==fb[0]
    return fa==fb


def capitalised(tok):
    return tok.text[:1].isupper()


def namespan(tok,preps=("of","for"),allowin=False):
    keep,stack={tok},[tok]
    okpreps=set(preps)|({"in"} if allowin else set())
    while stack:
        cur=stack.pop()
        for ch in cur.children:
            if ch.dep_ in ("compound","nmod","flat","amod") and capitalised(ch):
                keep.add(ch)
                stack.append(ch)
            elif ch.dep_=="prep" and ch.lower_ in okpreps:
                for p in ch.children:
                    if (p.dep_=="pobj" and capitalised(p)
                            and p.ent_type_ not in badplaceents-{"PERSON"}):
                        keep.update([ch,p])
                        stack.append(p)
    toks=sorted(keep,key=lambda t: t.i)
    return "".join(t.text_with_ws for t in toks).strip()


def owntokens(verb):
    out,stack=[],[verb]
    while stack:
        cur=stack.pop()
        out.append(cur)
        for ch in cur.children:
            if ch.pos_ in ("VERB","AUX") and ch.dep_ in ("conj","advcl","relcl","ccomp","xcomp","acl"):
                continue
            stack.append(ch)
    return out


def withconjuncts(tok):
    got,stack=[],[tok]
    while stack:
        cur=stack.pop()
        got.append(cur)
        stack.extend(c for c in cur.children if c.dep_=="conj")
    return sorted(got,key=lambda t: t.i)


def subjecttoken(verb):
    node=verb
    for _ in range(5):
        for ch in node.children:
            if ch.dep_ in ("nsubj","nsubjpass"):
                return ch
        if node.dep_ in ("conj","xcomp","advcl") and node.head is not node:
            node=node.head
        elif node.dep_ in ("acl","relcl") and node.head.pos_ in ("PROPN","PRON"):
            return node.head
        else:
            break
    return None


def isnegated(verb):
    for t in owntokens(verb):
        if t.dep_=="neg" or t.lower_ in negwords:
            return True
    node=verb
    while node.dep_=="xcomp" and node.head is not node:
        node=node.head
        if any(c.dep_=="neg" or c.lower_ in negwords for c in node.children):
            return True
    return False


def orglike(tok,spantext):
    return (tok.ent_type_ in ("ORG","FAC")
            or any(w in orgwords for w in fold(spantext).split()))


class DocState:
    def __init__(self,mainname,maingender):
        self.main=mainname
        self.maingender=maingender
        self.people=[mainname]
        self.recent=[mainname]
        self.mergelog=Counter()

    def canon(self,surface,count=False):
        core=striptitles(surface.strip())
        if not core:
            return None
        result=None
        for full in self.people:
            if fold(core)==fold(full):
                result=full
                break
        if result is None:
            for full in self.people:
                if sameperson(core,full):
                    result=full
                    break
        if result is None:
            result=core
            if len(core.split())>=2:
                self.people.append(core)
        if count and fold(result)!=fold(core):
            self.mergelog[(surface.strip(),result)]+=1
        return result

    def touch(self,name):
        if name in self.recent:
            self.recent.remove(name)
        self.recent.append(name)

    def pronoun(self,word):
        if word in male:
            g="m"
        elif word in female:
            g="f"
        else:
            return None
        if self.maingender in (None,g):
            return self.main
        for name in reversed(self.recent):
            if name!=self.main:
                return name
        return None


def personfromtoken(tok,st):
    if tok is None:
        return None
    if tok.pos_=="PRON":
        return st.pronoun(tok.lower_)
    if tok.pos_=="PROPN" and tok.ent_type_!="DATE":



        surface=namespan(tok,preps=())
        if any(w in orgwords|awardwords for w in fold(surface).split()):
            return None
        name=st.canon(surface)


        if name and (len(name.split())>=2 or tok.ent_type_=="PERSON"):
            return name
        return None
    return None


def lookslikeperson(text):
    words=fold(text).split()
    return bool(words) and not any(w in orgwords|awardwords for w in words)


def rulebornin(tok,st):
    if tok.lemma_!="bear":
        return
    for t in owntokens(tok):
        if (t.dep_=="pobj" and t.head.lower_ in ("in","at") and t.pos_=="PROPN"
                and t.ent_type_ not in badplaceents):
            subj=personfromtoken(subjecttoken(tok),st)
            if subj:
                yield "bornIn",subj,namespan(t,preps=()),"born-in/dep"
            return


def namedtargets(verb,preps,strict):
    for t in owntokens(verb):
        if t.dep_=="pobj" and t.head.lower_ in preps and t.pos_=="PROPN":
            for tt in withconjuncts(t):
                span=namespan(tt)
                if tt.ent_type_=="PERSON" and not orglike(tt,span):
                    continue
                if strict and not orglike(tt,span):
                    continue
                yield span


def ruleeducatedat(tok,st):
    lem=tok.lemma_
    if lem in ("study","graduate","enrol","enroll","matriculate","train"):
        for span in namedtargets(tok,{"at","from"},strict=False):
            subj=personfromtoken(subjecttoken(tok),st)
            if subj:
                yield "educatedAt",subj,span,"studied-at/dep"
    elif lem=="attend":
        for d in tok.children:
            if d.dep_ in ("dobj","obj") and d.pos_=="PROPN":
                for dd in withconjuncts(d):
                    span=namespan(dd)
                    if orglike(dd,span) or dd.ent_type_ in ("GPE","ORG","FAC"):
                        subj=personfromtoken(subjecttoken(tok),st)
                        if subj:
                            yield "educatedAt",subj,span,"attended/dep"
    elif lem in ("receive","earn","obtain","complete","gain","get","take"):
        degree=[t for t in owntokens(tok)
                  if t.dep_ in ("dobj","obj") and t.lemma_.lower() in degreewords]
        if degree:
            for span in namedtargets(tok,{"from","at"},strict=True):
                subj=personfromtoken(subjecttoken(tok),st)
                if subj:
                    yield "educatedAt",subj,span,"degree-from/dep"


def ruleaward(tok,st):
    if tok.lemma_ not in ("receive","win","award","share","earn","accept"):
        return
    objs=[]
    for d in tok.children:
        if d.dep_ in ("dobj","obj","dative","attr"):
            objs.append(d)
            if d.lemma_ in ("share","half","portion"):
                for p in d.children:
                    if p.dep_=="prep" and p.lower_=="of":
                        objs.extend(x for x in p.children if x.dep_=="pobj")
    for c in tok.children:
        if c.dep_=="conj" and c.pos_ in ("PROPN","NOUN"):
            objs.append(c)
    awards=[]
    for o in objs:
        for oo in withconjuncts(o):
            if oo.lemma_.lower() in awardwords:
                awards.append(oo)
    if not awards:
        return

    subjtok=subjecttoken(tok)
    if tok.lemma_=="award":
        for d in tok.children:
            if d.dep_=="dative" and d.pos_ in ("PRON","PROPN"):
                subjtok=d
    subj=personfromtoken(subjtok,st)
    if not subj:
        return
    for a in awards:
        yield "receivedAward",subj,namespan(a,preps=("of","for"),allowin=True),"award/dep"


def ruleworksat(tok,st):
    lem=tok.lemma_
    looseverbs={"work": {"at","for"},"teach": {"at"},
                   "lecture": {"at"},"serve": {"at"}}
    strictverbs={"move": {"to"},"return": {"to"},"relocate": {"to"},
                    "transfer": {"to"},"appoint": {"at","to"},"hire": {"by"},
                    "employ": {"by"},"recruit": {"by"}}
    if lem=="join":
        for d in tok.children:
            if d.dep_ in ("dobj","obj") and d.pos_=="PROPN":
                for dd in withconjuncts(d):
                    span=namespan(dd)
                    if dd.ent_type_=="PERSON" and not orglike(dd,span):
                        continue
                    subj=personfromtoken(subjecttoken(tok),st)
                    if subj:
                        yield "worksAt",subj,span,"joined/dep"
    elif lem in looseverbs:
        for span in namedtargets(tok,looseverbs[lem],strict=False):
            subj=personfromtoken(subjecttoken(tok),st)
            if subj:
                yield "worksAt",subj,span,"worked-at/dep"
    elif lem in strictverbs:
        for span in namedtargets(tok,strictverbs[lem],strict=True):
            subj=personfromtoken(subjecttoken(tok),st)
            if subj:
                yield "worksAt",subj,span,"moved-to/dep"
    if tok.lemma_.lower() in rolewords and tok.dep_ in ("attr","oprd") \
            and tok.head.lemma_ in ("be","become","remain"):
        stack,seen=[tok],[]
        while stack:
            cur=stack.pop()
            seen.append(cur)
            stack.extend(c for c in cur.children if c.pos_ not in ("VERB","AUX"))
        for t in seen:
            if t.dep_=="pobj" and t.head.lower_ in ("at","of","for") and t.pos_=="PROPN":


                if t.head.lower_!="at" and t.head.head.lemma_.lower() not in rolewords:
                    continue
                span=namespan(t)
                if orglike(t,span):
                    subj=personfromtoken(subjecttoken(tok.head),st)
                    if subj:
                        yield "worksAt",subj,span,"role-at/dep"


def possowner(noun,st):
    for c in noun.children:
        if c.dep_=="poss":
            return personfromtoken(c,st)
    return None


def ruleadvisor(tok,st):

    if tok.lemma_.lower() in advisorwords:
        mods={c.lower_ for c in tok.children}
        if mods&doctoralwords:
            holder=possowner(tok,st)
            other=None
            head=tok.head
            if head.lemma_=="be":
                if tok.dep_ in ("nsubj","nsubjpass"):
                    other=next((c for c in head.children if c.dep_ in ("attr","acomp")),None)
                elif tok.dep_=="attr":
                    other=next((c for c in head.children if c.dep_=="nsubj"),None)
            adv=personfromtoken(other,st) if other is not None else None
            if holder and adv and holder!=adv:
                yield "doctoralAdvisor",holder,adv,"advisor-noun/dep"
        return

    if tok.pos_=="VERB" and tok.lemma_ in ("study","complete","receive","earn","obtain",
                                              "write","work","do","pursue","finish","gain"):
        words={t.lower_ for t in owntokens(tok)}
        if words&doctoralwords:
            for t in owntokens(tok):
                if t.dep_=="prep" and t.lower_=="under":
                    for p in t.children:
                        if p.dep_!="pobj":
                            continue
                        cand=p
                        if p.pos_!="PROPN":
                            cand=next((x for pp in p.children if pp.dep_=="prep"
                                         and pp.lower_=="of" for x in pp.children
                                         if x.dep_=="pobj"),None)
                        adv=personfromtoken(cand,st) if cand is not None else None
                        stu=personfromtoken(subjecttoken(tok),st)
                        if adv and stu and adv!=stu:
                            yield "doctoralAdvisor",stu,adv,"under/dep"

    if tok.lemma_ in ("supervise","advise","mentor"):
        agent=next((p for c in tok.children if c.dep_=="agent"
                      for p in c.children if p.dep_=="pobj"),None)
        passive=next((c for c in tok.children if c.dep_=="nsubjpass"),None)
        activesubj=next((c for c in tok.children if c.dep_=="nsubj"),None)
        dobj=next((c for c in tok.children if c.dep_ in ("dobj","obj")),None)
        advtok,studenttok=None,None
        if passive is not None and agent is not None:
            advtok,studenttok=agent,passive
        elif activesubj is not None and dobj is not None:
            advtok,studenttok=activesubj,dobj
        if advtok is not None and studenttok is not None:
            if studenttok.lemma_ in ("thesis","dissertation","research","work","studies"):
                stu=possowner(studenttok,st)
            else:
                stu=personfromtoken(studenttok,st)
            adv=personfromtoken(advtok,st)
            if adv and stu and adv!=stu:
                yield "doctoralAdvisor",stu,adv,"supervise/dep"


rules=[rulebornin,ruleeducatedat,ruleaward,ruleworksat,ruleadvisor]


def guessmainname(stem,text):
    title=stem.replace("_"," ")
    if fold(title.split()[-1]) in fold(text):
        return title
    return None


def firstgender(docsents):
    for s in docsents:
        for t in s:
            if t.lower_ in male:
                return "m"
            if t.lower_ in female:
                return "f"
    return None


def processdocument(path):
    raw=path.read_text(encoding="utf-8",errors="ignore")
    lines=cleanlines(raw)
    fulltext="\n".join(lines)
    docs=list(nlp.pipe(lines,batch_size=32))
    sents=[s for d in docs for s in d.sents]

    main=guessmainname(path.stem,fulltext)
    if main is None:
        for s in sents:
            ents=[e for e in s.ents if e.label_=="PERSON" and len(e.text.split())>=2
                    and lookslikeperson(e.text)]
            if ents:
                main=striptitles(ents[0].text)
                break
    if main is None:
        main=path.stem
    st=DocState(main,firstgender(sents))

    rows,skipped=[],[]
    seen=set()
    for n,sent in enumerate(sents,start=1):
        text=sent.text.strip()
        hedged=any(t.lower_ in hedgewords for t in sent)
        for tok in sent:
            if tok.pos_ not in ("VERB","AUX","NOUN"):
                continue
            for rule in rules:
                for pred,subj,obj,why in rule(tok,st):
                    key=(subj,pred,obj,n)
                    if key in seen:
                        continue
                    seen.add(key)
                    verb=tok if tok.pos_ in ("VERB","AUX") else tok.head
                    if isnegated(verb) or isnegated(tok):
                        skipped.append((path.name,text,pred,subj,obj,"negated"))
                    elif hedged:
                        skipped.append((path.name,text,pred,subj,obj,"hedged"))
                    else:
                        rows.append((subj,pred,obj,path.name,text,why,n))

        mentioned=set()
        for e in sent.ents:
            if e.label_=="PERSON" and lookslikeperson(e.text):
                mentioned.add(e.text)
        for t in sent:
            if t.dep_ in ("nsubj","nsubjpass") and t.pos_=="PROPN" and t.ent_type_ in ("","PERSON"):
                span=namespan(t,preps=())
                if lookslikeperson(span):
                    mentioned.add(span)
        for surface in sorted(mentioned,key=lambda x: sent.text.find(x)):
            name=st.canon(surface,count=True)
            if name and (len(name.split())>=2 or name in st.people):
                st.touch(name)
    return rows,skipped,st


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--raw",default="data/raw")
    ap.add_argument("--out",default="out")
    args=ap.parse_args()

    outdir=Path(args.out)
    outdir.mkdir(exist_ok=True)
    allrows,allskipped,mergelines=[],[],[]
    totalmerges=0
    for path in sorted(Path(args.raw).glob("*.txt")):
        rows,skipped,st=processdocument(path)
        allrows+=rows
        allskipped+=skipped
        nmerge=sum(st.mergelog.values())
        totalmerges+=nmerge
        mergelines.append(f"{path.name}: main subject = {st.main!r}, merges = {nmerge}")
        for (surface,canon),k in st.mergelog.most_common():
            mergelines.append(f"    {surface!r} -> {canon!r}  x{k}")
        print(f"{path.name:35s} triples={len(rows):4d}  skipped(negated/hedged)={len(skipped)}")

    with open(outdir/"triples.csv","w",newline="",encoding="utf-8") as f:
        w=csv.writer(f)
        w.writerow(["subject","predicate","object","source_doc","sentence"])
        for r in allrows:
            w.writerow(r[:5])
    with open(outdir/"triples_debug.csv","w",newline="",encoding="utf-8") as f:
        w=csv.writer(f)
        w.writerow(["subject","predicate","object","source_doc","sentence","rule","sentence_no"])
        w.writerows(allrows)
    with open(outdir/"skipped_negated_or_hedged.csv","w",newline="",encoding="utf-8") as f:
        w=csv.writer(f)
        w.writerow(["source_doc","sentence","predicate","subject","object","reason"])
        w.writerows(allskipped)
    (outdir/"merge_report.txt").write_text(
        f"Total alias merges: {totalmerges}\n"+"\n".join(mergelines)+"\n",encoding="utf-8")

    perpred=Counter(r[1] for r in allrows)
    print("\nTriples per predicate:",dict(perpred))
    print("Total alias merges:",totalmerges,"(details in out/merge_report.txt)")


if __name__=="__main__":
    main()
