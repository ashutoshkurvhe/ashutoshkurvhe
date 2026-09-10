"""Regenerate editable, repository-native visual assets. Python 3.10+; no packages."""
from pathlib import Path
from theme import *

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
TECH = {
 'Languages': [('html5', 'HTML5'), ('css3', 'CSS3'), ('javascript', 'JavaScript'), ('typescript', 'TypeScript')],
 'Frontend': [('react', 'React'), ('react-router', 'React Router'), ('redux', 'Redux'), ('tailwindcss', 'Tailwind CSS'), ('bootstrap', 'Bootstrap'), ('mui', 'MUI'), ('sass', 'Sass'), ('vite', 'Vite')],
 'Backend & database': [('nodejs', 'Node.js'), ('express', 'Express.js'), ('mongodb', 'MongoDB'), ('ejs', 'EJS')],
 'Developer tools': [('git', 'Git'), ('github', 'GitHub'), ('npm', 'npm'), ('nodemon', 'Nodemon')],
}

def write(name, value):
    path = ASSETS / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding='utf-8')

def badge(label, accent=False):
    w = max(78, round(len(label) * 7.6 + 34))
    body = rect(1, 1, w-2, 33, '#19241a' if accent else PANEL, '#3d522d' if accent else BORDER, 7)
    body += text(w/2, 23, label, 13, LIME if accent else TEXT, 600, 'middle')
    return svg(w, 35, body, label, background=False)

def hero(mobile=False):
    w, h = (600, 330) if mobile else (1000, 310)
    x = 32 if mobile else 40
    art = '''<defs><linearGradient id="ribbon" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#b5f36b" stop-opacity=".62"/><stop offset=".4" stop-color="#53772c" stop-opacity=".25"/><stop offset="1" stop-color="#0d1117"/></linearGradient><linearGradient id="edge"><stop stop-color="#b5f36b"/><stop offset="1" stop-color="#b5f36b" stop-opacity="0"/></linearGradient><clipPath id="clip"><rect x="1" y="1" width="998" height="308" rx="14"/></clipPath></defs>'''
    if not mobile:
        art += '<g clip-path="url(#clip)"><path d="M932 -70C917 22 849 91 809 167S822 261 1045 365L1110 127C926 186 896 148 994 -23Z" fill="url(#ribbon)"/><path d="M932 -70C917 22 849 91 809 167S822 261 1045 365" fill="none" stroke="url(#edge)" stroke-width="2"/></g>'
    else:
        art += '<path d="M500 255Q565 145 618 193V329H469Q455 294 500 255Z" fill="url(#ribbon)"/>'
    art += line(x, 34, x+48, 34, LIME, 3)
    art += text(x, 74, 'FULL STACK DEVELOPER', 15, MUTED, 600, letter_spacing=3)
    if mobile:
        art += text(x, 139, 'Ashutosh', 61, TEXT, 700) + text(x, 197, 'Kurvhe', 61, TEXT, 700)
        art += text(x, 245, 'Building useful web apps,', 22) + text(x, 275, 'from interface to API.', 22)
        art += text(x, 308, 'React  ·  Node.js  ·  TypeScript', 16, MUTED)
    else:
        art += text(x, 148, 'Ashutosh Kurvhe', 60, TEXT, 700)
        art += text(x, 198, 'Building useful web apps, from interface to API.', 24)
        art += text(x, 255, 'React  ·  Node.js  ·  TypeScript', 19, MUTED)
    return svg(w, h, art, 'Ashutosh Kurvhe — Full Stack Developer', 'Building useful web apps, from interface to API. React, Node.js and TypeScript.')

def project(name, desc, sub, route=False, mobile=False):
    w, h = (600, 350) if mobile else (1000, 240)
    thumb_w = 280 if mobile else 350
    art = rect(18, 18, thumb_w, 202, '#0d1217', BORDER, 10)
    if route:
        for yy in [53,94,135,176]: art += f'<path d="M28 {yy}l230 -35" stroke="#222d34"/>'
        art += '<path d="M45 164C103 117 158 211 216 148S291 159 327 71" fill="none" stroke="#b5f36b" stroke-width="3"/>' if not mobile else '<path d="M38 164C100 117 150 194 214 136S255 96 271 71" fill="none" stroke="#b5f36b" stroke-width="3"/>'
        art += '<g transform="translate(104 95)"><path d="M0 0l96 -14 25 16v48L25 67 0 49Z" fill="#28323a" stroke="#4b5660"/><path d="M25 17L121 2v48L25 67Z" fill="#172027"/><path d="M122 23l32 -5 23 25v26l-55 9Z" fill="#38442f" stroke="#607444"/><path d="M132 27l16 -3 15 17-31 5Z" fill="#121a20"/><circle cx="43" cy="65" r="12" fill="#0b1015" stroke="#687659"/><circle cx="146" cy="72" r="12" fill="#0b1015" stroke="#687659"/><rect x="162" y="54" width="9" height="5" fill="#b5f36b"/></g>'
    else:
        art += rect(103, 40, 139, 147, '#18211b', '#3c4b35', 9)
        art += rect(87, 53, 139, 147, '#151c22', '#34412f', 9)
        for i in range(3):
            y=78+i*38
            art+=rect(105,y,20,20,LIME if i==0 else '#151c22','#718259' if i==0 else '#5b6660',4)
            if i==0: art+='<path d="M110 88l4 4 7 -8" fill="none" stroke="#18251a" stroke-width="2"/>'
            art+=line(139,y+7,203,y+7,'#697668',4)+line(139,y+15,184,y+15,'#37443b',3)
    if mobile:
        tx,ty=32,269
        art += text(thumb_w+45,96,'IN',15,LIME,600,letter_spacing=2)+text(thumb_w+45,122,'DEVELOPMENT',15,LIME,600)
        art += text(tx,ty,name,32,TEXT,700)+text(tx,ty+32,desc,18,MUTED)+text(tx,ty+60,sub,14,MUTED)
    else:
        tx=405
        art += text(tx,77,name,35,TEXT,700)+text(tx,118,desc,23,MUTED)+text(tx,151,sub,16,MUTED)
        art += rect(tx,174,183,34,'#1b281a','#3b4f2d',8)+text(tx+16,197,'•  In development',16,LIME,600)
    return svg(w,h,art,name,desc+'. '+sub+'. In development.')

def main():
    write('hero.svg',hero())
    write('hero-mobile.svg',hero(True))
    for group, items in TECH.items():
        for slug,label in items: write(f'badges/{slug}.svg',badge(label))
    for slug,label in [('linkedin','LinkedIn'),('email','Email'),('repositories','All repositories'),('open-project','View repository'),('email-address','kurvheashutosh@gmail.com')]:write(f'badges/{slug}.svg',badge(label,True))
    for mobile in [False,True]:
        suffix='-mobile' if mobile else ''
        write(f'routewise{suffix}.svg',project('RouteWise','Multi-tenant logistics platform','Tenant isolation · dispatch · tracking',True,mobile))
        write(f'productivity{suffix}.svg',project('Productivity OS','Tasks, notes & focus in one place','Kanban · notes · calendar · Pomodoro',False,mobile))

if __name__ == '__main__':main()
