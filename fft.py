#!/usr/bin/python
# -*- coding: utf-8 -*-
# $Id: fft.py,v 1.1 2019/02/03 19:43:36 micha Exp $
# $Author: micha $
# $Revision: 1.1 $
# $Log: fft.py,v $
# Revision 1.1  2019/02/03 19:43:36  micha
# Initial revision
#

import sys
import matplotlib.pyplot as plt
import numpy as np
import scipy as sp
from scipy import signal
from scipy.interpolate import interp1d
import argparse

plt.style.use('ggplot')

def GetXY(f):
    x,y=np.loadtxt(f,unpack=True)
    f.close()
    return x,y

def Interpolate(x,y):
    f_s=round(1/np.ediff1d(x).min())                # Sample frequency.
    f_int=interp1d(x,y,kind="cubic")                # Generate interpolation function.
    x_int=np.linspace(x[0],x[-1],(x[-1]-x[0])*f_s+1)# Generate new domain which is uniformly sampled.
    y_int=f_int(x_int)                              # Generate new range from uniformly-sampled domain.
    return x_int,y_int

def fft(x,y):
    x_int,y_int=Interpolate(x,y)                    # Get uniformly-sampled data.
    N=len(y_int)                                    # Find the number of data points, N, which is length.
    f_s=round(1/np.ediff1d(x_int).min())            # Get sample frequency from interpolated data.
    f=f_s*np.arange((N/2))/N                        # Generate frequency vector, which is half the length of N.
    Y_k=np.fft.fft(y_int)[0:int(N/2)]/N             # Perform FFT on interpolated y.
    Y_k[1:]=2*Y_k[1:]                               # Single side spectrum only.
    #Y_db=20*np.log10(2*np.abs(Y_k)/N)
    Pxx=np.abs(Y_k)                                 # Get magnitude of complex values.
    return f,Pxx

def PlotXY(x,y):
    fig=plt.figure()
    fig.set_size_inches(16,9)
    plt.minorticks_on()
    plt.grid(which="major",linestyle="-",linewidth="0.3")
    plt.grid(which="minor",linestyle="-",linewidth="0.1")
    plt.plot(x,y,color='black')
    plt.title("Original data")
    plt.show(block=False)
    return fig

def PlotFP(f,p):
    fig,ax=plt.subplots()
    fig.set_size_inches(16,9)
    plt.minorticks_on()
    plt.grid(which="major",linestyle="-",linewidth="0.3")
    plt.grid(which="minor",linestyle="-",linewidth="0.1")
    plt.plot(f,p,color='red')
    ax.set_xscale("log")
    ax.set_yscale("log")
    plt.title("Frequency Spectrum")
    plt.xlabel("Hz")
    plt.ylabel("dB")
    plt.show(block=False)
    return fig

def MainMenu(argv):
    parser=argparse.ArgumentParser(prog=sys.argv[0],usage="%(prog)s [options]")
    parser.add_argument("-i",help="Input data file.",type=argparse.FileType('r'),metavar="<str>",dest="InFilename",default="/dev/stdin")
    parser.add_argument("-o",help="Output data file.",nargs='?',type=argparse.FileType('w'),metavar="str",dest="OutFilename",const="/dev/stdout",default="/dev/null")
#    parser.add_argument("-s",help="Save image file.",type=argparse.FileType('wb'),metavar="<str>",dest="ImgFilename")
    parser.add_argument("-s",help="Save image file.",type=str,metavar="<str>",dest="ImgFilename")
    parser.add_argument("-p",help="Plot.",nargs='?',type=str,metavar="input|output",choices=["input","output","both"],dest="Plot",const="both",default="")
    parser.add_argument("-v",help="Verbose. Intended for debugging.",action="store_true",dest="Verbose",default=False)
    parser._actions[0].help="Show help message and exit."
    args=parser.parse_args(None if argv else ["-h"])
    if(args.Verbose):
        for i in vars(args):
            print("%s=%s"%(i,getattr(args,i)))
    return args

def main(argv):
    args=MainMenu(argv)

    x,y=GetXY(args.InFilename)

    if("both" in args.Plot or "input" in args.Plot):
        fig=PlotXY(x,y)
    F,P=fft(x,y)
    if("both" in args.Plot or "output" in args.Plot):
        fig=PlotFP(F,P)

    outdata=np.array([F,P])
    np.savetxt(args.OutFilename,outdata.T,fmt=['%16.10e','%17.10e'])
    args.OutFilename.close()

    if(args.ImgFilename):
        fig.savefig(args.ImgFilename,dpi=fig.dpi)

    plt.show()

if __name__=="__main__":
    main(sys.argv[1:])
