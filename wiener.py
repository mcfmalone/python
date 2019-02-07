#!/usr/bin/python
# -*- coding: utf-8 -*-
# $Id:$
# $Author:$
# $Revision:$
# $Log:$

import sys
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import scipy as sp
import scipy.signal as signal
from scipy.signal import medfilt
from scipy import interpolate
import argparse

def GetXY(f):
    x,y=np.loadtxt(f,unpack=True)
    f.close()
    return x,y

def GetWspace(a):
    if(len(a.w)==0): wspace=[None]
    elif(len(a.w)==1): wspace=a.w
    elif(len(a.w)==2): wspace=range(a.w[0],a.w[1]+1)
    for i in wspace:
        if(i%2==0): wspace.remove(i)
    return wspace

def GetNspace(a):
    if(len(a.n)==0): nspace=[None]
    elif(len(a.n)==1): nspace=a.n
    elif(len(a.n)==2): nspace=np.arange(a.n[0],a.n[1]+a.dn,a.dn).tolist()
    return nspace

def PlotXY(x,y,yf,a):
    wspace=GetWspace(a)
    nspace=GetNspace(a)
    fig=plt.figure()
    fig.set_size_inches(16.0,9.0)
    plt.style.use("ggplot")
    if(a.Plot=="animated"):
        plt.ion()
    color=iter(cm.gist_rainbow(np.linspace(0,1,len(yf[0:]))))   #gist_rainbow seems to be the same as grace
    if(a.Plot=="input" or a.Plot=="both"):
        plt.plot(x,y,color="black",label=a.InFilename.name,linewidth=1)
    if(a.Plot=="output" or a.Plot=="both" or a.Plot=="animated"):
        labelstr=""
        i=0
        for w in wspace:
            wstr="w="+str(w)
            for n in nspace:
                labelstr=wstr+" n="+str(n)
                plt.minorticks_on()
                plt.grid(which="major",linestyle="-",linewidth="0.3")
                plt.grid(which="minor",linestyle="-",linewidth="0.1")
                plt.title("Wiener filter: "+'w='+str(a.w)+' n='+str(a.n))
                plt.legend()
                if(a.Plot=="animated"):
                    plt.plot(x,y,color="black",label=a.InFilename.name,linewidth=1)
                    plt.plot(x,yf[i],linewidth=1,label=labelstr,c="red")
                    plt.legend()
                    plt.show()
                    plt.pause(a.d)
                    fig.clear()
                else: plt.plot(x,yf[i],linewidth=1,label=labelstr,c=next(color))
                i+=1
    if(a.Plot!="animated"):
        plt.show()
    return fig

def SaveImage(x,y,yf,a):
    nspace=GetNspace(a)
    wspace=GetWspace(a)
    fig=plt.figure()
    fig.set_size_inches(16.0,9.0)
    plt.minorticks_on()
    plt.grid(which="major",linestyle="-",linewidth="0.3")
    plt.grid(which="minor",linestyle="-",linewidth="0.1")
    plt.title("Wiener filter: "+'size(w='+str(a.w)+') noise power (n='+str(a.n)+')')
    color=iter(cm.gist_rainbow(np.linspace(0,1,len(yf[0:]))))
    if(a.Plot=="input" or a.Plot=="both" or a.Plot=="animated"):
        plt.plot(x,y,color="black",label=a.InFilename.name,linewidth=1)
    if(a.Plot=="output" or a.Plot=="both" or a.Plot=="animated"):
        labelstr=""
        i=0
        for w in wspace:
            wstr="w="+str(w)
            for n in nspace:
                labelstr=wstr+" n="+str(n)
                plt.plot(x,yf[i],linewidth=1,label=labelstr,c=next(color))
                i+=1
    plt.legend()
    if(a.ImgFilename):
        fig.savefig(a.ImgFilename,dpi=fig.dpi)
    return fig

def Interpolate(x,y,a):
    minX=x[0]
    maxX=x[-1]
    nSamples=maxX-minX
    fs=round(1/np.ediff1d(x).min())
    fcubic=interpolate.interp1d(x,y,kind="cubic")
    xcubic=np.linspace(minX,maxX,nSamples*fs+1)
    ycubic=fcubic(xcubic)
    return xcubic,ycubic

# Assuming the wiener() function workes on a uniformly sampled set of data, 
# certain modifications are performed in this function to account for data
# which is not sampled uniformly. This function will find the number of 
# samples in the input data, find the smallest interval between adjacent
# data points, and call that the sampling frequency. Using that sampling
# frequency, it will then build a new data set using interpolation, such 
# that the entire set of data will them be uniformly sampled. The new data
# will be filtered with butter(). The new data set will then be interpolated
# and the resultant values returned at the original sample points.
def Wiener(x,y,a):
    wspace=GetWspace(a)
    nspace=GetNspace(a)
    yf=[]
    x_int,y_int=Interpolate(x,y,a)
    for w in wspace:
        for n in nspace:
            ywiener=signal.wiener(y_int,w,n)
            fwiener=interpolate.interp1d(x_int,ywiener,kind="cubic")
            yf.append(fwiener(x))
    return yf

def WienerMenu(argv):
    parser=argparse.ArgumentParser(prog=sys.argv[0],usage="%(prog)s [options]")
    parser.add_argument("-i",help="Input data file.",type=argparse.FileType('r'),metavar="<str>",dest="InFilename",default="/dev/stdin")
    parser.add_argument("-o",help="Output data file.",nargs='?',type=argparse.FileType('w'),metavar="str",dest="OutFilename",const="/dev/stdout",default="/dev/null")
    parser.add_argument("-s",help="Save image file.",type=str,metavar="<str>",dest="ImgFilename")
    parser.add_argument("-w",help="Size of the filter. A scaler giving the size of the Wiener filter window. Elements should be odd.",nargs="+",type=int,metavar="<int>",dest="w",default=[])
    parser.add_argument("-dw",help="Step size of w for animated plots.",type=float,metavar="<float>",dest="dw",default=1)
    parser.add_argument("-n",help="Noise-power to use. If none, then noise is estimated as the average of the local variance of the input.",nargs='+',type=float,metavar="float",dest="n",default=[])
    parser.add_argument("-dn",help="Step size of n for animated plots.",type=float,metavar="float",dest="dn",default=0.01)
    parser.add_argument("-p",help="Plot.",nargs='?',type=str,metavar="input|output|animated",choices=["input","output","animated","both","fr"],dest="Plot",const="both",default="")
    parser.add_argument("-d",help="Number of seconds to delay between plot updates. Default is 0.5",type=float,metavar="<float>",dest="d",default=0.5)
    parser.add_argument("-v",help="Verbose. Intended for debugging.",action="store_true",dest="Verbose",default=False)
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
    args=WienerMenu(argv)

    x,y=GetXY(args.InFilename)
    yf=Wiener(x,y,args)
    fig=PlotXY(x,y,yf,args)
    fig=SaveImage(x,y,yf,args)
    return 0

if __name__=="__main__":
    main(sys.argv[1:])
