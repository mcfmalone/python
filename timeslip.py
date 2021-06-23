#!/usr/bin/python3
# $Id:$
# $Author:$
# $Revision:$
# $Log:$
#

import sys
import os
import numpy as np
import argparse
from cmd import Cmd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import csv

class Timeslip(object):
    def __init__(self,l):
        self.d=l[0]
        self.l=l[1]
        self.c=l[2]
        self.n=l[3]
        self.w=int(l[4])
        self.rt=float(l[5])
        self.t60=float(l[6])
        self.t330=float(l[7])
        self.t660=float(l[8])
        self.v660=float(l[9])
        self.t594=self.t660-45/self.v660
        self.t1000=float(l[10])
        self.t1320=float(l[11])
        self.v1320=float(l[12])
        self.t1254=self.t1320-45/self.v1320
        self.t=np.linspace(0,self.t1320,self.t1320*1000+1)

        # Time points (seconds)
        self.tp=np.array([0,self.t60,self.t330,self.t594,self.t660,self.t1000,self.t1254,self.t1320])

        # Positon points (feet)
        self.xp=np.array([0,60,330,594,660,1000,1254,1320])

        # Velocity points (mph)
        self.vp=np.array([self.v660,self.v1320])
        self.xoft=np.poly1d(np.polyfit(self.tp,self.xp,5,rcond=1e-20))
        print(self.xoft)
        self.x=self.xoft(self.t)
        self.voft=np.polyder(self.xoft)
        self.v=self.voft(self.t)    # This is ft/s. To get mph, multpily by 15.0/22.0
        self.aoft=np.polyder(self.xoft,2)
        self.a=self.aoft(self.t)    # This is ft/s^2. To get g, divide by 32.174
        self.P=self.w*self.a*self.v*5.65107724143E-05
    def file(self,f=None):
        self.t,self.x,self.v,self.mph,self.a,self.P,self.Pg=np.loadtxt(f,unpack=True)
        self.a=self.a*31.174
    def show(self):
        print("Date\t%s"%self.d)
        print("R/T\t%5.3f"%self.rt)
        print("60\t%6.3f"%self.t60)
        print("330\t%6.3f"%self.t330)
        print("594\t%6.3f"%self.t594)
        print("660\t%6.3f @ %5.2f"%(self.t660,self.v660))
        print("1000\t%6.3f"%self.t1000)
        print("1254\t%6.3f"%self.t1254)
        print("1320\t%6.3f @ %5.2f"%(self.t1320,self.v1320))
    def x_vs_t(self,T=None):
        plt.style.use("grace")
        fig=plt.figure()
        plt.plot(self.t,self.x,linewidth=1.0,color="black",label="%s: %s \#%s"%(self.l,self.c,self.n))
        if(T is not None):
            plt.plot(T.t,T.x,linewidth=1.0,color="red",label="%s: %s \#%s"%(T.l,T.c,T.n))
#            plt.plot(T.tp,T.xp,'ko')
        else:
            plt.plot(self.tp,self.xp,'ko')
            for i,txt in enumerate(self.tp):
                plt.annotate(txt,(self.tp[i]+0.1,self.xp[i]-5.0))
        plt.title("Distance vs. Time")
        plt.legend()
        plt.ylim(0,1320)
        plt.xlabel("s")
        plt.ylabel("ft")
        plt.grid()
        plt.show()
    def xvst(self,T=None,RT=True):
#        plt.style.use("grace")
        fig,ax0=plt.subplots(figsize=(16.0,9.0))
        ax0.set_xlabel("%s lane clock (s)\nreaction time %6.3f"%(self.l,self.rt),color="red")
        ax0.set_ylabel("distance (ft)")
        ax0.plot(self.tp[1:],self.xp[1:],'ko',label="Timeslip data")
        ax0.plot(self.t,self.x,color="red",label="Car #%s: %s"%(self.n,self.c))
        ax0.tick_params(axis='x',labelcolor="red")
        ax0.xaxis.set_major_locator(ticker.MultipleLocator(1))
        ax0.xaxis.set_minor_locator(ticker.MultipleLocator(0.1))
        ax0.yaxis.set_major_locator(ticker.MultipleLocator(100))
        ax0.yaxis.set_minor_locator(ticker.MultipleLocator(10))
        ax0.set_ylim(0,1350)
        if(T is not None):
            maxT=max(self.t1320,T.t1320)
            if(RT is False):
                dt0=0
            else:
                dt0=self.rt-T.rt
            dt1320=T.t1320-self.t1320
            ax1=ax0.twiny()
            ax1.set_xlabel("%s lane clock (s)\nreaction time %6.3f"%(T.l,T.rt),color="blue")
            ax1.plot(T.t,T.x,color="blue",label="Car #%s: %s"%(T.n,T.c))
            ax1.plot(T.tp[1:],T.xp[1:],'ko')
            ax1.tick_params(axis='x',labelcolor="blue")
            ax1.xaxis.set_major_locator(ticker.MultipleLocator(1))
            ax1.xaxis.set_minor_locator(ticker.MultipleLocator(0.1))
            ax1.yaxis.set_major_locator(ticker.MultipleLocator(100))
            ax1.yaxis.set_minor_locator(ticker.MultipleLocator(10))
            ax0.set_xlim(0-max(0,dt0),maxT-min(0,dt0))
            ax1.set_xlim(0+min(0,dt0),maxT+max(0,dt0))
            ax1.grid(which="major")
        fig.legend(bbox_to_anchor=(0.13,0.87),loc=2)
#        fig.legend(loc=2)
#        fig.subplots_adjust(top=0.88)
#        fig.tight_layout()
#        fig.suptitle("Distance vs. Time")
        if(RT is True):
            fn="%s x_vs_t timeshifted.png"
        else:
            fn="%s x_vs_t.png"
        ax0.grid(which="major")
        fig.savefig(fn%(self.l),dpi=300)
        plt.show()
    def v_vs_t(self,T=None,RT=True):
        tp0=np.array([self.t660,self.t1320])
        fig=plt.figure()
        fig,ax0=plt.subplots(figsize=(16.0,9.0))
        ax0.set_xlabel("%s lane clock (s)\nreaction time %6.3f"%(self.l,self.rt),color="red")
        ax0.set_ylabel("velocity (mph)")
        ax0.plot(tp0,self.vp,'ko',label="Timeslip data")
        ax0.plot(self.t,self.v*15.0/22.0,color="red",label="Car #%s: %s"%(self.n,self.c))
        ax0.tick_params(axis='x',labelcolor="red")
        ax0.xaxis.set_major_locator(ticker.MultipleLocator(1))
        ax0.xaxis.set_minor_locator(ticker.MultipleLocator(0.1))
        ax0.yaxis.set_major_locator(ticker.MultipleLocator(10))
        ax0.yaxis.set_minor_locator(ticker.MultipleLocator(1))
        if(T is not None):
            maxT=max(self.t1320,T.t1320)
            if(RT is True):
                dt0=self.rt-T.rt
            else:
                dt0=0
            dt1320=T.t1320-self.t1320
            ax0.set_ylim(0,max(self.v1320,T.v1320)+5)
            ax1=ax0.twiny()
            ax1.set_xlabel("%s lane clock (s)\nreaction time %6.3f"%(T.l,T.rt),color="blue")
            ax1.plot(T.t,T.v*15.0/22.0,color="blue",label="Car #%s: %s"%(T.n,T.c))
            tp1=np.array([T.t660,T.t1320])
            ax1.plot(tp1,T.vp,'ko')
            ax1.tick_params(axis='x',labelcolor="blue")
            ax1.xaxis.set_major_locator(ticker.MultipleLocator(1))
            ax1.xaxis.set_minor_locator(ticker.MultipleLocator(0.1))
            ax1.yaxis.set_major_locator(ticker.MultipleLocator(10))
            ax1.yaxis.set_minor_locator(ticker.MultipleLocator(1))
            ax0.set_xlim(0-max(0,dt0),maxT-min(0,dt0))
            ax1.set_xlim(0+min(0,dt0),maxT+max(0,dt0))
            ax1.grid(which="major")
        fig.legend(bbox_to_anchor=(0.13,0.87),loc=2)
#            for i,txt in enumerate(self.vp):
#                plt.annotate(txt,(tp[i]+0.1,self.vp[i]-5.0))
#        plt.title("Velocity vs. Time")
#        plt.legend()
#        fig.suptitle("Velocity vs. Time")
        if(RT is True):
            fn="%s v_vs_t timeshifted.png"
        else:
            fn="%s v_vs_t.png"
        ax0.grid(which="major")
        fig.savefig(fn%(self.l),dpi=300)
        plt.show()
    def v_vs_x(self,T=None):
        fig=plt.figure()
        fig,ax0=plt.subplots(figsize=(16.0,9.0))
        ax0.set_xlabel("%s lane distance (ft)"%self.l,color="red")
        ax0.set_ylabel("velocity (mph)")
        xp=np.array([660,1320])
        ax0.plot(xp,self.vp,'ko',label="Timeslip data")
        ax0.plot(self.x,self.v*15.0/22.0,color="red",label="Car #%s: %s"%(self.n,self.c))
        ax0.tick_params(axis='x',labelcolor="red")
        ax0.xaxis.set_major_locator(ticker.MultipleLocator(100))
        ax0.xaxis.set_minor_locator(ticker.MultipleLocator(10))
        ax0.yaxis.set_major_locator(ticker.MultipleLocator(10))
        ax0.yaxis.set_minor_locator(ticker.MultipleLocator(1))
        ax0.grid(which="major")
        if(T is not None):
            ax0.set_ylim(0,max(self.v1320,T.v1320)+5)
            ax1=ax0.twiny()
            ax1.set_xlabel("%s lane distance (ft)"%T.l,color="blue")
            ax1.plot(T.x,T.v*15.0/22.0,color="blue",label="Car #%s: %s"%(T.n,T.c))
            ax1.plot(xp,T.vp,'ko')
            ax1.tick_params(axis='x',labelcolor="blue")
            ax1.xaxis.set_major_locator(ticker.MultipleLocator(100))
            ax1.xaxis.set_minor_locator(ticker.MultipleLocator(10))
            ax1.yaxis.set_major_locator(ticker.MultipleLocator(10))
            ax1.yaxis.set_minor_locator(ticker.MultipleLocator(1))
            ax0.set_xlim(0,1320)
            ax1.set_xlim(0,1320)
            ax1.grid(which="major")
        fig.legend(bbox_to_anchor=(0.13,0.87),loc=2)
#        for i,txt in enumerate(self.vp):
#            plt.annotate(txt,(xp[i]+0.1,self.vp[i]-5.0))
#        plt.title("Velocity vs. Distance")
        fig.legend(bbox_to_anchor=(0.13,0.87),loc=2)
        fn="%s v_vs_x.png"
        fig.savefig(fn%(self.l),dpi=300)
        plt.show()
    def a_vs_t(self,T=None,RT=True):
        fig=plt.figure()
        fig,ax0=plt.subplots(figsize=(16.0,9.0))
        ax0.set_xlabel("%s lane clock (s)\nreaction time %6.3f"%(self.l,self.rt),color="red")
        ax0.set_ylabel("acceleration (g)")
        ax0.plot(self.t,self.a/32.174,color="red",label="Car #%s: %s"%(self.n,self.c))
        ax0.tick_params(axis='x',labelcolor="red")
        ax0.xaxis.set_major_locator(ticker.MultipleLocator(1))
        ax0.xaxis.set_minor_locator(ticker.MultipleLocator(0.1))
        ax0.yaxis.set_major_locator(ticker.MultipleLocator(.1))
        ax0.yaxis.set_minor_locator(ticker.MultipleLocator(.01))
        ax0.set_ylim(0,1)
        ax0.grid(which="major")
        if(T is not None):
            maxT=max(self.t1320,T.t1320)
            if(RT is True):
                dt0=self.rt-T.rt
            else:
                dt0=0
            dt1320=T.t1320-self.t1320
            ax1=ax0.twiny()
            ax1.set_xlabel("%s lane clock (s)\nreaction time %6.3f"%(T.l,T.rt),color="blue")
            ax1.plot(T.t,T.a/32.174,color="blue",label="Car #%s: %s"%(T.n,T.c))
            ax1.tick_params(axis='x',labelcolor="blue")
            ax1.xaxis.set_major_locator(ticker.MultipleLocator(1))
            ax1.xaxis.set_minor_locator(ticker.MultipleLocator(0.1))
            ax1.yaxis.set_major_locator(ticker.MultipleLocator(.1))
            ax1.yaxis.set_minor_locator(ticker.MultipleLocator(.01))
            ax0.set_xlim(0-max(0,dt0),maxT-min(0,dt0))
            ax1.set_xlim(0+min(0,dt0),maxT+max(0,dt0))
            ax1.grid(which="major")
        fig.legend(bbox_to_anchor=(0.13,0.87),loc=2)
        if(RT is True):
            fn="%s a_vs_t timeshifted.png"
        else:
            fn="%s a_vs_t.png"
        fig.savefig(fn%(self.l),dpi=300)
        plt.show()
    def a_vs_x(self,T=None):
        fig=plt.figure()
        fig,ax0=plt.subplots(figsize=(16.0,9.0))
        ax0.set_xlabel("%s lane distance (ft)"%(self.l),color="red")
        ax0.set_ylabel("acceleration (g)")
        ax0.plot(self.x,self.a/32.174,color="red",label="Car #%s: %s"%(self.n,self.c))
        ax0.tick_params(axis='x',labelcolor="red")
        ax0.xaxis.set_major_locator(ticker.MultipleLocator(100))
        ax0.xaxis.set_minor_locator(ticker.MultipleLocator(10))
        ax0.yaxis.set_major_locator(ticker.MultipleLocator(.1))
        ax0.yaxis.set_minor_locator(ticker.MultipleLocator(.01))
        ax0.set_ylim(0,1)
        ax0.grid(which="major")
        if(T is not None):
            ax1=ax0.twiny()
            ax1.set_xlabel("%s lane distance (ft)"%T.l,color="blue")
            ax1.plot(T.x,T.a/32.174,color="blue",label="Car #%s: %s"%(T.n,T.c))
            ax1.tick_params(axis='x',labelcolor="blue")
            ax1.xaxis.set_major_locator(ticker.MultipleLocator(100))
            ax1.xaxis.set_minor_locator(ticker.MultipleLocator(10))
            ax1.yaxis.set_major_locator(ticker.MultipleLocator(.1))
            ax1.yaxis.set_minor_locator(ticker.MultipleLocator(.01))
            ax1.grid(which="major")
        fig.legend(bbox_to_anchor=(0.13,0.87),loc=2)
        fn="%s a_vs_x.png"
        fig.savefig(fn%(self.l),dpi=300)
        plt.show()
    def a_vs_v(self,T=None):
        fig=plt.figure()
        maxV0=max(self.v)*15.0/22.0
        fig,ax0=plt.subplots(figsize=(16.0,9.0))
        ax0.set_xlabel("%s lane velocity (mph)"%(self.l),color="red")
        ax0.set_ylabel("acceleration (g)")
        ax0.plot(self.v*15.0/22.0,self.a/32.174,color="red",label="Car #%s: %s"%(self.n,self.c))
        ax0.tick_params(axis='x',labelcolor="red")
        ax0.xaxis.set_major_locator(ticker.MultipleLocator(10))
        ax0.xaxis.set_minor_locator(ticker.MultipleLocator(1))
        ax0.yaxis.set_major_locator(ticker.MultipleLocator(.1))
        ax0.yaxis.set_minor_locator(ticker.MultipleLocator(.01))
        ax0.set_ylim(0,1)
        ax0.grid(which="major")
        if(T is not None):
            maxV1=max(T.v)*15.0/22.0
            ax1=ax0.twiny()
            ax1.set_xlabel("%s lane velocity (mph)"%T.l,color="blue")
            ax1.plot(T.v*15.0/22.0,T.a/32.174,color="blue",label="Car #%s: %s"%(T.n,T.c))
            ax1.tick_params(axis='x',labelcolor="blue")
            ax1.xaxis.set_major_locator(ticker.MultipleLocator(10))
            ax1.xaxis.set_minor_locator(ticker.MultipleLocator(1))
            ax1.yaxis.set_major_locator(ticker.MultipleLocator(.1))
            ax1.yaxis.set_minor_locator(ticker.MultipleLocator(.01))
            ax1.grid(which="major")
            ax0.set_xlim(0,max(maxV0,maxV1))
            ax1.set_xlim(0,max(maxV0,maxV1))
        fig.legend(bbox_to_anchor=(0.13,0.87),loc=2)
        fn="%s a_vs_v.png"
        fig.savefig(fn%(self.l),dpi=300)
        plt.show()
    def P_vs_t(self,T=None,RT=True):
        maxP0=max(self.P)
        fig=plt.figure()
        fig,ax0=plt.subplots(figsize=(16.0,9.0))
        ax0.set_xlabel("%s lane clock (s)\nreaction time %6.3f"%(self.l,self.rt),color="red")
        ax0.set_ylabel("power (net hp)")
        ax0.plot(self.t,self.P,color="red",label="Car #%s: %s"%(self.n,self.c))
        ax0.tick_params(axis='x',labelcolor="red")
        ax0.xaxis.set_major_locator(ticker.MultipleLocator(1))
        ax0.xaxis.set_minor_locator(ticker.MultipleLocator(0.1))
        ax0.yaxis.set_major_locator(ticker.MultipleLocator(10))
        ax0.yaxis.set_minor_locator(ticker.MultipleLocator(1))
        ax0.grid(which="major")
        if(T is not None):
            maxP1=max(T.P)
            maxT=max(self.t1320,T.t1320)
            if(RT is True):
                dt0=self.rt-T.rt
            else:
                dt0=0
            dt1320=T.t1320-self.t1320
            ax1=ax0.twiny()
            ax1.set_xlabel("%s lane clock (s)\nreaction time %6.3f"%(T.l,T.rt),color="blue")
            ax1.plot(T.t,T.P,color="blue",label="Car #%s: %s"%(T.n,T.c))
            ax1.tick_params(axis='x',labelcolor="blue")
            ax1.xaxis.set_major_locator(ticker.MultipleLocator(1))
            ax1.xaxis.set_minor_locator(ticker.MultipleLocator(0.1))
            ax1.yaxis.set_major_locator(ticker.MultipleLocator(10))
            ax1.yaxis.set_minor_locator(ticker.MultipleLocator(1))
            ax0.set_xlim(0-max(0,dt0),maxT-min(0,dt0))
            ax1.set_xlim(0+min(0,dt0),maxT+max(0,dt0))
            ax1.grid(which="major")
            ax0.set_ylim(0,max(maxP0,maxP1)+10)
        fig.legend(bbox_to_anchor=(0.2,0.2),loc=2)
        if(RT is True):
            fn="%s p_vs_t timeshifted.png"
        else:
            fn="%s p_vs_t.png"
        fig.savefig(fn%(self.l),dpi=300)
        plt.show()
    def P_vs_x(self,T=None):
        maxP0=max(self.P)
        fig=plt.figure()
        fig,ax0=plt.subplots(figsize=(16.0,9.0))
        ax0.set_xlabel("%s lane distance (ft)"%(self.l),color="red")
        ax0.set_ylabel("power (net hp)")
        ax0.plot(self.x,self.P,color="red",label="Car #%s: %s"%(self.n,self.c))
        ax0.tick_params(axis='x',labelcolor="red")
        ax0.xaxis.set_major_locator(ticker.MultipleLocator(100))
        ax0.xaxis.set_minor_locator(ticker.MultipleLocator(10))
        ax0.yaxis.set_major_locator(ticker.MultipleLocator(10))
        ax0.yaxis.set_minor_locator(ticker.MultipleLocator(1))
        ax0.grid(which="major")
        ax0.set_xlim(0,1320)
        if(T is not None):
            maxP1=max(T.P)
            ax1=ax0.twiny()
            ax1.set_xlabel("%s lane distance (ft)"%T.l,color="blue")
            ax1.plot(T.x,T.P,color="blue",label="Car #%s: %s"%(T.n,T.c))
            ax1.tick_params(axis='x',labelcolor="blue")
            ax1.xaxis.set_major_locator(ticker.MultipleLocator(100))
            ax1.xaxis.set_minor_locator(ticker.MultipleLocator(10))
            ax1.yaxis.set_major_locator(ticker.MultipleLocator(10))
            ax1.yaxis.set_minor_locator(ticker.MultipleLocator(1))
            ax1.grid(which="major")
            ax0.set_ylim(0,max(maxP0,maxP1)+10)
            ax1.set_xlim(0,1320)
        fig.legend(bbox_to_anchor=(0.2,0.2),loc=2)
        fn="%s p_vs_x.png"
        fig.savefig(fn%(self.l),dpi=300)
        plt.show()
    def P_vs_v(self,T=None):
        maxP0=max(self.P)
        maxV0=max(self.v)*15.0/22.0
        fig=plt.figure()
        fig,ax0=plt.subplots(figsize=(16.0,9.0))
        ax0.set_xlabel("%s lane velocity (mph)"%(self.l),color="red")
        ax0.set_ylabel("power (net hp)")
        ax0.plot(self.v*15.0/22.0,self.P,color="red",label="Car #%s: %s"%(self.n,self.c))
        ax0.tick_params(axis='x',labelcolor="red")
        ax0.xaxis.set_major_locator(ticker.MultipleLocator(10))
        ax0.xaxis.set_minor_locator(ticker.MultipleLocator(1))
        ax0.yaxis.set_major_locator(ticker.MultipleLocator(10))
        ax0.yaxis.set_minor_locator(ticker.MultipleLocator(1))
        ax0.grid(which="major")
        if(T is not None):
            maxP1=max(T.P)
            maxV1=max(T.v)*15.0/22.0
            ax1=ax0.twiny()
            ax1.set_xlabel("%s lane velocity (mph)"%T.l,color="blue")
            ax1.plot(T.v*15.0/22.0,T.P,color="blue",label="Car #%s: %s"%(T.n,T.c))
            ax1.tick_params(axis='x',labelcolor="blue")
            ax1.xaxis.set_major_locator(ticker.MultipleLocator(10))
            ax1.xaxis.set_minor_locator(ticker.MultipleLocator(1))
            ax1.yaxis.set_major_locator(ticker.MultipleLocator(10))
            ax1.yaxis.set_minor_locator(ticker.MultipleLocator(1))
            ax1.grid(which="major")
            ax0.set_xlim(0,max(maxV0,maxV1))
            ax1.set_xlim(0,max(maxV0,maxV1))
            ax0.set_ylim(0,max(maxP0,maxP1)+10)
        fig.legend(bbox_to_anchor=(0.2,0.2),loc=2)
        fn="%s p_vs_v.png"
        fig.savefig(fn%(self.l),dpi=300)
        plt.show()
    def P_vs_a(self):
        fig=plt.figure()
        plt.plot(self.a/32.174,self.P,linewidth=1.0,label="%s: %s #%s"%(self.l,self.c,self.n))
        plt.title("Power vs. Acceleration")
        plt.legend()
        plt.xlabel("g")
        plt.ylabel("hp")
        plt.grid()
        plt.show()

def Drag(T0,T1):
    fig=plt.figure()
    plt.plot(T0.t,T0.x,color="black",label="%s: %s #%s"%(T0.l,T0.c,T0.n))
    plt.plot(T1.t,T1.x,color="red",label="%s: %s #%s"%(T1.l,T1.c,T1.n))
    plt.title("Distance vs. Time")
    plt.legend()
    plt.xlabel("s")
    plt.ylabel("ft")
    plt.grid()
    plt.show()

def MainMenu(argv):
    parser=argparse.ArgumentParser(description="Timeslip.",prog=sys.argv[0])
    parser.add_argument("InFile",help="Input file containing timeslip data.",type=argparse.FileType('r'),metavar="filename",default=sys.stdin)
    parser.add_argument("-rt",help="Reaction time.",type=float,metavar="<float>",dest="rt")
    parser.add_argument("-t60",help="60' time.",type=float,metavar="<float>",dest="t60")
    parser.add_argument("-t330",help="330' time.",type=float,metavar="<float>",dest="t330")
    parser.add_argument("-t660",help="1/8-mile time.",type=float,metavar="<float>",dest="t660")
    parser.add_argument("-v660",help="1/8-mile mph.",type=float,metavar="<float>",dest="v660")
    parser.add_argument("-t1000",help="1000' time.",type=float,metavar="<float>",dest="t1000")
    parser.add_argument("-t1320",help="1/4-mile time.",type=float,metavar="<float>",dest="t1320")
    parser.add_argument("-v1320",help="1/4-mile mph.",type=float,metavar="<float>",dest="v1320")
    parser.add_argument("-f",help="File.",type=str,metavar="<str>",dest="f")
    parser.add_argument("-w",help="Weight (lbs).",type=int,metavar="<int>",dest="w")
    parser.add_argument("-v",help="Verbose. Intended for debugging.",action="store_true",dest="verbose",default=False)
    args=parser.parse_args(None if argv else ["-h"])
    if(args.verbose):
        for i in vars(args):
            print("%s=%s"%(i,getattr(args,i)))
    return args

def ReadFile(f):
    car0=[]
    car1=[]
    key=["Date","Lane","Car","Number","Weight","RT","t60","t330","t660","v660","t1000","t1320","v1320"]
    data=csv.reader(f)
    for n,line in enumerate(data):
        if(n==0):
            car0.append(line[0])
            car1.append(line[0])
        else:
            car0.append(line[0])
            if(len(line)>1):
                car1.append(line[1])
    if(len(car1)>1):
        return car0,car1
    else:
        return car0,None

def main(argv):
    args=MainMenu(argv)
    car0,car1=ReadFile(args.InFile)
#    print(car0,car1)
    T0=Timeslip(car0);
    if(car1 is not None):
        T1=Timeslip(car1);
    if(args.f):
        T0.file(args.f)
#    Drag(T0,T1)
    T0.xvst(RT=False)
#    T0.xvst()
#    T1.xvst(RT=False)
#    T1.xvst(T0)
    T0.v_vs_t(RT=False)
#    T0.v_vs_t()
#    T1.v_vs_t(T0,RT=False)
#    T1.v_vs_t(T0)
    T0.v_vs_x()
#    T1.v_vs_x(T0)
#    T0.a_vs_t()
    T0.a_vs_t(RT=False)
#    T1.a_vs_t(T0)
#    T1.a_vs_t(T0,RT=False)
    T0.a_vs_x()
#    T1.a_vs_x(T0)
    T0.a_vs_v()
#    T1.a_vs_v(T0)
#    T0.P_vs_t()
    T0.P_vs_t(RT=False)
#    T1.P_vs_t(T0)
#    T1.P_vs_t(T0,RT=False)
    T0.P_vs_x()
#    T1.P_vs_x(T0)
    T0.P_vs_v()
#    T1.P_vs_v(T0)

if __name__=="__main__":
    main(sys.argv[1:])
