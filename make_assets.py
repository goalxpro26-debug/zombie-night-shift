#!/usr/bin/env python3
"""Original art for Zombie Night Shift — all drawn in code with PIL.
No stock, no copied art, no licensed characters."""
import math, random
from PIL import Image, ImageDraw
OUT="assets"
import os; os.makedirs(OUT, exist_ok=True)
random.seed(42)

def bg(path, graveyard=False):
    W,H=960,640
    img=Image.new("RGB",(W,H))
    d=ImageDraw.Draw(img,"RGBA")
    for y in range(H):
        t=y/H
        d.line([(0,y),(W,y)], fill=(int(8+10*t), int(12+14*t), int(28+22*t)))
    # stars
    for _ in range(120):
        x,y=random.randint(0,W), random.randint(0,220)
        r=random.randint(1,2); d.ellipse([x-r,y-r,x+r,y+r], fill=(220,220,255, random.randint(120,255)))
    # moon
    d.ellipse([780,40,860,120], fill=(235,230,190,255))
    d.ellipse([800,60,830,90], fill=(210,205,165,255))
    d.ellipse([830,85,845,100], fill=(210,205,165,255))
    # distant houses / trees silhouettes
    for x,w,h in [(0,180,120),(180,140,90),(700,160,110),(860,100,80)]:
        d.rectangle([x,300-h,x+w,300], fill=(10,14,30,255))
        d.polygon([(x-10,300-h),(x+w//2,300-h-50),(x+w+10,300-h)], fill=(8,10,24,255))
        for wx in range(x+20, x+w-15, 30):
            d.rectangle([wx,300-h+20,wx+12,300-h+38], fill=(255,200,80,180))
    # ground
    d.rectangle([0,300,W,640], fill=(22,32,24,255))
    # road horizontal
    d.rectangle([0,420,W,560], fill=(38,38,48,255))
    for x in range(20,W,70):
        d.rectangle([x,485,x+35,492], fill=(220,200,90,255))
    # sidewalk
    d.rectangle([0,380,W,420], fill=(60,60,66,255))
    d.rectangle([0,560,W,600], fill=(60,60,66,255))
    # lamps
    for x in (120,480,840):
        d.line([(x,380),(x,300)], fill=(30,30,35,255), width=6)
        d.ellipse([x-45,255,x+45,345], fill=(255,210,100,40))
        d.ellipse([x-12,288,x+12,312], fill=(255,220,120,255))
    # fence
    for x in range(0,W,40):
        d.rectangle([x,340,x+6,380], fill=(90,70,50,255))
    d.rectangle([0,350,W,356], fill=(90,70,50,255))
    if graveyard:
        for (x,y,s) in [(80,330,1),(200,315,1.2),(620,325,1),(760,310,1.3),(900,335,0.9),(350,320,1.1)]:
            d.rounded_rectangle([x,y,x+40*s,y+55*s], radius=12, fill=(110,110,120,255))
            d.text((x+12*s,y+12*s),"RIP", fill=(60,60,70,255))
        # dead tree
        d.line([(500,380),(500,260)], fill=(40,28,20,255), width=10)
        d.line([(500,300),(450,250)], fill=(40,28,20,255), width=6)
        d.line([(500,290),(560,240)], fill=(40,28,20,255), width=6)
    else:
        # bushes / grass tufts
        for _ in range(40):
            x,y=random.randint(0,W), random.randint(310,380)
            d.ellipse([x,y,x+18,y+8], fill=(18,48,26,255))
    img.save(f"{OUT}/{path}")

def zombie(path, skin, shirt, pants, size=64, kind="walker", acc=None):
    img=Image.new("RGBA",(size,size),(0,0,0,0))
    d=ImageDraw.Draw(img)
    cx,cy=size//2,size//2
    # shadow
    d.ellipse([cx-20,cy+16,cx+20,cy+26], fill=(0,0,0,90))
    # legs (top-down: feet below body)
    d.ellipse([cx-14,cy+8,cx-2,cy+24], fill=pants)
    d.ellipse([cx+2,cy+8,cx+14,cy+24], fill=pants)
    # arms reaching up (toward player direction = up in sprite)
    d.ellipse([cx-22,cy-18,cx-10,cy+2], fill=skin)
    d.ellipse([cx+10,cy-18,cx+22,cy+2], fill=skin)
    d.ellipse([cx-22,cy-22,cx-12,cy-12], fill=skin)  # hands
    d.ellipse([cx+12,cy-22,cx+22,cy-12], fill=skin)
    # torso
    d.ellipse([cx-18,cy-12,cx+18,cy+16], fill=shirt)
    # torn shirt patch
    d.rectangle([cx-6,cy-2,cx+8,cy+8], fill=(skin[0],skin[1],skin[2],255))
    # head
    d.ellipse([cx-13,cy-30,cx+13,cy-6], fill=skin)
    # eyes
    if kind=="boss":
        d.ellipse([cx-9,cy-22,cx-3,cy-16], fill=(255,0,0,255)); d.ellipse([cx+3,cy-22,cx+9,cy-16], fill=(255,0,0,255))
        # horns
        d.polygon([(cx-13,cy-28),(cx-20,cy-40),(cx-8,cy-30)], fill=(60,40,20,255))
        d.polygon([(cx+13,cy-28),(cx+20,cy-40),(cx+8,cy-30)], fill=(60,40,20,255))
    elif kind=="spitter":
        d.ellipse([cx-9,cy-22,cx-3,cy-16], fill=(255,220,0,255)); d.ellipse([cx+3,cy-22,cx+9,cy-16], fill=(255,220,0,255))
        d.ellipse([cx-5,cy-12,cx+5,cy-4], fill=(80,0,80,255))  # open mouth
    else:
        d.ellipse([cx-9,cy-22,cx-3,cy-16], fill=(255,255,255,255)); d.ellipse([cx+3,cy-22,cx+9,cy-16], fill=(255,255,255,255))
        d.ellipse([cx-7,cy-20,cx-4,cy-17], fill=(0,0,0,255)); d.ellipse([cx+4,cy-20,cx+7,cy-17], fill=(0,0,0,255))
    # blood / wound
    d.ellipse([cx+6,cy+2,cx+14,cy+10], fill=(140,0,0,200))
    if acc=="hat":
        d.ellipse([cx-14,cy-34,cx+14,cy-26], fill=(40,40,40,255))
        d.rectangle([cx-8,cy-42,cx+8,cy-28], fill=(40,40,40,255))
    if acc=="cap":
        d.ellipse([cx-13,cy-32,cx+13,cy-24], fill=(180,30,30,255))
    if acc=="bandana":
        d.rectangle([cx-13,cy-30,cx+13,cy-24], fill=(200,0,0,255))
    img.save(f"{OUT}/{path}")

def player():
    img=Image.new("RGBA",(64,64),(0,0,0,0)); d=ImageDraw.Draw(img)
    cx,cy=32,32
    d.ellipse([12,48,52,58], fill=(0,0,0,90))
    d.ellipse([18,40,30,56], fill=(40,45,60,255)); d.ellipse([34,40,46,56], fill=(40,45,60,255))
    d.ellipse([16,30,24,44], fill=(240,200,160,255)); d.ellipse([40,30,48,44], fill=(240,200,160,255))
    d.ellipse([14,18,50,46], fill=(50,90,160,255))  # jacket
    d.rectangle([28,22,36,44], fill=(30,30,30,255))
    d.ellipse([19,4,45,30], fill=(240,200,160,255))  # head
    d.ellipse([24,14,29,19], fill=(0,0,0,255)); d.ellipse([35,14,40,19], fill=(0,0,0,255))
    d.ellipse([19,2,45,12], fill=(90,60,30,255))  # hair
    # rifle pointing up
    d.rectangle([29,0,35,22], fill=(30,30,30,255))
    img.save(f"{OUT}/player.png")

def misc():
    # barricade
    img=Image.new("RGBA",(96,56),(0,0,0,0)); d=ImageDraw.Draw(img)
    for i,y in enumerate([4,20,36]):
        d.rectangle([4,y,92,y+12], fill=(150,110,60,255) if i%2==0 else (130,95,50,255))
        d.line([(4,y),(92,y)], fill=(90,60,30,255), width=2)
    for x in (14,82):
        d.rectangle([x,0,x+8,56], fill=(110,80,45,255))
    img.save(f"{OUT}/barricade.png")
    # coin
    img=Image.new("RGBA",(32,32),(0,0,0,0)); d=ImageDraw.Draw(img)
    d.ellipse([4,4,28,28], fill=(255,210,0,255)); d.ellipse([8,8,24,24], fill=(255,230,100,255))
    d.text((12,10),"$", fill=(180,120,0,255)); img.save(f"{OUT}/coin.png")
    # heart
    img=Image.new("RGBA",(32,32),(0,0,0,0)); d=ImageDraw.Draw(img)
    d.ellipse([4,6,16,18], fill=(230,0,40,255)); d.ellipse([16,6,28,18], fill=(230,0,40,255))
    d.polygon([(4,14),(28,14),(16,29)], fill=(230,0,40,255)); img.save(f"{OUT}/heart.png")
    # medkit
    img=Image.new("RGBA",(40,40),(0,0,0,0)); d=ImageDraw.Draw(img)
    d.rounded_rectangle([4,8,36,36], radius=6, fill=(240,240,240,255))
    d.rectangle([17,13,23,31], fill=(220,0,0,255)); d.rectangle([10,20,30,26], fill=(220,0,0,255))
    img.save(f"{OUT}/medkit.png")

bg("background.png", False)
bg("background_graveyard.png", True)
player(); misc()
# base types
zombie("enemy_walker.png",(120,180,110),(90,90,110),(50,50,70,255))
zombie("enemy_runner.png",(150,170,90),(180,40,40,255),(30,30,40,255),kind="runner",acc="bandana")
zombie("enemy_spitter.png",(160,130,190),(90,40,110),(60,40,80,255),kind="spitter")
zombie("enemy_brute.png",(140,140,140),(70,70,80,255),(40,40,50,255),size=96,kind="brute")
zombie("enemy_boss.png",(110,200,110),(120,20,20,255),(20,20,20,255),size=128,kind="boss")
# per-level distinct walkers (different skin/shirt/accessory per night)
variants=[
 ((120,180,110),(90,90,110),None),((170,150,100),(30,90,140),None),((140,160,120),(140,90,30),"hat"),
 ((100,170,140),(60,60,60),"cap"),((180,140,120),(150,30,90),None),((130,150,180),(20,110,60),"bandana"),
 ((160,120,100),(110,40,40),None),((110,190,130),(80,30,120),"hat"),((150,170,110),(40,80,120),None),
 ((175,160,90),(130,130,30),"cap"),((120,140,160),(90,20,60),None),((140,180,100),(20,20,20),"bandana"),
]
for i,(skin,shirt,acc) in enumerate(variants,1):
    zombie(f"enemy_l{i:02d}.png",skin,shirt,(50,50,70,255),acc=acc)
print("assets done:", sorted(os.listdir(OUT)))
