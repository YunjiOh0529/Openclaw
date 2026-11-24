import os
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
plt.rcParams.update({'font.family':'DejaVu Sans'})
OUT=os.environ.get('FIG_OUT','figures/Figure1.png')
INK='#000000'; INK2='#1a1a1a'; BG='#fcfcfb'
H1,H2,B,L=8.0,7.0,6.3,5.9

fig,ax=plt.subplots(figsize=(7.0,5.1)); ax.set_xlim(0,14.0); ax.set_ylim(0,10.2); ax.axis('off')
fig.subplots_adjust(0,0,1,1)
def rbox(x0,y0,w,h,ec=INK2,fc=BG,lw=1.4,ls='-',r=0.12):
    ax.add_patch(FancyBboxPatch((x0,y0),w,h,boxstyle=f'round,pad=0,rounding_size={r}',fc=fc,ec=ec,lw=lw,ls=ls))
def t(x,y,s,size=B,bold=False,color=INK,ha='center',va='center',style='normal'):
    ax.text(x,y,s,fontsize=size,fontweight='bold',color=INK,ha=ha,va=va,linespacing=1.22,style=style)
def arr(p,q,both=False,rad=0.0,lw=1.5,ms=9):
    ax.add_patch(FancyArrowPatch(p,q,arrowstyle='<|-|>' if both else '-|>',mutation_scale=ms,color=INK2,lw=lw,
        connectionstyle=f'arc3,rad={rad}',shrinkA=0,shrinkB=0))
def lab(x,y,s): t(x,y,s,L,color=INK2,style='italic')
TOP=10.05; BOT=0.72

LV=[('Level 1','Vehicle control','door, lights, turn signals,\nstatus, driving','#6250d6'),
    ('Level 2','Information retrieval','weather, location, date,\nday, speed','#2a78d6'),
    ('Level 3','Multi-command','2–3 actions and questions\nin one utterance','#1baf7a'),
    ('Level 4','Indirect command','situation with a keyword\nof the level-4 skill','#eda100'),
    ('Level 4P','Paraphrased Level 4','same situations\nwithout the keywords','#eb6834'),
    ('Level 5','External API, memory','POI, news, weather, music,\nuser data (N and P)','#e34948')]
n=len(LV); gap=0.14; h=(TOP-0.05-gap*(n-1))/n; y=TOP
for a,b,body,c in LV:
    rbox(0.06,y-h,3.05,h,ec=c,lw=1.8)
    t(0.2,y-0.3,a,H2,True,ha='left'); t(0.2,y-0.66,b,B,True,ha='left',color=INK)
    t(0.2,y-1.17,body,B-0.3,color=INK2,ha='left')
    y-=h+gap

sx0,sx1=3.85,6.5; sc=(sx0+sx1)/2
rbox(sx0,BOT,sx1-sx0,TOP-BOT,ec='#1baf7a',lw=1.8)
t(sc,TOP-0.38,'Workspace skills',H1,True); t(sc,TOP-0.8,'SKILL.md + Python script',B-0.4,color=INK2,style='italic')
groups=[('Experiment setup',['carla-vehicle-spawner']),('Vehicle (Levels 1–4)',['level-1','level-2','level-4']),
        ('External API (Level 5)',['poi-google-place','naver-local-search','weather-search','lastfm-music']),
        ('Memory (Level 5)',['memory-pattern','memory-personalization'])]
yy=TOP-1.38
for g,items in groups:
    t(sx0+0.15,yy,g,B,True,ha='left'); yy-=0.43
    for it in items: t(sx0+0.22,yy,'· '+it,B-0.55,ha='left',color=INK2); yy-=0.37
    yy-=0.3

x0,x1=7.25,11.05; cx=(x0+x1)/2
rbox(x0,BOT,x1-x0,TOP-BOT,ec='#e34948',lw=2.0)
t(cx,TOP-0.38,'OpenClaw agent (Computer B)',H1-0.3,True); t(cx,TOP-0.88,'OpenClaw 2026.11.3, new session per trial',B-1.2,color=INK2,style='italic')
rbox(x0+0.25,7.85,x1-x0-0.5,0.95); t(cx,8.5,'User command input',H2-0.3,True); t(cx,8.1,'e.g., "Turn on the hazard lights"',B-0.4,color=INK2)
rbox(x0+0.18,2.65,x1-x0-0.36,4.95,ec='#e34948',ls='--',lw=1.0)
t(cx,7.27,'Agent processing loop',H2-0.3,True)
rbox(cx-1.2,5.75,2.4,1.1); t(cx,6.55,'Reason',H2-0.3,True); t(cx,6.08,'interpret the command\nand plan the next step',B-0.5,color=INK2)
bw=1.58
rbox(x0+0.3,3.85,bw,1.25); t(x0+0.3+bw/2,4.78,'Observe',H2-0.3,True); t(x0+0.3+bw/2,4.25,'collect skill\nand tool output',B-0.6,color=INK2)
rbox(x1-0.3-bw,3.85,bw,1.25); t(x1-0.3-bw/2,4.78,'Act',H2-0.3,True); t(x1-0.3-bw/2,4.25,'read SKILL.md,\nrun skills/tools',B-0.6,color=INK2)
arr((cx+1.22,6.15),(x1-0.3-bw/2+0.1,5.12),rad=-0.3)
arr((x1-0.3-bw/2,3.83),(x0+0.3+bw/2,3.83),rad=-0.45)
arr((x0+0.3+bw/2-0.1,5.12),(cx-1.22,6.15),rad=-0.3)
t(cx,2.9,'repeat if needed',L,color=INK2,style='italic')
rbox(x0+0.25,0.95,x1-x0-0.5,1.35); t(cx,1.9,'Final response',H2-0.3,True); t(cx,1.38,'answer in natural language\nand report the result',B-0.5,color=INK2)
arr((cx,7.85),(cx,7.62)); arr((cx,2.65),(cx,2.32))

r0,r1=12.15,13.95; rc=(r0+r1)/2
rbox(r0,6.45,r1-r0,TOP-6.45,ec='#2a78d6',lw=1.8)
t(rc,TOP-0.38,'CARLA',H1,True); t(rc,TOP-0.78,'(Computer A)',B-0.4,color=INK2,style='italic')
rbox(r0+0.14,6.7,r1-r0-0.28,2.3); t(rc,8.35,'CARLA\n0.9.16',H2-0.3,True); t(rc,7.3,'Lincoln\nMKZ 2020',B-0.4,color=INK2)
rbox(r0,BOT,r1-r0,5.5,ec='#eda100',lw=1.8)
t(rc,5.82,'External\nservices',H2,True)
rbox(r0+0.12,4.15,r1-r0-0.24,1.0); t(rc,4.82,'Gemini API',B,True); t(rc,4.43,'LLM',B-0.4,color=INK2)
rbox(r0+0.12,2.25,r1-r0-0.24,1.7); t(rc,3.62,'External APIs',B,True); t(rc,2.88,'Google Places\nNaver News\nOpenWeather\nLast.fm',B-0.7,color=INK2)
rbox(r0+0.12,0.88,r1-r0-0.24,1.17,fc='#f1f0ec'); t(rc,1.73,'User data',B,True); t(rc,1.26,'memory_data\n.json (read-only)',B-1.2,color=INK2)

arr((3.13,5.3),(sx0-0.02,5.3)); t((3.13+sx0)/2,5.6,'com-\nmands',L-0.4,color=INK2,style='italic')
arr((sx1+0.02,5.3),(x0-0.02,5.3),both=True); lab((sx1+x0)/2,5.7,'read,\nrun')
mid=(x1+r0)/2
arr((x1+0.02,7.55),(r0-0.02,7.55),both=True); lab(mid,8.15,'CARLA\nAPI\ncontrol,\nstate')
arr((x1+0.02,4.65),(r0+0.1,4.65),both=True); lab(mid,5.07,'LLM\nrequests')
arr((x1+0.02,3.1),(r0+0.1,3.1),both=True); lab(mid,3.52,'Level 5\nskills')
arr((x1+0.02,1.46),(r0+0.1,1.46),both=True); lab(mid,1.88,'memory\nskills')

rbox(sx0,0.06,r1-sx0,0.5,ec=INK2,ls='--',lw=1.0,r=0.08)
t((sx0+r1)/2,0.31,'Baseline (Computer C)   same model and Level 5 skills, direct function calling without OpenClaw',B-0.2)
os.makedirs(os.path.dirname(OUT) or '.',exist_ok=True)
fig.savefig(OUT,dpi=300,facecolor='white')
