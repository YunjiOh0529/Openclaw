import pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Patch
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.edgecolor':'#52514e','axes.labelcolor':'#0b0b0b',
 'xtick.color':'#52514e','ytick.color':'#52514e','savefig.dpi':300})
import os
R='results/'; O='figures/'; os.makedirs(O, exist_ok=True)
INK='#0b0b0b'; INK2='#2b2a28'

d=pd.read_csv(R+'level14_results_final.csv')
FALSE={(1,'L4P-3'),(1,'L3-1'),(1,'L4-1'),(2,'L4-1'),(2,'L3-4'),(2,'L4P-1'),(3,'L4-1'),(3,'L4P-1'),(4,'L4-1'),(5,'L4-1')}
NOACT={(2,'L4P-3'),(2,'L4-2'),(4,'L4P-3'),(5,'L4-2'),(5,'L4P-2'),(5,'L4-4')}
WREF={(r,'L2-1') for r in range(1,6)}|{(4,'L3-3')}
def cls(r):
    k=(int(r['round']),r.cmd_id)
    if r.success_final=='y': return 0
    if k in FALSE: return 1
    if k in NOACT: return 2
    if k in WREF: return 3
    raise ValueError(k)
d['c']=d.apply(cls,axis=1)
assert (d.c==1).sum()==10 and (d.c==2).sum()==6 and (d.c==3).sum()==6
EN={'L1-1':'Open the driver\'s door','L1-2':'Turn on the hazard lights','L1-3':'Turn on the right turn signal','L1-4':'Check the vehicle status','L1-5':'Go forward 100 m',
'L2-1':'How\'s the weather now?','L2-2':'Where is my car now?','L2-3':'What day is it today?','L2-4':'Tell me today\'s date','L2-5':'What\'s the average speed now?',
'L3-1':'Close the doors and go forward','L3-2':'Tell me the weather and the speed','L3-3':'What time is it and where am I?','L3-4':'Stop the car and tell me the location','L3-5':'Close the doors, go forward, tell me the speed',
'L4-1':'It seems a bit dark','L4-2':'We\'ve arrived','L4-3':'I\'ll get out now','L4-4':'I\'m sleepy','L4-5':'It\'s dangerous',
'L4P-1':'I can\'t see well ahead','L4P-2':'Here we are','L4P-3':'I\'m getting out here','L4P-4':'My eyes keep closing','L4P-5':'Something just jumped out in front'}
order=[f'L{l}-{i}' for l in (1,2,3,4) for i in range(1,6)]+[f'L4P-{i}' for i in range(1,6)]
M=np.array([[d[(d.cmd_id==c)&(d['round']==r)].c.iloc[0] for r in range(1,6)] for c in order])
COL=['#dddbd4','#e34948','#eda100','#6250d6']; GLY=['','X','–','R']
fig,ax=plt.subplots(figsize=(7.6,8.2))
for i,c in enumerate(order):
    y=len(order)-1-i - (i//5)*0.0
    for j in range(5):
        v=M[i,j]
        ax.add_patch(plt.Rectangle((j+0.06,y+0.06),0.88,0.88,color=COL[v],lw=0))
        if v: ax.text(j+0.5,y+0.5,GLY[v],ha='center',va='center',color='white' if v!=2 else INK,fontsize=13,fontweight='bold')
    ax.text(5.15,y+0.5,f'{M[i].tolist().count(0)}/5',va='center',fontsize=11,color=INK,fontweight='bold')
ax.set_xlim(0,5.6); ax.set_ylim(0,len(order))
ax.set_xticks(np.arange(5)+0.5); ax.set_xticklabels([f'R{r}' for r in range(1,6)],fontsize=11.5,color=INK,fontweight='bold')
ax.set_yticks(np.arange(len(order))+0.5); ax.set_yticklabels([f'{c}  {EN[c]}' for c in order][::-1],fontsize=10.5,color=INK)
ax.tick_params(length=0); [s.set_visible(False) for s in ax.spines.values()]
ax.xaxis.set_ticks_position('top'); ax.set_xlabel('Round',labelpad=6,fontsize=12,fontweight='bold',color=INK); ax.xaxis.set_label_position('top')
for k in (5,10,15,20): ax.axhline(len(order)-k,color='#fcfcfb',lw=3)
ax.legend(handles=[Patch(color=COL[0],label='Success'),Patch(color=COL[1],label='X  Reported an action that was not performed'),
 Patch(color=COL[2],label='–  No action and no claim'),Patch(color=COL[3],label='R  Wrong reference (real world instead of simulator)')],
 loc='upper center',bbox_to_anchor=(0.42,-0.01),ncol=2,frameon=False,fontsize=10.5,handlelength=1.6,labelcolor=INK)
plt.tight_layout(); fig.savefig(O+'fig_level14_outcomes.png',bbox_inches='tight',facecolor='white'); plt.close()

a=pd.concat([pd.read_csv(R+f'level5_{s}_judged.csv') for s in ['OpenClaw','Direct']])
fig,ax=plt.subplots(figsize=(7.2,3.6))
C={'OpenClaw':'#2a78d6','Direct':'#eb6834'}; LAB={'OpenClaw':'OpenClaw','Direct':'Direct function calling'}
pos=0; yt=[];yl=[]
rng=np.random.default_rng(0)
for s in ['Direct','OpenClaw']:
    for c in ['P','N']:
        x=a[(a.system==s)&(a.condition==c)].total_sec.values
        ax.scatter(x,pos+rng.uniform(-0.2,0.2,len(x)),s=14,color=C[s],alpha=0.55,lw=0)
        ax.boxplot(x,positions=[pos],orientation='horizontal',widths=0.55,showfliers=False,patch_artist=True,
            boxprops=dict(facecolor='none',edgecolor=INK,lw=1.8),medianprops=dict(color=INK,lw=3),
            whiskerprops=dict(color=INK,lw=1.6),capprops=dict(color=INK,lw=1.6))
        ax.text(np.median(x),pos+0.44,f'{np.median(x):.1f} s',ha='center',fontsize=11,fontweight='bold',color=INK)
        yt.append(pos); yl.append(f'{LAB[s]}, {c}'); pos+=1.15
    pos+=0.45
ax.set_yticks(yt); ax.set_yticklabels(yl,fontsize=11,color=INK)
ax.set_xlabel('Response time (s)',fontsize=12,fontweight='bold',color=INK)
ax.tick_params(axis='x',labelsize=10.5,colors=INK,width=1.2); ax.tick_params(axis='y',length=0)
ax.set_xlim(0,None); ax.grid(axis='x',color='#d6d4cd',lw=0.9); ax.set_axisbelow(True)
[ax.spines[k].set_visible(False) for k in ('top','right','left')]; ax.spines['bottom'].set_linewidth(1.2)
plt.tight_layout(); fig.savefig(O+'fig_level5_latency.png',dpi=300,bbox_inches='tight',facecolor='white'); plt.close()
print('ok', a.total_sec.max())
