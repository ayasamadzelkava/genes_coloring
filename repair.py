#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec  5 11:56:51 2024

@author: phillips

Interface for repair_direct_ar_prohibit_Binary_Options.py
Idea is to create an all-in-one command parser

"""
from utils import repair_direct_ar_prohibit_Binary_Options as rep
from utils import graphs as gra
from os import listdir, makedirs
from os.path import isfile, join
import networkx as nx
import numpy as np
import re
import pandas as pd
import argparse
import yaml
from contextlib import redirect_stdout
import os
import random


#add and remove flag constants -- not to be changed
ADDONLY = 1
RMONLY = 2
BOTHADDRM = 3

# ===========FOR FUNCTIONAL CALL ==============

def suppress_gurobi_output():
    """Temporarily suppress Gurobi output."""
    return open(os.devnull, 'w')


def repair_network(color_file_path, instance_file_path, output_file_path, alpha, beta, prohibit_file_path=None, verbose=True):
    
    with suppress_gurobi_output() as f, redirect_stdout(f):
        from utils.settings import param_data
        
        rm_add_flag = param_data["rm_add_flag"]        
        if rm_add_flag == 'add_only':
            RM_AD = ADDONLY
        elif rm_add_flag == "rm_only":
            RM_AD = RMONLY
        elif rm_add_flag == "both":
            RM_AD = BOTHADDRM
            
            
        rmip,B,C,D,E,F,G,H,I,Setup_time = rep.set_rmip(instance_file_path,color_file_path,param_data["model_type"],\
                                                    param_data["hard_flag"],[],[],param_data["InDegOneFlag"],\
                                                    RM_AD,prohibit_file_path,verbose)
        

            
        rmip.setParam("MIPGap",param_data["mip_gap"])
        rmip.setParam("Seed", random.randint(1, 1000000))

        gname,idealnum,minp,EdgesRemoved,EdgesAdded,sumremovals,sumadds,outfname,rmip,rcons,rvars,G_result,executionTime = rep.solve_and_write(instance_file_path,\
                                        color_file_path,alpha,beta,output_file_path,rmip,B,C,D,E,F,G,H,I,\
                                        "Linear",param_data["hard_flag"],[],[],param_data["InDegOneFlag"],prohibit_file_path,\
                                        Save_info=param_data["save_output"],NetX=True)
        
        return EdgesRemoved,EdgesAdded, G_result


#=================FOR TERMINAL CALL===================

##basic function reads a parameters file, an instance file, and a color file
#outputs the inputs used along with the graph file
def create_parser():
    parser = argparse.ArgumentParser(description="Solves the specificed network repair MIP")
    parser.add_argument("-c", "--color", type=str, help="Path of the color file")
    parser.add_argument("-i", "--instance", type = str, help="Path of the instance file")
    parser.add_argument("-p", "--params", type = str, help="Path of the params yaml file")
    parser.add_argument("-o", "--output", type = str, help="Path of the output file")
    parser.add_argument("-r", "--prohibit", type = str, help="Path of the p(r)ohibited edges file")
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()

    ##test for color, instance, and params file which are required
    goodrun = True
    if not args.color:
        print("color file required for run")
        goodrun=False
        
    if not args.instance:
        print("instance file required for run")
        goodrun = False
        
    if not args.params:
        print("params file required for run")
        goodrun = False
        
    if not args.output:
        print("Output file prefix required for run")
        goodrun = False

    prohibit_path = None
    if args.prohibit:
        prohibit_path = args.prohibit

    if goodrun:      
        ##user has to send the path names
        gpath = args.instance
        cpath = args.color
        outfile = args.output
        
        #read the parameters
        yf = open(args.params,"r")
        param_data = yaml.safe_load(yf)
        HardFlag = param_data["hard_flag"]
        Save_output = param_data["Save_output"]
        InDegOneFlag=param_data["InDegOneFlag"]
        add_weight = param_data["add_weight"]
        rm_weight = param_data["remove_weight"]
        
        rm_add_flag = param_data["rm_add_flag"]        
        if rm_add_flag == 'add_only':
            RM_AD = ADDONLY
        elif rm_add_flag == "rm_only":
            RM_AD = RMONLY
        elif rm_add_flag == "both":
            RM_AD = BOTHADDRM
        else:
            print("rm_add_flag set to something weird! Exiting")
            exit(0)
            
        mip_gap = param_data["mip_gap"]
        
        model_type = param_data["model_type"]
        verbose = True
        
        rmip,B,C,D,E,F,G,H,I,Setup_time = rep.set_rmip(gpath,cpath,model_type,\
                                                    HardFlag,[],[],InDegOneFlag,\
                                                    RM_AD,prohibit_path,verbose)
            
        rmip.setParam("MIPGap",mip_gap)

        _,idealnum,_,_,_,rem,add,_,_,_,_,gg,Solving_time = rep.solve_and_write(gpath,\
                                        cpath,rm_weight,add_weight,outfile,rmip,B,C,D,E,F,G,H,I,\
                                        "Linear",HardFlag,[],[],InDegOneFlag,prohibit_path,\
                                        Save_info=Save_output,NetX=True)
    


if __name__ == "__main__":
    main()    