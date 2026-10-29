"""BlogoSvod: minimal RSS/Atom collector; Python standard library only."""
import csv, datetime as dt, email.utils, html, json, re, urllib.request, urllib.parse
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

ROOT=Path(__file__).parent
UA={'User-Agent':'BlogoSvodFeedReader/0.1 (+https://blogosvod.blogspot.com/)'}
ATOM='{http://www.w3.org/2005/Atom}'
DC='{http://purl.org/dc/elements/1.1/}'
MEDIA='{http://search.yahoo.com/mrss/}'

class Snippet(HTMLParser):
    def __init__(self): super().__init__(); self.text=[]; self.img=None; self.skip=0
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if tag in ('script','style'): self.skip+=1
        if tag=='img' and not self.img: self.img=a.get('src')
    def handle_endtag(self,tag):
        if tag in ('script','style'): self.skip=max(0,self.skip-1)
    def handle_data(self,data):
        if not self.skip: self.text.append(data)

def extract(markup):
    p=Snippet(); p.feed(markup or '')
    text=' '.join(' '.join(p.text).split())
    return text[:280]+('…' if len(text)>280 else ''),p.img

def dateparse(value):
    if not value:return None
    try:return dt.datetime.fromisoformat(value.replace('Z','+00:00')).astimezone(dt.timezone.utc)
    except ValueError:
        try:return email.utils.parsedate_to_datetime(value).astimezone(dt.timezone.utc)
        except (TypeError,ValueError):return None

def get_text(el,tag):
    n=el.find(tag); return ''.join(n.itertext()).strip() if n is not None else ''

def get_feed(blog_url):
    parsed=urllib.parse.urlsplit(blog_url)
    base=f'{parsed.scheme}://{parsed.netloc}'
    candidates=[base+'/feeds/posts/default?max-results=2',base+'/feed/',base+'/rss/',blog_url]
    for url in candidates:
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=12) as response:
                data=response.read(2_000_000)
            root=ET.fromstring(data)
            if root.tag==ATOM+'feed':
                entries=[]
                for e in root.findall(ATOM+'entry'):
                    link=next((x.get('href') for x in e.findall(ATOM+'link') if x.get('rel')=='alternate' and x.get('type','text/html')=='text/html'),None)
                    raw=get_text(e,ATOM+'summary') or get_text(e,ATOM+'content')
                    snippet,img=extract(raw)
                    stamp=dateparse(get_text(e,ATOM+'published') or get_text(e,ATOM+'updated'))
                    if link and stamp:entries.append(dict(title=get_text(e,ATOM+'title'),url=link,stamp=stamp,snippet=snippet,image=img))
                if entries:return max(entries,key=lambda x:x['stamp'])
            if root.tag.lower() in ('rss','{http://www.w3.org/1999/02/22-rdf-syntax-ns#}rdf'):
                entries=[]
                for e in root.findall('.//item'):
                    link=get_text(e,'link');stamp=dateparse(get_text(e,'pubDate') or get_text(e,DC+'date'))
                    snippet,img=extract(get_text(e,'description') or get_text(e,'{http://purl.org/rss/1.0/modules/content/}encoded'))
                    media=e.find(MEDIA+'thumbnail')
                    if media is not None:img=media.get('url') or img
                    if link and stamp:entries.append(dict(title=get_text(e,'title'),url=link,stamp=stamp,snippet=snippet,image=img))
                if entries:return max(entries,key=lambda x:x['stamp'])
        except Exception:continue
    return None

def render(items,failed):
    rows=[]
    for x in sorted(items,key=lambda p:p['stamp'],reverse=True):
        safe=lambda s:html.escape(s or '',quote=True)
        image=''
        if x['image'] and urllib.parse.urlsplit(x['image']).scheme in ('https','http'):
            image=f'<img loading="lazy" class="thumb" src="{safe(x["image"])}" alt="">'
        rows.append(f'<article><a class="blog" href="{safe(x["blog_url"])}" target="_blank" rel="noopener noreferrer">{safe(x["blog"])}</a><h2><a href="{safe(x["url"])}" target="_blank" rel="noopener noreferrer">{safe(x["title"])}</a></h2><time>{x["stamp"].astimezone(dt.timezone(dt.timedelta(hours=1))).strftime("%d.%m.%Y %H:%M")} (SEČ, orientačně)</time><p>{safe(x["snippet"])}</p>{image}</article>')
    now=dt.datetime.now(dt.timezone.utc).strftime('%d.%m.%Y %H:%M UTC')
    return '''<!doctype html><html lang="cs"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Co nového na blozích – BlogoSvod</title><style>body{font:16px/1.55 Arial,sans-serif;background:white;color:#242424;max-width:760px;margin:0 auto;padding:24px}h1{font-size:27px;margin-bottom:0}h2{font-size:19px;margin:4px 0}a{color:#b95a12}a.blog{font-size:15px;font-weight:bold}article{border-bottom:1px solid #ddd;padding:20px 0}time,small{color:#666;font-size:13px}p{margin:8px 0}.thumb{display:block;max-width:220px;max-height:150px;object-fit:contain;margin-top:10px} </style><h1>Co nového na blozích</h1><small>Poslední kontrola: '''+now+''' · Funkční kanály: '''+str(len(items))+''' · Nepodařilo se načíst: '''+str(len(failed))+'''</small>'''+''.join(rows)+'''</html>'''

def main():
    items=[];failed=[]
    with (ROOT/'blogs.csv').open(encoding='utf-8-sig',newline='') as f:
        for b in csv.DictReader(f):
            try:
                post=get_feed(b['url'])
                if post:items.append(dict(post,blog=b['name'],blog_url=b['url']))
                else:failed.append(b)
            except Exception:failed.append(b)
    (ROOT/'index.html').write_text(render(items,failed),encoding='utf-8')
    (ROOT/'status.json').write_text(json.dumps({'successful':len(items),'failed':failed},ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'Loaded {len(items)} blogs, failed {len(failed)}')

if __name__=='__main__':main()
