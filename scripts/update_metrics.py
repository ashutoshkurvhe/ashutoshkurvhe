"""Fetch public GitHub data and render local Obsidian cards. Standard library only.

No private repository endpoints or account-scoped personal token are required.
Calendar data comes from GitHub's publicly visible contribution HTML; its markup
is not a versioned API. Parsing/HTTP failures abort before replacing any cards.
"""
import concurrent.futures
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
import time
from html.parser import HTMLParser
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen
from theme import *

ROOT = Path(__file__).resolve().parents[1]
USER = 'ashutoshkurvhe'
API = 'https://api.github.com'
TOKEN = os.environ.get('GH_TOKEN', '')
CACHE = os.environ.get('PROFILE_FETCH_CACHE')  # Optional local QA read-through cache.

def fetch(url, as_json=True):
    cached = Path(CACHE) / hashlib.sha256(url.encode()).hexdigest() if CACHE else None
    if cached and cached.exists():
        content = cached.read_bytes()
    else:
        headers = {'User-Agent': 'Obsidian-Profile/1.0', 'Accept-Language': 'en-US,en;q=0.9'}
        if url.startswith(API + '/'):
            headers.update({'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'})
            if TOKEN: headers['Authorization'] = f'Bearer {TOKEN}'
        for attempt in range(2):
            try:
                with urlopen(Request(url, headers=headers), timeout=30) as response:
                    content = response.read()
                break
            except Exception:
                if attempt: raise
                time.sleep(1)
        if cached:
            cached.parent.mkdir(parents=True, exist_ok=True)
            cached.write_bytes(content)
    return json.loads(content) if as_json else content.decode('utf-8')

class CalendarParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.cells, self.tips, self.active, self.parts = {}, {}, None, []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get('data-date') and a.get('data-level') is not None:
            date = dt.date.fromisoformat(a['data-date'])
            self.cells[a.get('id', date.isoformat())] = {
                'date': date.isoformat(), 'level': int(a['data-level']),
                'count': int(a['data-count']) if 'data-count' in a else None,
            }
        if tag == 'tool-tip' and a.get('for'):
            self.active, self.parts = a['for'], []

    def handle_data(self, data):
        if self.active: self.parts.append(data)

    def handle_endtag(self, tag):
        if tag == 'tool-tip' and self.active:
            self.tips[self.active] = ''.join(self.parts)
            self.active = None

    def days(self):
        if not self.cells: raise ValueError('No contribution cells found; GitHub calendar markup may have changed.')
        result = {}
        for key, value in self.cells.items():
            value = value.copy()
            if value['count'] is None:
                match = re.match(r'\s*(No|[\d,]+)\s+contributions?\b', self.tips.get(key, ''), re.I)
                if not match: raise ValueError(f'Missing contribution count for {value["date"]}; refusing to invent data.')
                value['count'] = 0 if match[1].lower() == 'no' else int(match[1].replace(',', ''))
            if not 0 <= value['level'] <= 4 or value['count'] < 0:
                raise ValueError('Invalid contribution value')
            result[value['date']] = value
        return sorted(result.values(), key=lambda d: d['date'])

def parse_calendar(html):
    parser = CalendarParser()
    parser.feed(html)
    return parser.days()

def compute_streaks(days, today):
    counts = {dt.date.fromisoformat(d['date']): d['count'] for d in days}
    ordered = sorted(d for d in counts if d <= today)
    best = run = 0
    previous = None
    for date in ordered:
        run = (run + 1 if previous == date - dt.timedelta(days=1) else 1) if counts[date] > 0 else 0
        best = max(best, run)
        previous = date
    cursor = today if counts.get(today, 0) > 0 else today - dt.timedelta(days=1)
    current = 0
    while counts.get(cursor, 0) > 0:
        current += 1
        cursor -= dt.timedelta(days=1)
    return {'current': current, 'longest': best}

def public_repos():
    repos = []
    page = 1
    while True:
        batch = fetch(f'{API}/users/{USER}/repos?per_page=100&type=owner&sort=full_name&page={page}')
        if not isinstance(batch, list): raise ValueError('Unexpected repositories response')
        repos.extend(r for r in batch if not r.get('private') and r['owner']['login'].lower() == USER)
        if len(batch) < 100: break
        page += 1
    return repos

def language_bytes(repos):
    selected = [r for r in repos if not r['fork'] and not r['archived'] and r['name'].lower() != USER]
    def one(repo):
        return fetch(f'{API}/repos/{USER}/{quote(repo["name"], safe="")}/languages')
    totals = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for result in pool.map(one, selected):
            if not isinstance(result, dict): raise ValueError('Unexpected language response')
            for name, size in result.items():
                if not isinstance(size, int) or size < 0: raise ValueError('Invalid language byte count')
                totals[name] = totals.get(name, 0) + size
    return sorted(totals.items(), key=lambda x: (-x[1], x[0]))

def collect():
    now = dt.datetime.now(dt.timezone.utc)
    today = now.date()
    user = fetch(f'{API}/users/{USER}')
    created = dt.datetime.fromisoformat(user['created_at'].replace('Z', '+00:00')).date()
    start = dt.date(created.year, 1, 1)
    days = {}
    def calendar_year(year):
        end = min(today, dt.date(year,12,31))
        url = f'https://github.com/users/{USER}/contributions?from={year}-01-01&to={end.isoformat()}'
        return year, parse_calendar(fetch(url, False))
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        for year, values in pool.map(calendar_year, range(created.year, today.year+1)):
            for day in values:
                date = dt.date.fromisoformat(day['date'])
                if date.year == year and start <= date <= today: days[day['date']] = day
    cursor = start
    while cursor <= today:
        if cursor.isoformat() not in days:
            raise ValueError(f'Incomplete contribution calendar ({cursor}); existing cards preserved.')
        cursor += dt.timedelta(days=1)
    all_days = sorted(days.values(), key=lambda x:x['date'])
    recent_start = max(start, today - dt.timedelta(days=364))
    recent = [d for d in all_days if recent_start.isoformat() <= d['date'] <= today.isoformat()]
    repos = public_repos()
    owned = [r for r in repos if not r['fork']]
    langs = language_bytes(repos)
    counts = {}
    for kind in ['pr','issue']:
        result = fetch(f'{API}/search/issues?' + urlencode({'q':f'author:{USER} is:{kind} is:public','per_page':1}))
        if result.get('incomplete_results'): raise ValueError('Search results incomplete; existing cards preserved.')
        counts[kind] = result['total_count']
    return {
        'schema_version':1,'username':USER,'updated_at':now.isoformat(timespec='seconds'),
        'today':today.isoformat(), 'history_start':start.isoformat(),'recent_start':recent_start.isoformat(),
        'scope':'Public repositories and counts visible on the public GitHub contribution calendar. Private repository details are never requested.',
        'public_repositories':len(repos), 'public_original_repositories':len(owned),
        'public_repository_stars':sum(r['stargazers_count'] for r in owned),
        'public_pull_requests':counts['pr'], 'public_issues':counts['issue'],
        'contributions_365_days':sum(d['count'] for d in recent),
        'active_days_365_days':sum(d['count'] > 0 for d in recent),
        'contributions_since_history_start':sum(d['count'] for d in all_days),
        'streaks':compute_streaks(all_days,today),'languages':langs,
        'days':all_days,'repositories':[{'name':r['name'],'url':r['html_url'],'language':r['language'],'stars':r['stargazers_count'],'updated_at':r['updated_at']} for r in repos],
        'sources':{'repositories':f'{API}/users/{USER}/repos','calendar':f'https://github.com/users/{USER}/contributions','languages':f'{API}/repos/{USER}/{{repository}}/languages','issues':f'{API}/search/issues'},
    }

def stats_card(data, mobile=False):
    w=600 if mobile else 1000
    body = heading('GitHub overview','Public repositories · visible contribution counts' if mobile else 'Public repository statistics · contribution counts visible on GitHub',w)
    metrics = [('Contributions / 365 days',data['contributions_365_days']),('Public repositories',data['public_repositories']),('Stars on original repositories',data['public_repository_stars']),('Public pull requests',data['public_pull_requests']),('Public issues',data['public_issues']),('Active days / 365 days',data['active_days_365_days'])]
    for i,(label,value) in enumerate(metrics):
        cols=2 if mobile else 3
        x=32+(i%cols)*(284 if mobile else 322);y=142+(i//cols)*102
        body+=text(x,y,fmt(value),37,LIME,700)+text(x,y+28,label,14 if mobile else 15,MUTED)
    h=438 if mobile else 338
    body += text(30,h-20,'Refreshed '+data['updated_at'][:10]+' UTC',13,MUTED)
    return svg(w,h,body,'GitHub overview','; '.join(f'{k}: {v}' for k,v in metrics))

def streak_card(data,mobile=False):
    since=data['history_start'][:4]
    w=600 if mobile else 1000
    body=heading('Consistency',f'Contribution-day streaks · January {since} onwards · UTC',w)
    values=[('Total contributions',data['contributions_since_history_start'],f'January {since} to today'),('Current streak',data['streaks']['current'],'days · today may still be in progress'),('Longest streak',data['streaks']['longest'],f'consecutive days since {since}')]
    for i,(title,value,sub) in enumerate(values):
        if mobile:
            y=142+i*100
            body+=text(32,y,fmt(value),42,LIME,700)+text(205,y-7,title,19,TEXT,600)+text(205,y+20,sub,14,MUTED)
            if i<2:body+=line(30,y+40,570,y+40)
        else:
            x=168+i*331
            if i:body+=line(x-165,115,x-165,226)
            body+=text(x,157,fmt(value),43,LIME,700,'middle')+text(x,190,title,18,TEXT,600,'middle')+text(x,218,sub,12,MUTED,400,'middle')
    return svg(w,390 if mobile else 247,body,'Contribution streaks','; '.join(f'{t}: {v}. {s}' for t,v,s in values))

def languages_card(data,mobile=False):
    w=600 if mobile else 1000
    body=heading('Repository languages' if mobile else 'Languages across my repositories','Source bytes · public originals · profile repo excluded' if mobile else 'Source bytes · public, non-fork, non-archived repositories · profile repo excluded',w)
    rows=data['languages']; total=sum(v for _,v in rows)
    if not total:
        body+=text(30,135,'No language bytes returned by GitHub.',20,MUTED)
        return svg(w,180,body,'Repository languages')
    display=rows[:5]
    if len(rows)>5:display=display+[('Other',sum(v for _,v in rows[5:]))]
    for i,(name,value) in enumerate(display):
        y=122+i*42
        bx,bw=(190,280) if mobile else (240,610)
        body+=text(30,y+2,name,17,TEXT,600)+text(w-32,y+2,f'{value/total*100:.1f}%',15,LIME,500,'end')
        body+=rect(bx,y-12,bw,13,'#202a24','none',5)+rect(bx,y-12,max(1,bw*value/total),13,LIME,'none',5)
    height=151+len(display)*42
    body+=text(30,height-22,'Repository composition, not a proficiency score.',13,MUTED)
    return svg(w,height,body,'Repository language composition','; '.join(f'{n}: {v/total*100:.1f} percent of bytes' for n,v in rows))

def calendar_card(data,mobile=False):
    today=dt.date.fromisoformat(data['today'])
    start=dt.date.fromisoformat(data['recent_start'])
    first_sunday=start-dt.timedelta(days=(start.weekday()+1)%7)
    days=[d for d in data['days'] if data['recent_start']<=d['date']<=data['today']]
    w=600 if mobile else 1000
    body=heading('Contribution calendar',f'{data["recent_start"]} → {data["today"]} · {fmt(data["contributions_365_days"])} contributions',w)
    x0,y0,step,size=56,124,17,13
    for weekday,label in [(1,'Mon'),(3,'Wed'),(5,'Fri')]:body+=text(15,y0+weekday*step+11,label,10,MUTED)
    if mobile:
        for weekday,label in [(1,'Mon'),(3,'Wed'),(5,'Fri')]:body+=text(15,y0+185+weekday*step+11,label,10,MUTED)
    last_month=None; last_label_col=-5
    for d in days:
        date=dt.date.fromisoformat(d['date']); col=(date-first_sunday).days//7;row=(date.weekday()+1)%7
        segment=col//27 if mobile else 0
        local_col=col%27 if mobile else col
        yy=y0+segment*185
        if date.month != last_month or (mobile and col==27 and row==0):
            if col-last_label_col >= 3:
                body+=text(x0+local_col*step,yy-12,date.strftime('%b'),11,MUTED);last_label_col=col
            last_month=date.month
        body+=f'<g><title>{d["date"]}: {d["count"]} contributions</title>'+rect(x0+local_col*step,yy+row*step,size,size,LEVELS[d['level']],'none',3)+'</g>'
    foot=465 if mobile else 282
    if not mobile:body+=text(30,foot,'Daily contribution counts visible on your public GitHub profile.',13,MUTED)
    lx=365 if mobile else 795
    body+=text(lx,foot,'Less',11,MUTED)
    for i,color in enumerate(LEVELS):body+=rect(lx+30+i*18,foot-12,13,13,color,'none',3)
    body+=text(lx+131,foot,'More',11,MUTED)
    return svg(w,488 if mobile else 304,body,'Obsidian contribution calendar',f'{data["contributions_365_days"]} contributions across the last 365 days. An accessible daily data table is stored in data/metrics.json.')

def render(data):
    result={}
    for mobile in [False,True]:
        suffix='-mobile' if mobile else ''
        for name,fn in [('overview',stats_card),('streak',streak_card),('languages',languages_card),('calendar',calendar_card)]:
            result[name+suffix+'.svg']=fn(data,mobile)
    return result

def save(data):
    rendered=render(data)  # Validate and render all cards before touching previous files.
    target=ROOT/'assets'/'metrics'
    target.mkdir(parents=True,exist_ok=True)
    (ROOT/'data').mkdir(exist_ok=True)
    outputs={target/name:body for name,body in rendered.items()}
    outputs[ROOT/'data'/'metrics.json']=json.dumps(data,indent=2,ensure_ascii=False)+'\n'
    with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
        staged=[]
        for i,(path,body) in enumerate(outputs.items()):
            temp=Path(tmp)/str(i);temp.write_text(body,encoding='utf-8');staged.append((temp,path))
        for temp,path in staged:os.replace(temp,path)

def main():
    data=collect()
    save(data)
    print(f'Refreshed {USER}: {data["public_repositories"]} public repositories; {data["contributions_365_days"]} contributions in the last 365 days; {len(data["days"])} calendar days validated.')

if __name__=='__main__':main()
