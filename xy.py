#!/usr/bin/python
# $Id: xy.py,v 1.1 2018/12/10 05:19:27 lyonsd Exp micha $
# $Author: lyonsd $
# $Revision: 1.1 $
# $Log: xy.py,v $
# Revision 1.1  2018/12/10 05:19:27  lyonsd
# Initial revision
#

import sys
import os
import numpy as np
import argparse
from cmd import Cmd
import subprocess as sp
from scipy.signal import savgol_filter
import matplotlib.pyplot as plt

class XY(object):
  data="0.0"
  rows=0
  cols=0
  max=0.0
  min=0.0
  mean=0.0
  median=0.0
  stdev=0.0
  domain=0.0
  range=0.0
  ifile=""
  tfile=""
  ofile=""
  def __init__(self):
    return
  def Update(self):
    self.rows=len(self.data)
    self.cols=len(self.data[0])
    self.max=np.max(self.y)
    self.maxi=np.argmax(self.y)
    self.amax=np.max(abs(self.y))
    self.amaxi=np.argmax(abs(self.y))
    self.min=np.min(self.y)
    self.mini=np.argmin(self.y)
    self.amin=np.min(abs(self.y))
    self.amini=np.argmin(abs(self.y))
    self.domain=np.max(self.x)-np.min(self.x)
    self.range=self.max-self.min
    self.mean=np.mean(self.y)
    self.median=np.median(self.y)
    self.stdev=np.std(self.y)
    try:
        self.x
    except NameError:
        pass
    else:
        try:
            self.y
        except NameError:
            pass
        else:
            self.data=np.array([self.x,self.y])
            self.data=self.data.T
    fout=open(self.tfile,"w")
    fmt=["%23.16e","%23.16e"]
    np.savetxt(fout,self.data,fmt)
    fout.close()
  def ReadFile(self,filename):
    self.ifile=filename
    self.tfile=self.ifile+".txy"
    self.data=np.loadtxt(self.ifile)
    self.x=self.data[:,0]
    self.y=self.data[:,1]
    self.Update()
  def WriteFile(self,filename):
    if filename=="" and self.ofile=="":
      if os.path.exists(self.ifile): self.ofile=self.ifile
    else:
      if filename!="": self.ofile=filename
    fout=open(self.ofile,"w")
    fmt=["%23.16e","%23.16e"]
    np.savetxt(fout,self.data,fmt)
  def NewXY(self,x,y):
    self.x=x
    self.y=y
    self.data=np.array([x,y])
    self.data=self.data.T
    if self.tfile=="":
      self.tfile="deltaxy.txy"
    self.Update()
  def Meta(self):
    if self.ifile: print("iFile  = %s" % self.iFile())
    if self.ofile: print("oFile  = %s" % self.oFile())
    print("Rows   = %d" % self.Rows())
    print("Cols   = %d" % self.Cols())
    print("Max    = %23.16e at i=%3d" % (self.Max(),self.maxi))
    print("aMax   = %23.16e at i=%3d" % (self.aMax(),self.amaxi))
    print("Min    = %23.16e at i=%3d" % (self.Min(),self.mini))
    print("aMin   = %23.16e at i=%3d" % (self.aMin(),self.amini))
    print("Domain = %23.16e" % self.Domain())
    print("Range  = %23.16e" % self.Range())
    mu=unichr(0x3bc).encode("utf-8")
    print("\x1B[3m%s\x1B[23m      = %23.16e" % (mu,self.Mean()))
    print("Median = %23.16e" % self.Median())
    sigma=unichr(0x3c3).encode("utf-8")
    print("\x1B[3m%s\x1B[23m      = %23.16e" % (sigma,self.Stdev()))
  def iFile(self): return self.ifile
  def oFile(self): return self.ofile
  def Rows(self): return self.rows
  def Cols(self): return self.cols
  def Max(self): return self.max
  def aMax(self): return self.amax
  def Min(self): return self.min
  def aMin(self): return self.amin
  def Domain(self): return self.domain
  def Range(self): return self.range
  def Mean(self): return self.mean
  def Median(self): return self.median
  def Stdev(self): return self.stdev
  def read_x(self,xdata):
    self.x=xdata
  def read_y(self,xdata):
    self.y=ydata
  def Data(self):
    print "Data"
    self.i=np.arange(self.rows)
    td=np.array([self.i,self.x,self.y])
    fout=open("/dev/stdout","w")
    fmt=["%3d","%23.16e","%23.16e"]
    np.savetxt(fout,td.T,fmt)
  def Plot(self):
    fig=plt.figure()
    fig.set_size_inches(16,9)
    plt.plot(self.x,self.y, color='black', label='input: '+self.ifile)
#    plt.plot(x,y2, color='red', label='output: '+ofile)
#    plt.title(filt+' ('+'w='+str(w)+')')
    plt.legend()
    plt.minorticks_on()
    plt.grid(which='major',linestyle='-',linewidth='0.3')
#    plt.grid(which='minor',linestyle=':',linewidth='0.3')
    plt.show()
  def __add__(self,xy):
    return np.add(self.y,xy.y)
  def __sub__(self,xy):
    return np.add(self.y,-xy.y)
  def xmGrace(self):
    cmdstr=["/usr/local/bin/xmgrace","-nxy",self.tfile]
    self.pid=sp.Popen(cmdstr).pid
  def __del__(self):
    if os.path.exists(self.tfile):
      try: os.remove(self.tfile)
      except OSError, e: print("Error: %s: %s" % (e.filename,e.strerror))
    else: print("Error: 404: %s: Not found" % self.tfile)
  def setOfile(self,ofile):
    if ofile=="": self.ofile="/dev/stdout"
    else: self.ofile=ofile
  def Savitzky_Golay_Filter(self,sgsz,sgord):
    yhat=savgol_filter(self.y,sgsz,sgord)
    self.y=np.copy(yhat)
    self.Update()
  def Moving_Average_Filter(self,sz):
    box=np.ones(sz)/sz
    yhat=np.convolve(self.y,box,mode="same")
    self.y=np.copy(yhat)
    self.Update()

class XY2(Cmd):
  xy_1=False
  xy_2=False
  SGF_sz=0
  SGF_o=0
  prompt='xy> '
#  deltaxy=object.__new__(XY)
  def __init__(self,file1,file2):
    Cmd.__init__(self)
    self.ReadXY1(file1)
    self.ReadXY2(file2)
  def SwapData(self,index):
      if index=="" and self.i=="":
        print("Swap index not set.")
        return
      else:
        if index=="": index=self.i
      index=int(index)
      self.xy1.y[index:],self.xy2.y[index:]=self.xy2.y[index:],self.xy1.y[index:].copy()
      self.xy1.Update()
      self.xy2.Update()
  def DeltaXY(self):
    self.deltaxy=XY()
    self.deltaxy.NewXY(self.xy1.x,self.xy1.y-self.xy2.y)
  def ReadXY1(self,fn):
    if self.xy_1==False: self.xy1=XY()
    if fn=="" and self.xy1.ifile=="":
      fn=raw_input("Enter a filename from which to read xy data for set 1: ")
    else:
      if fn=="": fn=self.xy1.ifile
    self.xy1.ReadFile(fn)
    self.xy_1=True
    self.xy1orig=self.xy1
    if self.xy_1 and self.xy_2:
      if self.xy1.rows==self.xy2.rows:
        self.DeltaXY()
  def ReadXY2(self,fn):
    if self.xy_2==False: self.xy2=XY()
    if fn=="" and self.xy2.ifile=="":
      fn=raw_input("Enter a filename from which to read xy data for set 2: ")
    else:
      if fn=="": fn=self.xy2.ifile
    self.xy2.ReadFile(fn)
    self.xy_2=True
    self.xy2orig=self.xy2
    if self.xy_1 and self.xy_2:
      if self.xy1.rows==self.xy2.rows:
        self.DeltaXY()
  def do_exit(self,inp):
    return True
  def help_exit(self):
    print("Exit the terminal.")
  def default(self,inp):
    if inp=='x' or inp=='q':
      return self.do_exit(inp)
  do_EOF=do_exit
  help_EOF=help_exit
  def do_shell(self,inp):
    output=os.popen(inp).read()
    print output
    self.last_output=output
  def help_shell(self):
    print("Execute shell command.")
  def do_p(self,n):
    if n=="": self.help_p()
    if n=='1': self.xy1.Plot()
    if n=='2': self.xy2.Plot()
    if n=='d': self.deltaxy.Plot()
  def help_p(self):
    print("Plot")
    print("Usage: p 1|2|d")
    print("Plot set 1|2|d.")
  def do_r(self,args):
    if len(args)==0:
      f=""
      self.ReadXY1(f)
      self.ReadXY2(f)
      return
    if len(args)==1:
      try:
        int(args)
      except ValueError:
        self.help_r()
        return
      n=args
      f=""
    else:
      inp=args.split()
      try:
        int(inp[0])
        n=inp[0]
        f=inp[1]
      except ValueError:
        self.help_r()
        return
    if n=='1': self.ReadXY1(f)
    if n=='2': self.ReadXY2(f)
  def help_r(self):
    print("Read\n\nUsage: r [1|2 [filename]]\n")
    print("Reads filename and stores into 1|2.\nIf no arguments are given, then current filenames for both sets are read.\nIf filename is not given, then it reads the current filename for the given set.")
  def do_w(self,args):
    if len(args)==0:
      f=""
      self.xy1.WriteFile(f)
      self.xy2.WriteFile(f)
      return
    if len(args)==1:
      n=args
      f=""
    else:
      inp=args.split()
      if len(inp)!=2:
        self.help_w()
        return
      n=inp[0]
      f=inp[1]
    if n=='1': self.xy1.WriteFile(f)
    if n=='2': self.xy2.WriteFile(f)
    if n=='d': self.deltaxy.WriteFile(f)
  def help_w(self):
    print("Write")
    print("Usage: w 1|2|d [filename]")
    print("Writes data from 1|2|d, where d is the difference between sets 1 and 2, to filename.")
  def do_d(self,n):
    if n=='1': self.xy1.Data()
    if n=='2': self.xy2.Data()
    if n=='d': self.deltaxy.Data()
  def help_d(self):
    print("Data")
    print("Usage: d 1|2|d")
    print("Prints the data of 1|2|d, where d is the difference between set 1 and set 2, to stdout.")
  def do_m(self,n):
    if n=='1':
      self.xy1.Meta()
      return
    if n=='2':
      self.xy2.Meta()
      return
    if n=='d':
      self.deltaxy.Meta()
      return
    print("1. %s\n2. %s" % (self.xy1.ifile,self.xy2.ifile))
  def help_m(self):
    print("Metadata")
    print("Usage: m 1|2|d")
    print("Prints the metadata of 1|2|d, where d is the difference between set 1 and set 2.")
  def do_si(self,i):
    if i=="": self.help_si()
    self.i=i
  def help_si(self):
    print("Index")
    print("Usage: i <int>")
    print("Set index were data of the two sets are to be swapped.")
  def do_g(self,n):
    if n=='':
      cmdstr=["/usr/local/bin/xmgrace","-nxy",self.xy1.tfile,"-nxy",self.xy2.tfile]
      self.pid=sp.Popen(cmdstr)
#      os.system(cmdstr)
      return
    if n=='1':
      self.xy1.xmGrace()
      return
    if n=='2':
      self.xy2.xmGrace()
      return
  def help_g(self):
    print("Grace (xmgrace)")
    print("Usage: g [1|2]")
    print("Display 1|2 or both in xmgrace plot.")
  def do_s(self,index):
    self.SwapData(index)
  def help_s(self):
    print("Swap")
    print("Usage: sw [i]")
    print("Swap data of sets 1 and 2 at index i to the end.")
  def do_SGF_sz(self,n):
    self.SGF_sz=int(n)
  def do_SGF_o(self,n):
    self.SGF_o=int(n)
  def do_SGF(self,n):
    if n=='1':
      self.xy1.Savitzky_Golay_Filter(self.SGF_sz,self.SGF_o)
    if n=='2':
      self.xy2.Savitzky_Golay_Filter(self.SGF_sz,self.SGF_o)
    if self.xy_1 and self.xy_2:
      if self.xy1.rows==self.xy2.rows:
        self.DeltaXY()
  def help_SGF(self):
    print("Savitzky-Golay Filter")
    print("Usage: SGF 1|2")
    print("Apply Savitzky-Golay filter to 1|2.")
  def do_MAF(self,n):
    if n=='1':
      self.xy1.Moving_Average_Filter(self.MAF_sz)
    if n=='2':
      self.xy2.Moving_Average_Filter(self.MAF_sz)
    if self.xy_1 and self.xy_2:
      if self.xy1.rows==self.xy2.rows:
        self.DeltaXY()
  def help_MAF(self):
    print("Moving Average Filter")
    print("Usage: MAF 1|2")
    print("Apply moving average filter to 1|2.")
  def do_MAF_sz(self,n):
    self.MAF_sz=int(n)

###########################################################
# Main function
###########################################################
def main(argv):
  infile="/dev/stdin"
  outfile="/dev/stdout"
##########################################################
# Parse command-line arguments
##########################################################
  parser = argparse.ArgumentParser()
  parser.add_argument("-if1",help="Input file 1",type=str,metavar="<filename>",dest="ifname1")
  parser.add_argument("-if2",help="Input file 2",type=str,metavar="<filename>",dest="ifname2")
  parser.add_argument("-of1",help="Output file 1",type=str,metavar="<filename>",dest="ofname1",default="out1.dat")
  parser.add_argument("-of2",help="Output file 2",type=str,metavar="<filename>",dest="ofname2",default="out2.dat")
  parser.add_argument("-si",help="Swap index",type=int,metavar="<int>",dest="si")
  parser.add_argument("-ein",help="Print the input channel energy at infinity.",action="store_true")
  parser.add_argument("-eout",help="Print the output channel energy at infinty.",action="store_true")
  parser.add_argument("-max",help="Print the maximum value of the data.",action="store_true")
  parser.add_argument("-mean",help="Print the mean value of the data.",action="store_true")
  parser.add_argument("-min",help="Print the minimum value of the data.",action="store_true")
  parser.add_argument("-range",help="Print the range of the data.",action="store_true")
  parser.add_argument("-meta",help="Print the meta data.",action="store_true")
  parser.add_argument("-a","--alpha",help="Alpha (static dipole polarizability) in au.",type=float,metavar="<float>",dest="alpha")
  parser.add_argument("-c","--console",help="Console (interactive mode).",dest="Console",action="store_true")
  parser.add_argument("-o","--offset",help="Offset to subtract from final energy value (typically the input channel's energy at infinity.",type=float,metavar="<float>",dest="offset")
  parser.add_argument("-z","--charge",help="Charge in au.",type=int,metavar="<integer>",dest="z")
  args = parser.parse_args()
##########################################################

  twoxy=XY2(args.ifname1,args.ifname2)
#  if args.Console==True:
  twoxy.cmdloop()

#  xy2=XY2(args.ifname1,args.ifname2)
#  print xy2.Mindiff()
#  xy2.xy1.Meta()
#  xy2.SwapData(args.si)
  
#  xy2.xy1.Data(args.ofname1)
#  xy2.xy2.Data(args.ofname2)
#  xy=XY(infile)
#  xy.Meta()
#  xy.Data(outfile)

#  xy1=XY(args.ifname1)
#  xy2=XY(args.ifname2)

#  xy=xy1-xy2
#  print np.savetxt(sys.stdout,xy.T)
  return 0

if __name__=="__main__":
  main(sys.argv[1:])
