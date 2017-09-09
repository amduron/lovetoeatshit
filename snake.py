#!/usr/bin/env python
# -*- coding: utf8 -*-
################################################
#love to eat shit
#贪屎蛇
#auther:amduron
#2017.7.27
##################################################
import time
import oled
import random
import Image, ImageDraw
import threading 
import Queue
import os
import sys,termios
#from enum import Enum
class direction:
    Up=0
    Down=-1
    Left=1
    Right=-2
BODY=1
HEAD=0
TAIL=2
isrun=1

class keyinput(threading.Thread):
    
    def __init__(self):
        threading.Thread.__init__(self)
        self.keys = Queue.Queue()
        stdin = sys.stdin
        self.fd = stdin.fileno()
        
        new = old = termios.tcgetattr(self.fd)
        self.config=old 
        new[3] &= ~termios.ICANON
        new[3] &= termios.ECHO
        termios.tcsetattr(self.fd, termios.TCSAFLUSH, new)
    def __del__(self):
         termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.config)
    
    def getkey(self):
        if not self.keys.empty():
            return self.keys.get()
        else:
            return None
    def run(self):
        global isrun
        isrun=1;
        while isrun==1:
            a=os.read(self.fd,1)
            if a=='x':
                isrun=0;
                break;
            elif a in 'ABCD':
                self.keys.put(a)

titleheight=64
titlewidth=20
boxwidth=2
sw=128
sh=64
class shit:
    def __init__(self):
        self.size=8
        minx=self.size+titlewidth
        maxx=sw-(boxwidth-1)-self.size
        miny=boxwidth-1+self.size
        maxy=sh-self.size-boxwidth                  
        
        self.pos=(random.randint(minx,maxx),random.randint(miny,maxy))
        print self.pos
        self.image=Image.new('1',(self.size,self.size),0)
        ImageDraw.Draw(self.image).line([(3,0),(4,0),(2,1),(2,2),(1,3),(1,5),(0,5),(0,6),(1,7),(6,7),(7,6),(7,4),(6,5),(6,3),(4,2),(5,2),(3,5),(3,5)],fill=1)
        #shit
    
        
class Canvas:
    def __init__(self):
        self.image=Image.new('1',(sw,sh),0)
        self.canv=ImageDraw.Draw(self.image)
        self.score=00
        self.top=boxwidth 
        self.bottom=boxwidth
        self.left=titlewidth
        self.right=boxwidth
        
    def drawrange(self):
        self.clear(1)
        self.canv.rectangle([self.left,self.top-1,sw-self.right,sh-self.bottom],0)

    def drawscore(self):
        global score
        self.canv.text((1,10),str(score))

    def drawsnake(self,snake):
#        i=0 
        x=0
        y=0
        global gametime
        part=snake.head
        while part is not None :
                self.canv.bitmap(part.pos, part.image,1)
                part=part.next
#print gametime,snake.time
        disptime=3 if len(snake.words)<7 else 10 
        if gametime-snake.time<disptime :
            if snake.head.movdir==direction.Up and snake.head.movdir==direction.Down:
                x=12
            else:
                y=-12

            self.canv.text((snake.pos[0]+x,snake.pos[1]+y),snake.words,fill=1)

    def drawshits(self,shits):
        for a in shits:
            self.canv.bitmap(a.pos,a.image,1)
    
    def clear(self,fill=0):
        self.canv.rectangle([0,0,128,63],fill)
    
class snakepart:
    def __init__(self,mytype,pre=None,next=None):
        self.pre= pre if pre!=None  else None
        self.movdir=direction.Up
        self.next = next if next!=None else None
        self.image=self.buildpart(1,mytype)
        self.pos=(32,32)

        self.upimg=self.image
        self.hozimg=self.image.transpose(Image.ROTATE_90)
    def buildpart(self,size,part_type):
        part=Image.new('1', (6, 6),0)
        partdraw=ImageDraw.Draw(part)
        if part_type==HEAD:
            partdraw.line([(1,0),(4,0),(1,0),(1,2),(4,0),(4,2),(5,2),(5,5),(4,5),(0,5),(0,4),(0,2)],fill=1)
            #part=part.ranspose(Image.ROTATE_90)
        elif part_type==TAIL:
            partdraw.rectangle([2,0,3,5],fill=1)
# partdraw.rectangle([1,0,4,2],fill=1)
#partdraw.line([(2,0),(2,5),(3,0),(3,5)],fill=1)
# partdraw.line([(0,0),(0,0),(1,1),(1,3),(5,0),(5,0)],fill=1)
#            partdraw.rectangle([2,4,3,5],fill=1)
        else: 
            partdraw.rectangle([1,1,4,4],fill=1)
        return part
    def setupimage(self):
        self.image=self.upimg
    def sethozimage(self):
        self.image=self.hozimg
        
    def setpre(self,part):
        self.pre=part

    def setnext(self,part):
        self.next=part

    

    def getnext(self):
        return self.next

    def setpos(self,pos):
        self.pos=pos

    def setdirection(self,movdir):
        self.movdir=movdir

    def roate(self,xx):
        if xx not in (90,270):
            return
        d=Image.ROTATE_90
        
        if xx==90:#cw90
            d = Image.ROTATE_90
        else: 
            d = Image.ROTATE_270   
        self.image=self.image.transpose(d)
        

class snake:
    
    def __init__(self,snakelen=10,snakewidth=2):
        self.snakelen=snakelen
        self.snamkewidth=snakewidth
        self.words=""
        self.head=snakepart(HEAD)
        self.pos=(62,32)
        self.head.pos=self.pos
        self.time=0
        self.randwords=("shit!!!","love shit","hunary","sexy snake","need motor","fuck GFW","Indian SB","NomoneyNowifi","ww is coder","zuo&die","oled game","power shit","yes shit","chain","FKYOUSELF")
        part=self.head

        for i in range(5): 
            part.next=snakepart(BODY,pre=part)
            prepos=part.pos
            part=part.next
            part.setpos((prepos[0],prepos[1]+3))
            print "create ",i,"body " 
        prepos=part.pos
        part.next=snakepart(TAIL,pre=part)
        part.next.setpos((prepos[0],prepos[1]+3))
        self.tail=part.next
        print "create tail",part.next.pos 
        part=self.head
        i=0
        while part is not None :
            part=part.next
            if part is not None: print part.pos
            i +=1
        print i

    
    def setposdir(self,pos,movdir):
        self.pos=pos
        prepos=self.head.pos
        predir=self.head.movdir
        self.head.setpos(pos)
        self.head.setdirection(movdir)
        part=self.head.next
        while part is not  None:
            tmppos=part.pos
            tmpdir=part.movdir
            part.setpos(prepos)
            part.setdirection(predir)
            prepos=tmppos
            predir=tmpdir
            part=part.next
        if self.tail.movdir ==direction.Up or self.tail.movdir==direction.Down :
        
            self.tail.setupimage()
        else:
            self.tail.sethozimage()
    def appendpart(self):
        A=self.tail.pre
        part1=snakepart(BODY,pre=self.tail.pre,next=self.tail)
        self.tail.pre=part1
        
        part1.movedir=self.tail.movdir
        A.next=part1
        part1.setpos(self.tail.pos)
        
    def getdir(self):
        return self.head.direction
    def setdir(self,movdir):
        pass
    def snakesay(self,words,mytime):
        self.time=mytime
        self.words=words

def impactshit(snake,shits):
    x1=snake.head.pos[0]+2
    y1=snake.head.pos[1]+2
    global score
    i=0
    j=0
    for s in shits:
        x2=s.pos[0]+4
        y2=s.pos[1]+4
        ss=pow((x1-x2),2)+pow((y1-y2),2)
        if ss<16:
            score+=1
            del(shits[i])
            j=1
        i+=1
    return j

def checkimpactborder(snake):
    pass

score=0            
o=oled.OLED()
o.begin()
mysnake=snake()
cav=Canvas()
isrun=1
keydir=None
keythread=keyinput()
keythread.start()
shits=[]
i=0
gametime=0
while isrun:
    cav.drawrange()
    key=keythread.getkey()
#print key
    if key=='D':#left
        keydir=direction.Left
    elif key=='C':#right
        keydir=direction.Right
    elif key=='A':#UP
        keydir=direction.Up
    elif key=='B':#down
        keydir=direction.Down
    elif key== 'a':
        pass
    elif key== 'r':
        pass
    else:
        key=None
    CC=0
    if i%20==0 and len(shits)<8:
        
        print "product a shit"
        shits.append(shit())
    i+=1
    
    if mysnake.head.movdir==direction.Up:
        if keydir==direction.Left:
            CC=90
        elif keydir==direction.Right:
            CC=270
    elif mysnake.head.movdir==direction.Left:
        if keydir==direction.Up:
            CC=270
        elif keydir==direction.Down:
            CC=90
    elif mysnake.head.movdir==direction.Down:
        if keydir==direction.Left:
            CC=270
        elif keydir==direction.Right:
            CC=90
    elif mysnake.head.movdir==direction.Right:
        if keydir==direction.Down:
            CC=270
        elif keydir==direction.Up:
            CC=90
#print CC
    if score>=2:
        score=0
        mysnake.appendpart()
       
    mysnake.head.roate(CC)
    if keydir == None or keydir==~mysnake.head.movdir:
        godir=mysnake.head.movdir
    else:
        godir=keydir
    if godir==direction.Left:
        mysnake.setposdir((mysnake.pos[0]-3,mysnake.pos[1]),godir)
    elif godir==direction.Right:
        mysnake.setposdir((mysnake.pos[0]+3,mysnake.pos[1]),godir)
    elif godir==direction.Down:
        mysnake.setposdir((mysnake.pos[0],mysnake.pos[1]+3),godir)
    elif godir==direction.Up:
        mysnake.setposdir((mysnake.pos[0],mysnake.pos[1]-3),godir)
    
    
#if godir is not None:     
#        mysnake.head.setdirection(godir)
        
    if impactshit(mysnake,shits)>0:
        mysnake.snakesay("Woo",gametime)
    x=random.randint(0,len(mysnake.randwords)-1) 
    if gametime-mysnake.time>40:
        mysnake.snakesay(mysnake.randwords[x],gametime)

    checkimpactborder(mysnake)
#print "mian loop"
    cav.drawscore()
    cav.drawsnake(mysnake)
    cav.drawshits(shits)
    o.image(cav.image)
    o.display()
    time.sleep(0.1)
    gametime+=1
