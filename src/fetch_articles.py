from pathlib import Path

import requests

contact="p230044@pwr.nu.edu.pk"
titles=["Richard Feynman","Sheldon Glashow","James Chadwick",
          "Werner Heisenberg","Erwin Schrödinger"]
api="https://en.wikipedia.org/w/api.php"


def getplaintext(title):
    reply=requests.get(
        api,
        params={"action": "query","format": "json","prop": "extracts",
                "explaintext": 1,"redirects": 1,"titles": title},
        headers={"User-Agent": f"KRR-coursework/1.0 ({contact})"},
        timeout=30,
    )
    reply.raise_for_status()
    pages=reply.json()["query"]["pages"]
    page=next(iter(pages.values()))
    return page.get("extract","")


def main():
    out=Path("data/raw")
    out.mkdir(parents=True,exist_ok=True)
    for title in titles:
        text=getplaintext(title)
        file=out/(title.replace(" ","_")+".txt")
        file.write_text(text,encoding="utf-8")
        print(f"{title:20s} -> {file}  ({len(text.split())} words)")


main()
