# -*- coding: utf-8 -*-
"""Тестовые файлы: MIDI (C5 E5 G5 C6...) и WAV (чистые синусы той же мелодии)."""
import struct, math, os

OUT='/home/z/my-project/scripts/testdata'
os.makedirs(OUT,exist_ok=True)

def vlq(n):
    b=[n&127]
    n>>=7
    while n:
        b.insert(0,(n&127)|128)
        n>>=7
    return bytes(b)

# ---------- MIDI ----------
DIV=480
events=[]  # (absTick, trackBytes)
# мелодия ch0: (beat, durBeats, midi)
mel=[(0,1,72),(1,1,76),(2,1,79),(3,1,84),
     (4,0.5,81),(4.5,0.5,79),(5,0.5,76),(5.5,0.5,72),
     (6,1,74),(7,1,67)]
for b,d,p in mel:
    t0=int(b*DIV);t1=int((b+d)*DIV)
    events.append((t0,bytes([0x90,p,100])))
    events.append((t1,bytes([0x80,p,0])))
# бас ch1
for b,p in [(0,48),(4,41)]:
    t0=int(b*DIV);t1=int((b+4)*DIV)
    events.append((t0,bytes([0x91,p,90])))
    events.append((t1,bytes([0x81,p,0])))
# барабаны ch9
for b in range(8):
    events.append((int(b*DIV),bytes([0x99,36,100])))
for b in [1,3,5,7]:
    events.append((int(b*DIV),bytes([0x99,38,100])))
# конец трека
events.append((8*DIV,bytes([0xff,0x2f,0x00])))
events.sort(key=lambda e:e[0])
track=bytearray()
track+=vlq(0)+bytes([0xff,0x51,0x03,0x07,0xa1,0x20])  # tempo 120 bpm
last=0
for t,ev in events:
    track+=vlq(t-last)+ev
    last=t
mid=bytearray()
mid+=b'MThd'+struct.pack('>IHHH',6,0,1,DIV)
mid+=b'MTrk'+struct.pack('>I',len(track))+track
open(OUT+'/test.mid','wb').write(bytes(mid))
print('test.mid',len(mid),'bytes')

# ---------- WAV ----------
SR=22050
DUR=4.0
n=int(SR*DUR)
buf=bytearray()
melody=[440.0,523.25,659.26,783.99]  # A4 C5 E5 G5
noteDur=0.5
for i in range(n):
    t=i/SR
    s=0.0
    # мелодия с огибающей
    nt=int(t/noteDur)
    f=melody[nt%4]
    lt=t-nt*noteDur
    a=0.5
    if lt<0.01:a*=lt/0.01
    if lt>noteDur-0.05:a*=max(0.0,(noteDur-lt)/0.05)
    s+=a*math.sin(2*math.pi*f*t)
    # бас A2
    s+=0.22*math.sin(2*math.pi*110*t)
    # кик каждые 0.5 с
    bt=t%(noteDur)
    if bt<0.09:
        s+=0.35*math.exp(-bt*40)*math.sin(2*math.pi*60*t)
    v=max(-32767,min(32767,int(s*32767)))
    buf+=struct.pack('<h',v)
wh=b'RIFF'+struct.pack('<I',36+len(buf))+b'WAVEfmt '+struct.pack('<IHHIIHH',16,1,1,SR,SR*2,2,16)+b'data'+struct.pack('<I',len(buf))
open(OUT+'/tone.wav','wb').write(wh+bytes(buf))
print('tone.wav',len(wh+buf),'bytes')
