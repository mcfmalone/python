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
from scipy.signal import savgol_filter
from scipy import interpolate
import argparse

def GetXY(f):   # Returns two numpy arrays from a given data file.
    x,y=np.loadtxt(f,unpack=True)
    f.close()
    return x,y

def PlotXY(x,y,yf,a):
    fig=plt.figure()
    fig.set_size_inches(16.0,9.0)
    plt.style.use("ggplot")
    if(a.Plot=="animated"):
        plt.ion()
    color=iter(cm.gist_rainbow(np.linspace(0,1,len(yf[0:]))))   #gist_rainbow seems to be the same as grace
    if(a.Plot=="input" or a.Plot=="both"):
        plt.plot(x,y,color="black",label=a.InFilename.name,linewidth=2)
    if(a.Plot=="output" or a.Plot=="both" or a.Plot=="animated"):
        i=0
        for Window_length in Get_window_length_space(a):
            for Polyorder in Get_polyorder_space(a):
                if(Polyorder < Window_length):
                    for Deriv in Get_deriv_space(a):
                        for Delta in Get_delta_space(a):
                            plt.title("Savitzky-Golay filter: window_length="+str(a.window_length)+" polyorder="+str(a.polyorder)+" deriv="+str(a.deriv)+" delta="+str(a.delta))
                            labelstr=str(Window_length)+"|"+str(Polyorder)+"|"+str(Deriv)+"|"+str(Delta)
                            plt.grid(which="major",linestyle="-",linewidth="0.3")
                            plt.grid(which="minor",linestyle="-",linewidth="0.1")
                            if(a.Plot=="animated"):
                                plt.plot(x,y,color="black",label=a.InFilename.name,linewidth=2)
                                plt.plot(x,yf[i],color="red",label=labelstr,linewidth=1.25)
                                plt.legend()
                                plt.show()
                                plt.pause(a.delay)
                                fig.clear()
                            else:
                                plt.plot(x,yf[i],linewidth=0.75,label=labelstr,color=next(color))
                            i+=1
    if(a.Plot!="animated"):
        plt.legend()
        plt.show()
    return fig

def SaveImage(x,y,yf,a):
    fig=plt.figure()
    fig.set_size_inches(16.0,9.0)
    plt.style.use("ggplot")
    plt.minorticks_on()
    plt.grid(which="major",linestyle="-",linewidth="0.3")
    plt.grid(which="minor",linestyle="-",linewidth="0.1")
    plt.title("Savitzky-Golay filter: window_length="+str(a.window_length)+" polyorder="+str(a.polyorder)+" deriv="+str(a.deriv)+" delta="+str(a.delta))
    color=iter(cm.gist_rainbow(np.linspace(0,1,len(yf[0:]))))
    if(a.Plot=="input" or a.Plot=="both" or a.Plot=="animated"):
        plt.plot(x,y,color="black",label=a.InFilename.name,linewidth=2)
    if(a.Plot=="output" or a.Plot=="both" or a.Plot=="animated"):
        i=0
        for Window_length in Get_window_length_space(a):
            for Polyorder in Get_polyorder_space(a):
                if(Polyorder < Window_length):
                    for Deriv in Get_deriv_space(a):
                        for Delta in Get_delta_space(a):
                            labelstr=str(Window_length)+"|"+str(Polyorder)+"|"+str(Deriv)+"|"+str(Delta)
                            plt.plot(x,yf[i],linewidth=0.75,label=labelstr,color=next(color))
                            i+=1
    plt.legend()
    fig.savefig(a.ImgFilename,dpi=fig.dpi)
    return fig

def Get_window_length_space(a):               # window_length space (must be odd)
    if(len(a.window_length)==0): window_length_space=[None]
    elif(len(a.window_length)==1): window_length_space=a.window_length
    elif(len(a.window_length)==2): window_length_space=range(a.window_length[0],a.window_length[1]+1)
    for i in window_length_space:
        if(i%2==0): window_length_space.remove(i)
    return window_length_space

def Get_polyorder_space(a):
    if(len(a.polyorder)==0): polyorder_space=[None]
    elif(len(a.polyorder)==1): polyorder_space=a.polyorder
    elif(len(a.polyorder)==2): polyorder_space=range(a.polyorder[0],a.polyorder[1]+1)
    return polyorder_space

def Get_deriv_space(a):
    if(len(a.deriv)==0): deriv_space=[None]
    elif(len(a.deriv)==1): deriv_space=a.deriv
    elif(len(a.deriv)==2): deriv_space=range(a.deriv[0],a.deriv[1]+1)
    return deriv_space

def Get_delta_space(a):
    delta_space=[]
    if(len(a.delta)==0): delta_space=[None]
    elif(len(a.delta)==1): delta_space=a.delta
    elif(len(a.delta)==2): delta_space=np.arange(a.delta[0],a.delta[1]+a.ddelta,a.ddelta).tolist()
    return delta_space

    return delta_space

def Interpolate(x,y,a):
    minX=x[0]
    maxX=x[-1]
    nSamples=maxX-minX
    fs=round(1/np.ediff1d(x).min())
    fcubic=interpolate.interp1d(x,y,kind="cubic")
    xcubic=np.linspace(minX,maxX,nSamples*fs+1)
    ycubic=fcubic(xcubic)
    return xcubic,ycubic

# Assuming the savgol_filter() function workes on a uniformly sampled set of
# data, certain modifications are performed in this function to account for
# data which is not sampled uniformly. This function will find the number of 
# samples in the input data, find the smallest interval between adjacent
# data points, and call that the sampling frequency. Using that sampling
# frequency, it will then build a new data set using interpolation, such that
# the entire set of data will them be uniformly sampled. The new data will be
# filtered with butter(). The new data set will then be interpolated and the
# resultant values returned at the original sample points.
#
# scipy.signal.savgol_filter(x, window_length, polyorder, deriv=0, delta=1.0, axis=-1, mode='interp', cval=0.0)[source]
#
# This is a 1-d filter. If x has dimension greater than 1, axis determines the axis along which the filter is applied.
#
# x : array_like
#
# The data to be filtered. If x is not a single or double precision floating point array, it will be converted to type numpy.float64 before filtering.
#
# window_length : int
# 
# The length of the filter window (i.e. the number of coefficients). window_length must be a positive odd integer.
#
# polyorder : int
#
# The order of the polynomial used to fit the samples. polyorder must be less than window_length.
#
# deriv : int, optional
#
# The order of the derivative to compute. This must be a nonnegative integer. The default is 0, which means to filter the data without differentiating.
#
# delta : float, optional
#
# The spacing of the samples to which the filter will be applied. This is only used if deriv > 0. Default is 1.0.
#
# axis : int, optional
#
# The axis of the array x along which the filter is to be applied. Default is -1.
#
# mode : str, optional
#
# Must be ‘mirror’, ‘constant’, ‘nearest’, ‘wrap’ or ‘interp’. This determines the type of extension to use for the padded signal to which the filter is applied. When mode is ‘constant’, the padding value is given by cval. See the Notes for more details on ‘mirror’, ‘constant’, ‘wrap’, and ‘nearest’. When the ‘interp’ mode is selected (the default), no extension is used. Instead, a degree polyorder polynomial is fit to the last window_length values of the edges, and this polynomial is used to evaluate the last window_length // 2 output values.
#
# cval : scalar, optional
#
# Value to fill past the edges of the input if mode is ‘constant’. Default is 0.0.
#
# Returns:	
# y : ndarray, same shape as x
#
# The filtered data.
#
# In this function, the following parameters can be lists of two values:
#
# window_length (odd int)
# polyorder (int < window_length)
# deriv (int)
# delta (float)
#
# Any that are a list of two values, then those values will be the start and stop values of a range over which the filter will be performed.
def SavGol(x,y,a):
    yf=[]
#    window_length_space=Get_window_length_space(a)
    x_int,y_int=Interpolate(x,y,a)
    for Window_length in Get_window_length_space(a):
        for Polyorder in Get_polyorder_space(a):
            if(Polyorder < Window_length):
                for Deriv in Get_deriv_space(a):
                    for Delta in Get_delta_space(a):
#                        print(Window_length,Polyorder,Deriv,Delta)
                        ysavgol=savgol_filter(y_int,window_length=Window_length,polyorder=Polyorder,deriv=Deriv,delta=Delta,mode=a.mode,cval=a.cval)
                        fsavgol=interpolate.interp1d(x_int,ysavgol,kind="cubic")
                        yf.append(fsavgol(x))
    return yf

def MainMenu(argv):
    parser=argparse.ArgumentParser(description="Apply a Savitzky-Golay filter to an array.",prog=sys.argv[0],usage="%(prog)s [options]")
    parser.add_argument("-i",help="Input data file.",type=argparse.FileType('r'),metavar="str",dest="InFilename",default="/dev/stdin")
    parser.add_argument("-o",help="Output data file.",nargs='?',type=argparse.FileType('w'),metavar="str",dest="OutFilename",const="/dev/stdout",default="/dev/null")
    parser.add_argument("-s",help="Save image file.",type=str,metavar="str",dest="ImgFilename")
    parser.add_argument("-w","--window_length",help="The length of the filter window (i.e. the number of coefficients). window_length must be a positive odd integer. Default=3",nargs='+',type=int,metavar="int",dest="window_length",default=[3])
    parser.add_argument("-po","--polyorder",help="he order of the polynomial used to fit the samples. polyorder must be less than window_length. Default=2",nargs='+',type=int,metavar="int",dest="polyorder",default=[2])
    parser.add_argument("-d","--deriv",help="The order of the derivative to compute. This must be a nonnegative integer. The default is 0, which means to filter the data without differentiating.",nargs='+',type=int,metavar="int",dest="deriv",default=[0])
    parser.add_argument("-del","--delta",help="The spacing of the samples to which the filter will be applied. This is only used if deriv > 0. Default is 1.0.",nargs='+',type=float,metavar="float",dest="delta",default=[1.0])
    parser.add_argument("-dd",help="The change in the spacing of the samples to which the filter will be applied. This is only used if a start and end value are given for -del.",type=float,metavar="float",dest="dd",default=0.01)
    parser.add_argument("-m","--mode",help="Must be ‘mirror’, ‘constant’, ‘nearest’, ‘wrap’ or ‘interp’. This determines the type of extension to use for the padded signal to which the filter is applied. When mode is ‘constant’, the padding value is given by cval. When the ‘interp’ mode is selected (the default), no extension is used. Instead, a degree polyorder polynomial is fit to the last window_length values of the edges, and this polynomial is used to evaluate the last window_length // 2 output values. 'mirror' Repeats the values at the edges in reverse order. The value closest to the edge is not included. 'nearest' The extension contains the nearest input value. 'constant' The extension contains the value given by the cval argument. 'wrap' The extension contains the values from the other end of the array. ",dest="mode",type=str,choices=["mirror","constant","nearest","wrap","interp"],default="interp")
    parser.add_argument("-c","--cval",help="Value to fill past the edges of the input if mode is ‘constant’. Default is 0.0.",type=float,nargs='+',metavar="float",dest="cval",default=[0.0])
    parser.add_argument("-p","--plot",help="Plot.",nargs='?',type=str,metavar="input|output|both|animated|fr",choices=["input","output","animated","both","fr"],dest="Plot",const="both",default="")
    parser.add_argument("-delay",help="The amount of time to delay between animated plot updates.",type=float,metavar="float",dest="delay",default=0.5)
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
    yf=SavGol(x,y,args)
    fig=PlotXY(x,y,yf,args)
    if(args.ImgFilename): fig=SaveImage(x,y,yf,args)
    return 0

if __name__=="__main__":
    main(sys.argv[1:])
