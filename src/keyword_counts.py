import re
from pathlib import Path

ideas={
    "bornIn":          r"\bborn\b",
    "educatedAt":      r"\b(studied|attended|graduated|enrolled|educated)\b",
    "receivedAward":   r"\b(prize|medal|award(ed)?)\b",
    "worksAt":         r"\b(joined|worked|professor|taught|lecturer|moved to)\b",
    "doctoralAdvisor": r"\b(advisor|adviser|supervis\w+|doctoral|thesis|dissertation|phd)\b",
}

print(f"{'file':32s}"+"".join(f"{k:>17s}" for k in ideas))
for path in sorted(Path("data/raw").glob("*.txt")):
    text=path.read_text(encoding="utf-8",errors="ignore")
    sentences=re.split(r"(?<=[.!?])\s+",text)
    counts=[sum(1 for s in sentences if re.search(rx,s,re.I)) for rx in ideas.values()]
    print(f"{path.name:32s}"+"".join(f"{c:17d}" for c in counts))
