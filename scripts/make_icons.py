# -*- coding: utf-8 -*-
"""Иконки PWA: раундель с маской-балаклавой, виолет на чёрном."""
from PIL import Image, ImageDraw, ImageFont
import math

OUT='/home/z/my-project/'
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
VIOLET=(139,92,246); VIOLET_L=(196,181,253); DARK=(11,7,24); MASK=(26,16,48); EDGE=(49,38,90)

def draw_icon(S, pad=0.0):
    im=Image.new('RGB',(S,S),DARK); d=ImageDraw.Draw(im)
    sc=S*(1-2*pad); cx=cy=S/2
    r=sc*0.42
    # свечение за кругом
    for gr in range(int(sc*0.55),0,-4):
        a=int(40*(1-gr/(sc*0.55)))
        d.ellipse([cx-gr,cy-gr,cx+gr,cy+gr],fill=(DARK[0]+a//2,DARK[1],min(255,DARK[2]+a)))
    # шипы вокруг
    n=16
    for i in range(n):
        a=i/n*2*math.pi-math.pi/2
        p1=(cx+math.cos(a-0.13)*r*1.0,cy+math.sin(a-0.13)*r*1.0)
        p2=(cx+math.cos(a)*r*1.28,cy+math.sin(a)*r*1.28)
        p3=(cx+math.cos(a+0.13)*r*1.0,cy+math.sin(a+0.13)*r*1.0)
        d.polygon([p1,p2,p3],fill=(124,58,237))
    # кольцо
    w=max(3,int(sc*0.055))
    d.ellipse([cx-r,cy-r,cx+r,cy+r],outline=VIOLET,width=w)
    # маска над плашкой
    mrw,mrh=r*0.52,r*0.62; mcy=cy-r*0.38
    d.ellipse([cx-mrw,mcy-mrh,cx+mrw,mcy+mrh],fill=MASK,outline=EDGE,width=max(2,int(sc*0.02)))
    for k in range(1,4):
        y=mcy-mrh+k*mrh*0.5
        d.line([cx-mrw*0.85,y,cx+mrw*0.85,y],fill=(34,26,56),width=max(1,int(sc*0.01)))
    ew,eh=r*0.13,r*0.075
    for sx in (-1,1):
        d.ellipse([cx+sx*r*0.22-ew,mcy-eh,cx+sx*r*0.22+ew,mcy+eh],fill=VIOLET_L)
    # плашка
    sw,sh=sc*0.86,sc*0.15; sy=cy+r*0.62
    d.rectangle([cx-sw/2,sy-sh/2,cx+sw/2,sy+sh/2],fill=(5,3,8),outline=VIOLET,width=max(2,int(sc*0.02)))
    f=ImageFont.truetype(FONT,int(sh*0.62))
    tb=d.textbbox((0,0),'RAVE',font=f)
    d.text((cx-(tb[2]-tb[0])/2-tb[0],sy-(tb[3]-tb[1])/2-tb[1]),'RAVE',font=f,fill=VIOLET_L)
    return im

draw_icon(192).save(OUT+'icon-192.png')
draw_icon(512).save(OUT+'icon-512.png')
draw_icon(512,pad=0.12).save(OUT+'icon-maskable-512.png')
for f in ('icon-192.png','icon-512.png','icon-maskable-512.png'):
    im=Image.open(OUT+f); print(f, im.size)
