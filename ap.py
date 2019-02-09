#!/usr/bin/python
# This is a test program which uses argparse within the Cmd class.
# Command methods are defined in the Cmd object. These commands can
# accept arguments. And the arguments are parsed with argparse.
# $Id: ap.py,v 1.1 2019/02/09 18:22:19 micha Exp micha $
# $Author: micha $
# $Revision: 1.1 $
# $Log: ap.py,v $
# Revision 1.1  2019/02/09 18:22:19  micha
# Initial revision
#

import sys
import argparse
from cmd import Cmd
import inspect

class CMD(Cmd):
    prompt="test> "
    def __init__(self):
        Cmd.__init__(self)
    def x_parser(self):
#        parser=argparse.ArgumentParser(description="Test x sub-menu.",prog="x",usage="%(prog)s [options]")
        parser=argparse.ArgumentParser()
        parser.add_argument("-xi",help="integer",type=int,metavar="int",dest="i")
        parser.add_argument("-xf",help="float",type=float,metavar="float",dest="f")
        parser.add_argument("-xs",help="string",type=str,metavar="string",dest="s")
        parser.add_argument("-xb",help="boolean",action="store_true",dest="b",default=False)
        return parser

    def y_parser(self):
        parser=argparse.ArgumentParser()
#        parser=argparse.ArgumentParser(description="Test y sub-menu.",prog="y",usage="%(prog)s [options]")
        parser.add_argument("-yi",help="integer",type=int,metavar="int",dest="i")
        parser.add_argument("-yf",help="float",type=float,metavar="float",dest="f")
        parser.add_argument("-ys",help="string",type=str,metavar="string",dest="s")
        parser.add_argument("-yb",help="boolean",action="store_true",dest="b",default=False)
        return parser

    def do_x(self,argv):
        argvl=argv.split()
        sys.argv[0]='x'
        parser=self.x_parser()
        try:
            args=parser.parse_args(argvl)
        except SystemExit:
            return 0
        print("x(%s)"%argvl)
        for i in vars(args):
#            print(inspect.stack()[0][3])
            print("%s=%s"%(i,getattr(args,i)))

    def help_x(self):
        self.do_x("-h")

    def do_y(self,argv):
        argvl=argv.split()
        sys.argv[0]='y'
        parser=self.y_parser()
        try:
            args=parser.parse_args(argvl)
        except SystemExit:
            return 0
        print("y(%s)"%argvl)
        for i in vars(args):
#            print(inspect.stack()[0][3])
            print("%s=%s"%(i,getattr(args,i)))

    def help_y(self):
        self.do_x("-h")

    def do_exit(self,inp):
        return True
    def help_exit(self):
        print("Exit the terminal.")
    def default(self,inp):
        if inp=='x' or inp=='q':
            return self.do_exit(inp)
    do_EOF=do_exit
    help_EOF=help_exit


def main():
    parser=argparse.ArgumentParser(description="Test sub-menus in interactive mode.",prog=sys.argv[0],usage="%(prog)s [options]")
    parser.add_argument("-i",help="integer",type=int,metavar="int",dest="i")
    parser.add_argument("-f",help="float",type=float,metavar="float",dest="f")
    parser.add_argument("-s",help="string",type=str,metavar="string",dest="s")
    parser.add_argument("-b",help="boolean",action="store_true",dest="b",default=False)
    args=parser.parse_args()
    print("main(%s)"%sys.argv)
    for i in vars(args):
        print("%s=%s"%(i,getattr(args,i)))
    test=CMD()
    test.cmdloop()
    return 0

if __name__=="__main__":
    main()
#    main(sys.argv[1:])
