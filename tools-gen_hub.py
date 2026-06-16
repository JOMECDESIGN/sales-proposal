# -*- coding: utf-8 -*-
# 一站式六维放射图 — 高清渲染(品牌蓝紫 + 辉光球体 + 放射光束 + 虚线轨道)
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math, os

S=240.0  # px per inch
WIN,HIN=10.0,5.625
W,H=int(WIN*S),int(HIN*S)
FONT='/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'
def F(pt): return ImageFont.truetype(FONT, int(pt*S/72.0*1.0), index=0)
def px(xin,yin): return (int(xin*S),int(yin*S))

base=Image.new('RGB',(W,H),(6,9,18))
# 背景径向暗角(中心略亮)
vg=Image.new('L',(W,H),0); dv=ImageDraw.Draw(vg)
cx,cy=W//2,int(2.75*S)
for i in range(60):
    r=int((1-i/60)* (W*0.62)); a=int(38*(i/60))
    dv.ellipse([cx-r,cy-r,cx+r,cy+r],fill=a)
vg=vg.filter(ImageFilter.GaussianBlur(80))
glowbg=Image.new('RGB',(W,H),(18,30,78))
base=Image.composite(glowbg,base,vg)

draw=ImageDraw.Draw(base,'RGBA')

C=(5.0,2.72)
caps=[  # (name, cx,cy, color)
 ('软硬件开发', 5.0, 1.02, (124,58,237)),
 ('造型设计',   5.0, 4.42, (32,191,107)),
 ('交互系统开发',2.62,2.72, (0,181,227)),
 ('展车模型制作',7.38,2.72, (244,63,94)),
]
Rcap=0.62; Rctr=1.04

# ---- 放射光束(4条对角)----
beam=Image.new('RGBA',(W,H),(0,0,0,0)); db=ImageDraw.Draw(beam)
ccx,ccy=px(*C)
for (dx,dy) in [(-1,-1),(1,-1),(-1,1),(1,1)]:
    ex,ey=ccx+dx*W*0.62, ccy+dy*H*0.95
    spread=int(0.9*S)
    db.polygon([(ccx,ccy),(ex-spread*(1 if dx>0 else -1),ey),(ex+spread*(0.2),ey)],fill=(36,107,255,70))
beam=beam.filter(ImageFilter.GaussianBlur(70))
base.alpha_composite(beam) if base.mode=='RGBA' else base.paste(Image.alpha_composite(base.convert('RGBA'),beam).convert('RGB'),(0,0))
base=base.convert('RGB'); draw=ImageDraw.Draw(base,'RGBA')

# ---- 虚线椭圆轨道 ----
orb=Image.new('RGBA',(W,H),(0,0,0,0)); do=ImageDraw.Draw(orb)
rx,ry=2.38*S,1.7*S
seg=140
for i in range(seg):
    if i%2: continue
    a0=2*math.pi*i/seg; a1=2*math.pi*(i+1)/seg
    p0=(ccx+rx*math.cos(a0),ccy+ry*math.sin(a0)); p1=(ccx+rx*math.cos(a1),ccy+ry*math.sin(a1))
    do.line([p0,p1],fill=(120,160,230,150),width=2)
base.paste(Image.alpha_composite(base.convert('RGBA'),orb).convert('RGB'),(0,0))
draw=ImageDraw.Draw(base,'RGBA')

# ---- 中心→各球 虚线指引 ----
guide=Image.new('RGBA',(W,H),(0,0,0,0)); dg=ImageDraw.Draw(guide)
for (nm,xx,yy,col) in caps:
    p0=px(*C); p1=px(xx,yy)
    ang=math.atan2(p1[1]-p0[1],p1[0]-p0[0])
    s0=(p0[0]+math.cos(ang)*Rctr*S, p0[1]+math.sin(ang)*Rctr*S)
    s1=(p1[0]-math.cos(ang)*Rcap*S, p1[1]-math.sin(ang)*Rcap*S)
    n=14
    for i in range(n):
        if i%2: continue
        t0=i/n; t1=(i+0.6)/n
        a=(s0[0]+(s1[0]-s0[0])*t0,s0[1]+(s1[1]-s0[1])*t0)
        b=(s0[0]+(s1[0]-s0[0])*t1,s0[1]+(s1[1]-s0[1])*t1)
        dg.line([a,b],fill=(150,180,235,170),width=3)
base.paste(Image.alpha_composite(base.convert('RGBA'),guide).convert('RGB'),(0,0))
draw=ImageDraw.Draw(base,'RGBA')

def sphere(cx,cy,r,color,glow=True):
    cxp,cyp,rp=int(cx*S),int(cy*S),int(r*S)
    if glow:
        g=Image.new('RGBA',(W,H),(0,0,0,0)); dgw=ImageDraw.Draw(g)
        dgw.ellipse([cxp-rp-26,cyp-rp-26,cxp+rp+26,cyp+rp+26],fill=color+(150,))
        g=g.filter(ImageFilter.GaussianBlur(34))
        base.paste(Image.alpha_composite(base.convert('RGBA'),g).convert('RGB'),(0,0))
    d=ImageDraw.Draw(base,'RGBA')
    # 暗玻璃球体
    d.ellipse([cxp-rp,cyp-rp,cxp+rp,cyp+rp],fill=(10,14,28,255))
    # 内渐变(颜色由边缘向内)
    grad=Image.new('RGBA',(2*rp,2*rp),(0,0,0,0)); dgr=ImageDraw.Draw(grad)
    steps=rp
    for i in range(steps,0,-1):
        t=i/steps
        cc=(int(color[0]*t*0.9),int(color[1]*t*0.9),int(color[2]*t*0.9),int(120*t))
        dgr.ellipse([rp-i,rp-i,rp+i,rp+i],fill=cc)
    base.paste(Image.alpha_composite(base.crop([cxp-rp,cyp-rp,cxp+rp,cyp+rp]).convert('RGBA'),grad).convert('RGB'),(cxp-rp,cyp-rp))
    d=ImageDraw.Draw(base,'RGBA')
    # 亮边环
    d.ellipse([cxp-rp,cyp-rp,cxp+rp,cyp+rp],outline=color+(255,),width=max(3,int(0.03*S)))
    # 顶部高光
    hl=Image.new('RGBA',(W,H),(0,0,0,0)); dh=ImageDraw.Draw(hl)
    dh.ellipse([cxp-rp*0.55,cyp-rp*0.7,cxp+rp*0.55,cyp-rp*0.1],fill=(255,255,255,60))
    hl=hl.filter(ImageFilter.GaussianBlur(18))
    base.paste(Image.alpha_composite(base.convert('RGBA'),hl).convert('RGB'),(0,0))

# 4球 + 中心
for (nm,xx,yy,col) in caps: sphere(xx,yy,Rcap,col)
sphere(*C,Rctr,(36,107,255))

draw=ImageDraw.Draw(base,'RGBA')
def text(cx,cy,s,pt,color=(255,255,255),anchor='mm',bold=False,sp=0):
    f=F(pt)
    try: draw.text((cx*S,cy*S),s,font=f,fill=color+(255,) if len(color)==3 else color,anchor=anchor)
    except TypeError:
        w,h=draw.textbbox((0,0),s,font=f)[2:]; draw.text((cx*S-w/2,cy*S-h/2),s,font=f,fill=color)

# 中心 logo 峰形 + 文字
lx,ly=C[0],C[1]-0.42
draw.polygon([(lx*S,(ly-0.28)*S),((lx-0.26)*S,(ly+0.18)*S),((lx-0.06)*S,(ly+0.18)*S),(lx*S,(ly-0.05)*S),
              ((lx+0.06)*S,(ly+0.18)*S),((lx+0.26)*S,(ly+0.18)*S)],fill=(255,255,255,255))
text(C[0],C[1]+0.18,'智能座舱创新开发',17,(255,255,255),bold=True)
text(C[0],C[1]+0.5,'一站式解决方案公司',15,(150,200,255))

# 4球名称
for (nm,xx,yy,col) in caps:
    text(xx,yy, nm, 13.5,(255,255,255),bold=True)

# 角部价值标签
corners=[('协同合作','各团队无缝对接 · 各环节高效互动',1.9,1.18,'tl'),
         ('效率提升','减少冗余与沟通壁垒 · 精准把控节奏',8.1,1.18,'tr'),
         ('同步工作','并行模式 · 各部同步推进提升效率',1.9,4.5,'bl'),
         ('责任归属','清晰界定体系 · 问题与责任主体并解决',8.1,4.5,'br')]
for (t,sub,xx,yy,pos) in corners:
    al='lm' if 'l' in pos else 'rm'
    text(xx,yy,t,22,(235,240,255),anchor=('lm' if 'l' in pos else 'rm'),bold=True)
    text(xx,yy+0.34,sub,9.5,(150,160,185),anchor=('lm' if 'l' in pos else 'rm'))
    # 箭头
    dirx=-1 if 'l' in pos else 1; diry=-1 if 't' in pos else 1
    ax,ay=(xx+dirx*0.05),(yy- (0.45 if 't' in pos else -0.7))
    draw.line([((xx+dirx*1.0)*S,(yy+diry*0.95)*S),((xx+dirx*0.05)*S,(yy- (0.5 if 't' in pos else -0.75))*S)],fill=(170,180,205,220),width=3)

# 角色标签(小字,灰)
roles=[
 (3.4,0.82,'座舱系统·电器·上位机'),(3.4,1.05,'嵌入式·智能产品工程师'),
 (6.6,0.82,'硬件架构·硬件开发'),(6.6,1.05,'测试工程师'),
 (5.0,5.2,'前瞻 · 内外造型 · 零部件 · 色彩 · CAS建模'),
 (1.3,2.36,'UI/UX 设计师'),(1.3,2.66,'动画师 · VR开发/内容'),
 (8.7,2.36,'原型车制作 · 品质/成本经理'),(8.7,2.66,'工艺设计 · 产品交付 · 售后管理'),
]
for (xx,yy,t) in roles:
    text(xx,yy,t,9,(140,150,175),anchor='mm')

# 标题(左上)
text(0.0,0.0,'',1)
draw.rectangle([int(0.5*S),int(0.34*S),int(0.5*S+0.07*S),int(0.34*S+0.5*S)],fill=(124,58,237,255))
ft=F(20); draw.text((0.68*S,0.32*S),'组织协同:四大能力中心,收敛于一个责任主体',font=ft,fill=(255,255,255,255))
fe=F(10); draw.text((0.7*S,0.74*S),'ONE-STOP ACCOUNTABILITY',font=fe,fill=(0,181,227,255))

base.save('/tmp/assets/hub.png')
print('hub.png',base.size)
EOF=1
