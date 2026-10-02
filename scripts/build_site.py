#!/usr/bin/env python3
from pathlib import Path
import html, json, re
ROOT=Path(__file__).resolve().parents[1]
SITE="https://aradmanamnaoon.github.io"
PERSON_ID=f"{SITE}/#person"

def replace_between(text,start,end,replacement):
    pattern=re.escape(start)+r".*?"+re.escape(end)
    text,n=re.subn(pattern,start+"\n"+replacement.rstrip()+"\n"+end,text,count=1,flags=re.S)
    if n!=1: raise RuntimeError(f"Missing build markers: {start}")
    return text

def load_articles():
    p=ROOT/"blog"/"articles.json"
    data=json.loads(p.read_text(encoding="utf-8"))
    required={"title","url","date","dateDisplay","readTime","description","tags"}
    for i,a in enumerate(data,1):
        missing=required-set(a)
        if missing: raise ValueError(f"Article {i} missing: {sorted(missing)}")
        if not a["url"].startswith("/blog/"): raise ValueError(f"Bad article URL: {a['url']}")
    return sorted(data,key=lambda a:a["date"],reverse=True)

def home_cards(items):
    cards=[]
    for a in items[:3]:
        tags="\n".join(f'                <span class="writing-post-tag">{html.escape(t)}</span>' for t in a.get("tags",[]))
        cards.append(f'''        <a class="writing-post-card" href="{html.escape(a["url"])}" aria-label="Read {html.escape(a["title"],quote=True)}">
          <div><div class="writing-post-meta">{html.escape(a["dateDisplay"])} · {html.escape(a["readTime"])}</div>
            <h3 class="writing-post-title">{html.escape(a["title"])}</h3>
            <p class="writing-post-description">{html.escape(a["description"])}</p>
            <div class="writing-post-tags" aria-label="Article topics">\n{tags}\n            </div>
          </div><span class="writing-post-arrow" aria-hidden="true">→</span>
        </a>''')
    return "\n\n".join(cards)

def blog_cards(items):
    cards=[]
    for a in items:
        tags="\n".join(f'                  <span class="blog-post-tag">{html.escape(t)}</span>' for t in a.get("tags",[]))
        cards.append(f'''          <article><a class="blog-post" href="{html.escape(a["url"])}" aria-label="Read {html.escape(a["title"],quote=True)}">
              <div class="blog-post-meta"><time datetime="{a["date"]}">{html.escape(a["dateDisplay"])}</time><br />{html.escape(a["readTime"])}</div>
              <div><h3 class="blog-post-title">{html.escape(a["title"])}</h3><p class="blog-post-description">{html.escape(a["description"])}</p>
                <div class="blog-post-tags" aria-label="Article topics">\n{tags}\n                </div></div>
              <span class="blog-post-arrow" aria-hidden="true">→</span></a></article>''')
    return "\n\n".join(cards)

def schema(items):
    posts=[{"@type":"BlogPosting","@id":f"{SITE}{a['url']}#article","url":f"{SITE}{a['url']}","headline":a["title"],"description":a["description"],"datePublished":a["date"],"dateModified":a.get("modified",a["date"]),"inLanguage":"en","keywords":a.get("tags",[]),"author":{"@id":PERSON_ID},"isPartOf":{"@id":f"{SITE}/blog/#blog"},"mainEntityOfPage":f"{SITE}{a['url']}"} for a in items]
    graph={"@context":"https://schema.org","@graph":[{"@type":"Blog","@id":f"{SITE}/blog/#blog","url":f"{SITE}/blog/","name":"ARADMANAMNAOON — AI Engineering Blog","description":"First-hand technical notes, experiments, debugging stories, and project breakdowns from AI and machine-learning work.","inLanguage":"en","author":{"@id":PERSON_ID},"publisher":{"@id":PERSON_ID},"blogPost":posts},{"@type":"Person","@id":PERSON_ID,"name":"Seyyed Arad Hosseini Moghaddam","alternateName":"ARADMANAMNAOON","url":f"{SITE}/","sameAs":["https://github.com/aradmanamnaoon","https://huggingface.co/aradmanamnaoon","https://www.linkedin.com/in/seyyed-arad-hosseini-moghaddam"]},{"@type":"BreadcrumbList","@id":f"{SITE}/blog/#breadcrumb","itemListElement":[{"@type":"ListItem","position":1,"name":"Home","item":f"{SITE}/"},{"@type":"ListItem","position":2,"name":"Blog","item":f"{SITE}/blog/"}]}]}
    return '  <script type="application/ld+json">\n'+json.dumps(graph,ensure_ascii=False,indent=2)+'\n  </script>'

def sitemap(items):
    latest=max(a.get("modified",a["date"]) for a in items)
    rows=[(f"{SITE}/",latest),(f"{SITE}/projects/","2026-10-02"),(f"{SITE}/blog/",latest)]+[(f"{SITE}{a['url']}",a.get("modified",a["date"])) for a in items]
    lines=['<?xml version="1.0" encoding="UTF-8"?>','<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u,d in rows: lines += ["  <url>",f"    <loc>{html.escape(u)}</loc>",f"    <lastmod>{d}</lastmod>","  </url>"]
    lines.append("</urlset>")
    (ROOT/"sitemap.xml").write_text("\n".join(lines)+"\n",encoding="utf-8")

def main():
    items=load_articles(); latest=max(a.get("modified",a["date"]) for a in items)
    p=ROOT/"index.html"; t=p.read_text(encoding="utf-8"); t=replace_between(t,"<!-- AUTO:HOME_ARTICLES:START -->","<!-- AUTO:HOME_ARTICLES:END -->",home_cards(items)); t=re.sub(r'("dateModified"\s*:\s*")[0-9]{4}-[0-9]{2}-[0-9]{2}(")',rf'\g<1>{latest}\2',t,count=1); p.write_text(t,encoding="utf-8")
    p=ROOT/"blog"/"index.html"; t=p.read_text(encoding="utf-8"); t=replace_between(t,"<!-- AUTO:BLOG_ARTICLES:START -->","<!-- AUTO:BLOG_ARTICLES:END -->",blog_cards(items)); t=replace_between(t,"<!-- AUTO:BLOG_SCHEMA:START -->","<!-- AUTO:BLOG_SCHEMA:END -->",schema(items)); p.write_text(t,encoding="utf-8")
    sitemap(items)
    print(f"Built {len(items)} article(s): index.html, blog/index.html, sitemap.xml")
if __name__=="__main__": main()
