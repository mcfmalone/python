#!/usr/bin/python

import matplotlib.pyplot as plt
import numpy as np
import argparse
import sys
import os

class DynoRun(object):
    def __init__(self,f,g):
        self.s,self.w,self.p,self.t=np.loadtxt(f,unpack=True)
        self.w*=1000
        self.gr=np.loadtxt(g)
        self.circumference=None
    def Tire(self,mm,aspect,rim):
        self.mm=mm
        self.aspect=aspect
        self.rim=rim
        self.diameter=self.rim/63360.0 + self.mm*self.aspect*6.2137119223733E-9
        self.circumference=3.14159265359*self.diameter
    def RedLine(self,redline=None):
        self.redline=redline
    def Weight(self,weight=None):
        self.weight=weight
    def plot(self,order=None,ImgFilename=None):
        fig=plt.figure(figsize=(16,9))
        plt.style.use("grace")
        plt.plot(self.w,self.t,label="lb-ft",color="black")
        plt.plot(self.w,self.p,label="hp",color="red")
        if(order is not None):
            torq=np.poly1d(np.polyfit(self.w,self.t,int(order),rcond=1e-20))
            if(self.redline is not None):
                w=np.arange(self.w[0],self.redline,1)
                t=torq(w)
            else:
                w=self.w
                t=torq(self.w)
            plt.plot(w,t,color="black")
            plt.plot(w,t*w/5252,color="red")
        plt.grid()
        plt.legend()
        if(ImgFilename is not None):
            fig.savefig(ImgFilename,dpi=300,bbox_inches="tight")
        plt.show()

    def plotgears(self,order=None,ImgFilename=None):
        fig=plt.figure(figsize=(16,9))
        plt.style.use("grace")
        plt.ylabel("Rear wheel torque (lb-ft)")
        plt.xlabel("Rear wheel speed (rpm)")
        if(order is None):
            w1=self.rpm(1)
            t1=self.lbft(1)
            w2=self.rpm(2)
            t2=self.lbft(2)
            w3=self.rpm(3)
            t3=self.lbft(3)
            w4=self.rpm(4)
            t4=self.lbft(4)
            w5=self.rpm(5)
            t5=self.lbft(5)
            w6=self.rpm(6)
            t6=self.lbft(6)
            w7=self.rpm(7)
            t7=self.lbft(7)
        else:
            torq=np.poly1d(np.polyfit(self.w,self.t,int(order),rcond=1e-20))
            if(self.redline is not None):
                w=np.arange(self.w[0],self.redline,1)
            else:
                w=self.w
            t=torq(w)
            w1=w/self.gr[1][1]/self.gr[0][1]
            t1=t*self.gr[1][1]*self.gr[0][1]
            w2=w/self.gr[2][1]/self.gr[0][1]
            t2=t*self.gr[2][1]*self.gr[0][1]
            w3=w/self.gr[3][1]/self.gr[0][1]
            t3=t*self.gr[3][1]*self.gr[0][1]
            w4=w/self.gr[4][1]/self.gr[0][1]
            t4=t*self.gr[4][1]*self.gr[0][1]
            w5=w/self.gr[5][1]/self.gr[0][1]
            t5=t*self.gr[5][1]*self.gr[0][1]
            w6=w/self.gr[6][1]/self.gr[0][1]
            t6=t*self.gr[6][1]*self.gr[0][1]
            w7=w/self.gr[7][1]/self.gr[0][1]
            t7=t*self.gr[7][1]*self.gr[0][1]
        wi1,ti1=self.intersection(w1,t1,w2,t2)
        wi2,ti2=self.intersection(w2,t2,w3,t3)
        wi3,ti3=self.intersection(w3,t3,w4,t4)
        wi4,ti4=self.intersection(w4,t4,w5,t5)
        wi5,ti5=self.intersection(w5,t5,w6,t6)
        wi6,ti6=self.intersection(w6,t6,w7,t7)
        if(self.circumference is not None):
            w1=w1*60*self.circumference
            w2=w2*60*self.circumference
            w3=w3*60*self.circumference
            w4=w4*60*self.circumference
            w5=w5*60*self.circumference
            w6=w6*60*self.circumference
            w7=w7*60*self.circumference
            plt.xlabel("Vehicle speed (mph)")
        plt.plot(w1,t1,label="1:"+str(int(wi1*self.gr[1][1]*self.gr[0][1])))
        plt.plot(w2,t2,label="2:"+str(int(wi2*self.gr[2][1]*self.gr[0][1])))
        plt.plot(w3,t3,label="3:"+str(int(wi3*self.gr[3][1]*self.gr[0][1])))
        plt.plot(w4,t4,label="4:"+str(int(wi4*self.gr[4][1]*self.gr[0][1])))
        plt.plot(w5,t5,label="5:"+str(int(wi5*self.gr[5][1]*self.gr[0][1])))
        plt.plot(w6,t6,label="6:"+str(int(wi6*self.gr[6][1]*self.gr[0][1])))
        plt.plot(w7,t7,label="7")
        plt.grid()
        plt.legend()
        if(ImgFilename is not None):
            bname,extension=os.path.splitext(ImgFilename)
            ImgFilename=bname+"_gears"+extension
            fig.savefig(ImgFilename,dpi=300,bbox_inches="tight")
        plt.show()
    def lbft(self,gear):
        ratio=self.gr[gear][1]*self.gr[0][1]
        return self.t*ratio
    def rpm(self,gear):
        ratio=self.gr[gear][1]*self.gr[0][1]
        return self.w/ratio

    def _rect_inter_inner(self,x1,x2):
        n1=x1.shape[0]-1
        n2=x2.shape[0]-1
        X1=np.c_[x1[:-1],x1[1:]]
        X2=np.c_[x2[:-1],x2[1:]]    
        S1=np.tile(X1.min(axis=1),(n2,1)).T
        S2=np.tile(X2.max(axis=1),(n1,1))
        S3=np.tile(X1.max(axis=1),(n2,1)).T
        S4=np.tile(X2.min(axis=1),(n1,1))
        return S1,S2,S3,S4

    def _rectangle_intersection_(self,x1,y1,x2,y2):
        S1,S2,S3,S4=self._rect_inter_inner(x1,x2)
        S5,S6,S7,S8=self._rect_inter_inner(y1,y2)

        C1=np.less_equal(S1,S2)
        C2=np.greater_equal(S3,S4)
        C3=np.less_equal(S5,S6)
        C4=np.greater_equal(S7,S8)

        ii,jj=np.nonzero(C1 & C2 & C3 & C4)
        return ii,jj

    def intersection(self,x1,y1,x2,y2):
        ii,jj=self._rectangle_intersection_(x1,y1,x2,y2)
        n=len(ii)

        dxy1=np.diff(np.c_[x1,y1],axis=0)
        dxy2=np.diff(np.c_[x2,y2],axis=0)

        T=np.zeros((4,n))
        AA=np.zeros((4,4,n))
        AA[0:2,2,:]=-1
        AA[2:4,3,:]=-1
        AA[0::2,0,:]=dxy1[ii,:].T
        AA[1::2,1,:]=dxy2[jj,:].T

        BB=np.zeros((4,n))
        BB[0,:]=-x1[ii].ravel()
        BB[1,:]=-x2[jj].ravel()
        BB[2,:]=-y1[ii].ravel()
        BB[3,:]=-y2[jj].ravel()

        for i in range(n):
            try:
                T[:,i]=np.linalg.solve(AA[:,:,i],BB[:,i])
            except:
                T[:,i]=np.NaN


        in_range= (T[0,:] >=0) & (T[1,:] >=0) & (T[0,:] <=1) & (T[1,:] <=1)

        xy0=T[2:,in_range]
        xy0=xy0.T
        return xy0[:,0],xy0[:,1]


#            plt.plot(self.rpm(self.gr[1][1]*self.gr[0][1]),self.p,label="1")
#            plt.plot(self.rpm(self.gr[2][1]*self.gr[0][1]),self.p,label="2")
#            plt.plot(self.rpm(self.gr[3][1]*self.gr[0][1]),self.p,label="3")
#            plt.plot(self.rpm(self.gr[4][1]*self.gr[0][1]),self.p,label="4")
#            plt.plot(self.rpm(self.gr[5][1]*self.gr[0][1]),self.p,label="5")
#            plt.plot(self.rpm(self.gr[6][1]*self.gr[0][1]),self.p,label="6")
#            plt.plot(self.rpm(self.gr[7][1]*self.gr[0][1]),self.p,label="7")
    

def MainMenu(argv):
    parser=argparse.ArgumentParser(description="Dyno",prog=sys.argv[0])
    parser.add_argument("InFile",help="Input file.",type=argparse.FileType('r'),metavar="str",default=sys.stdin)
    parser.add_argument("-a",help="Aspect ratio.",type=int,metavar="int",dest="aspect")
    parser.add_argument("-g",help="Gear ratio file.",type=argparse.FileType('r'),metavar="str",dest="grFile")
    parser.add_argument("-m",help="Rim size (inches).",type=int,metavar="int",dest="rim")
    parser.add_argument("-o",help="Order of polynomial to fit data.",type=int,metavar="int",dest="order")
    parser.add_argument("-p",help="Pounds, gross weight.",type=int,metavar="int",dest="weight")
    parser.add_argument("-r",help="Redline RPM.",type=int,metavar="int",dest="redline")
    parser.add_argument("-s",help="Save image file.",type=str,metavar="str",dest="ImgFilename")
    parser.add_argument("-v",help="Verbose. Intended for debugging.",action="store_true",dest="Verbose",default=False)
    parser.add_argument("-w",help="Width, tire (mm).",type=int,metavar="int",dest="width")
    parser._actions[0].help="Show help message and exit."
    if(len(argv)==0):
        args=parser.parse_args(["-h"])
    else:
        args=parser.parse_args()
        if(args.Verbose):
            for i in vars(args):
                print("%s=%s"%(i,getattr(args,i)))
    return args

def main(argv):
    args=MainMenu(argv)
    DR=DynoRun(args.InFile,args.grFile)
    if(args.order>0):
        o=args.order
    else:
        o=None
    if(args.redline):
        r=args.redline
    else:
        r=None
    if(args.width and args.aspect and args.rim):
        DR.Tire(args.width,args.aspect,args.rim)
    DR.RedLine(r)
    DR.plot(o,args.ImgFilename)
    DR.plotgears(o,args.ImgFilename)

if __name__=="__main__":
    main(sys.argv[1:])
