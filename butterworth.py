#!/usr/bin/python
# -*- coding: utf-8 -*-
# $Id: butterworth.py,v 1.2 2019/02/03 16:33:22 micha Exp micha $
# $Author: micha $
# $Revision: 1.2 $
# $Log: butterworth.py,v $
# Revision 1.2  2019/02/03 16:33:22  micha
# Rewrote most of the code.
#

import sys
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import scipy as sp
import scipy.signal as signal
from scipy.signal import medfilt
from scipy import interpolate
import argparse

def GetXY(f):   # Returns two numpy arrays from a given data file.
    x,y=np.loadtxt(f,unpack=True)
    f.close()
    return x,y

def PlotFrequencyResponse(N,Wn,Btype,Analog):
    b,a=signal.butter(N,Wn,btype=Btype,analog=Analog)
    w,h=signal.freqs(b,a)
    fig=plt.figure()
    fig.set_size_inches(16,9)
    plt.semilogx(w,20*np.log10(abs(h)))
    plt.title("Butterworth Filter Frequency Response, N="+str(N)+", Wn="+str(Wn))
    if(Analog):
        plt.xlabel("rad/s")
    else:
        plt.xlabel("Normalized frequency")
    plt.ylabel("dB")
    plt.margins(0,0.1)
    plt.grid(which="both",axis="both")
    if(len(Wn)>1):
        plt.axvline(Wn[0],color="red")
        plt.axvline(Wn[1],color="red")
    else:
        plt.axvline(Wn,color="red")
    plt.show()
    return fig

def PlotXY(x,y,yf,a):
    wspace=GetWspace(a)
    nspace=GetNspace(a)
    fig=plt.figure()
    fig.set_size_inches(16.0,9.0)
    plt.style.use("ggplot")
    if(a.Plot=="animated"):
        plt.ion()
    color=iter(cm.gist_rainbow(np.linspace(0,1,len(yf[0:]))))   #gist_rainbow seems to be the same as grace
    plt.title("Butterworth filter: "+'order(N='+str(a.N)+') critical freq. (Wn='+str(a.Wn)+')')
    if(a.Plot=="input" or a.Plot=="both"):
        plt.plot(x,y,color="black",label=a.InFilename.name,linewidth=1)
    if(a.Plot=="output" or a.Plot=="both" or a.Plot=="animated"):
        labelstr=""
        i=0
        for N in nspace:
            nstr="N="+str(N)
            for Wn in wspace:
                labelstr=nstr+" Wn="+str(Wn)
                plt.minorticks_on()
                plt.grid(which="major",linestyle="-",linewidth="0.3")
                plt.grid(which="minor",linestyle="-",linewidth="0.1")
                if(a.Plot=="animated"):
                    plt.title("Butterworth filter: "+'order(N='+str(N)+') critical freq. (Wn='+str(Wn)+')')
                    plt.plot(x,y,color="black",label=a.InFilename.name,linewidth=1)
                    plt.plot(x,yf[i],linewidth=1,label=labelstr,c="red")
                    plt.legend()
                    plt.show()
                    plt.pause(a.d)
                    fig.clear()
                else: plt.plot(x,yf[i],linewidth=1,label=labelstr,c=next(color))
#                print(labelstr)
                plt.legend()
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
    plt.title("Butterworth filter: "+'order(N='+str(a.N)+') critical freq. (Wn='+str(a.Wn)+')')
    color=iter(cm.gist_rainbow(np.linspace(0,1,len(yf[0:]))))
    if(a.Plot=="input" or a.Plot=="both" or a.Plot=="animated"):
        plt.plot(x,y,color="black",label=a.InFilename.name,linewidth=1)
    if(a.Plot=="output" or a.Plot=="both" or a.Plot=="animated"):
        labelstr=""
        i=0
        for N in nspace:
            nstr="N="+str(N)
            for Wn in wspace:
                labelstr=nstr+" Wn="+str(Wn)
                plt.plot(x,yf[i],linewidth=1,label=labelstr,c=next(color))
                i+=1
    plt.legend()
    if(a.ImgFilename):
        fig.savefig(a.ImgFilename,dpi=fig.dpi)
    return fig

def GetNspace(a):
    if(len(a.N)==0): nspace=[None]
    elif(len(a.N)==1): nspace=a.N
    elif(len(a.N)==2): nspace=range(a.N[0],a.N[1]+1)
    return nspace

def GetWspace(a):
    if(len(a.Wn)==0): wspace=[None]
    elif(len(a.Wn)==1): wspace=a.Wn
    elif(len(a.Wn)==2): wspace=np.arange(a.Wn[0],a.Wn[1]+a.dWn,a.dWn).tolist()
    return wspace

def Interpolate(x,y,a):
    minX=x[0]
    maxX=x[-1]
    nSamples=maxX-minX
    fs=round(1/np.ediff1d(x).min())
    fcubic=interpolate.interp1d(x,y,kind="cubic")
    xcubic=np.linspace(minX,maxX,nSamples*fs+1)
    ycubic=fcubic(xcubic)
    return xcubic,ycubic

# Assuming the butter() function workes on a uniformly sampled set of data, 
# certain modifications are performed in this function to account for data
# which is not sampled uniformly. This function will find the number of 
# samples in the input data, find the smallest interval between adjacent
# data points, and call that the sampling frequency. Using that sampling
# frequency, it will then build a new data set using interpolation, such 
# that the entire set of data will them be uniformly sampled. The new data
# will be filtered with butter(). The new data set will then be interpolated
# and the resultant values returned at the original sample points.
def Butterworth(x,y,a):
    wspace=GetWspace(a)
    nspace=GetNspace(a)
    yf=[]
    x_int,y_int=Interpolate(x,y,a)
    print(y_int)
    for N in nspace:
        for Wn in wspace:
            B,A=signal.butter(N,Wn,btype=a.Btype,analog=a.Analog,output=a.output)     
            ybutter=signal.filtfilt(B,A,y_int)
            fbutter=interpolate.interp1d(x_int,ybutter,kind="cubic")
            yf.append(fbutter(x))
    return yf

def ButterworthMenu(argv):
    parser=argparse.ArgumentParser(prog="buttworth",usage="%(prog)s [options]")
    parser.add_argument("-i",help="Input data file.",type=argparse.FileType('r'),metavar="<str>",dest="InFilename",default="/dev/stdin")
    parser.add_argument("-o",help="Output data file.",nargs='?',type=argparse.FileType('w'),metavar="<str>",dest="OutFilename",const="/dev/stdout",default="/dev/null")
    parser.add_argument("-s",help="Save image file.",type=str,metavar="<str>",dest="ImgFilename")
    parser.add_argument("-N",help="Order of the filter. If more than one option is given, the first will be the starting order, and the second will be the finishing order. Default=3",nargs="+",type=int,metavar="<int>",dest="N",default=[3])
    parser.add_argument("-Wn",help="A scalar or lenth-2 sequence giving the critical frequencies. This is the point at which the gain drops to 1/sqrt(2) that of the passband (the “-3 dB point”). For digital filters, Wn is normalized from 0 to 1, where 1 is the Nyquist frequency, pi radians/sample. (Wn is thus in half-cycles / sample.) For analog filters, Wn is an angular frequency (e.g. rad/s). Default=0.5",nargs='+',type=float,metavar="float",dest="Wn",default=[0.5])
    parser.add_argument("-btype",help="The type of filter. Default=‘lowpass’.",type=str,metavar="<lowpass|highpass|bandpass|bandstop>",choices=["lowpass","highpass","bandpass","bandstop"],dest="Btype",default="lowpass")
    parser.add_argument("-analog",help="When specified, return an analog filter, otherwise a digital filter is returned.",action="store_true",dest="Analog")
    parser.add_argument("-p",help="Plot.",nargs='?',type=str,metavar="<input|output|both|animated|fr>",choices=["input","output","animated","both","fr"],dest="Plot",const="both",default="")
    parser.add_argument("-dWn",help="Step size for Wn[0] to Wn[1]. Default is 0.01",type=float,metavar="<float>",dest="dWn",default=0.01)
    parser.add_argument("-d",help="Number of seconds to delay between plot updates. Default is 0.5",type=float,metavar="<float>",dest="d",default=0.5)
    parser.add_argument("-output",help="Type of output: numerator/denominator (‘ba’) or pole-zero (‘zpk’). Default is ‘ba’.",type=str,metavar="<ba|zpk>",choices=["ba","zpk"],dest="output",default="ba")
    parser.add_argument("-v",help="Verbose. Intended for debugging.",action="store_true",dest="Verbose",default=False)
    parser._actions[0].help="Show help message and exit."
    args=parser.parse_args(None if argv else ["-h"])
    if(args.Verbose):
        for i in vars(args):
            print("%s=%s"%(i,getattr(args,i)))
    return args

def main(argv):
    args=ButterworthMenu(argv)
    x,y=GetXY(args.InFilename)
    yf=Butterworth(x,y,args)
    fig=PlotXY(x,y,yf,args)
    fig=SaveImage(x,y,yf,args)

if __name__=="__main__":
    main(sys.argv[1:])
