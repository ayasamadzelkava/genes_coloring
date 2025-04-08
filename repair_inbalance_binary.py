#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple algorithm to achieve an in-balanced coloring

Created on Tue Dec 10 09:35:34 2024

@author: phillips
"""

import networkx as nx
import pandas as pd


charsep="\t"

def read_data(fname,colorfile):
    
    #read in graph
    base_graph = nx.read_weighted_edgelist(fname,comments="#",\
                                           create_using=nx.DiGraph)
    
    print("Read graph: n="+str(base_graph.order())+" m="+str(base_graph.size()))
    
    #read color file

    #cdict keys are  
    ##read in color set
    ctable=pd.read_csv(colorfile,index_col=0,sep=charsep,header=None,\
                       comment="#")        
    cdict = ctable.to_dict()[1]

    #set up a list of colorsets
    color_sets = []        
    color_dict = {}
    for c in set(cdict.values()):
        C = [i for i in cdict.keys() if cdict[i]==c]
        color_sets.append(C)
        color_dict[c] = C
         
          

    print("Read colors")

    
    #inputs = {}     
    #inputs['base_graph'] = base_graph
    #inputs['color_keys'] = cdict.values()
    #inputs['color_dict'] = color_dict
    
    
    return base_graph,color_dict

#takes a graph and two colorsets
#G is the input graph
#C and D are colorsets
#R is the graph where edges will be added or removed to inbalance C
#with respect to D
#creates a subgraph
def repair_two_colors(G,C,D,R):
    
    #Get the sizes of D and C
    D_size = len(D)
    C_size = len(C)
    
    #for each node in C
        #get the edges from D to that node
        #calculate original in-degree wrt D
    DC_edge_dict = {}
    DC_edge_len_dict = {}
    DC_notadj_dict = {}
    for p in C:
        Dp_edges = [(i,j) for (i,j) in G.edges() if i in D and j==p]
        Dp_notadj = [j for j in D if (p,j) not in Dp_edges]
        DC_edge_dict[p] = Dp_edges
        DC_edge_len_dict[p] = len(Dp_edges)
        DC_notadj_dict[p] = Dp_notadj
        
    #for each possible in-balance number
    best_count = D_size*C_size + 1
    for temp_target in range(0,D_size+1):
        temp_count = 0
        for p in C:
            temp_count = temp_count + abs(temp_target - DC_edge_len_dict[p])
            
        #update best_count, best_target
        if temp_count < best_count:
            best_target = temp_target
            best_count = temp_count
    
    #conduct repair for best_target
    #for each node in C
    for p in C:
        #get the D to p edges
        Dp_edges = DC_edge_dict[p]
        delta = best_target - DC_edge_len_dict[p]
        if delta > 0:            
            Dp_notadj = DC_notadj_dict[p]
            print(f"Adding {delta} edges to {p}")
            for i in range(delta):                
                #add some edges to the edge list
                Dp_edges.append((Dp_notadj[i],p))
        elif delta < 0:
            temp_list = Dp_edges.copy()
            for i in range(-delta):
                #remove an edge from Dp_edges
                Dp_edges.remove(temp_list[i])
        
        #add these edges to R
        R.add_edges_from(Dp_edges)
            
            
    return R, best_count, best_target
    
    
def repair_graph(graph_path,color_path):
    
    #read in the graph and colorsets
    base_graph,color_dict = read_data(graph_path,color_path)
    
    color_list = list(color_dict.keys())
    
    #create a solution graph with the same nodes
    repaired_graph = nx.DiGraph()
    repaired_graph.add_nodes_from(base_graph.nodes())
    
    #for every pair of colors, repair the graph
    obj_value = 0
    target_dict = {}
    for c in color_list:
        C = color_dict[c]
        for d in color_list:
            D = color_dict[d]
            
            print(f"Repairing color {c} wrt color {d}")
            repaired_graph,best_count,best_target = \
                repair_two_colors(base_graph,C,D,repaired_graph)
            #keep track of the objective               
            obj_value = obj_value + best_count
            #save best_target in a dictionary with the color numbers as keys
            target_dict[(c,d)] = best_target

    return repaired_graph,obj_value,target_dict

def analyze_graph(graph_path,color_path):
    
    base_graph,color_dict = read_data(graph_path,color_path)

    color_list = list(color_dict.keys())


    color_indeg_dict = {}    
    for c in color_list:
        print(f"Processing color {c}")
        C = color_dict[c]
        for d in color_list:
            D = color_dict[d]            
            #Dp_nums is the list of different D to p degrees
            Dp_nums = []
            for p in C:
                Dp_edges = [(i,j) for (i,j) in base_graph.edges() if i in D and j==p]
                Dp_deg = len(Dp_edges)
                if Dp_deg not in Dp_nums:
                    Dp_nums.append(Dp_deg)
                    
            color_indeg_dict[(c,d)] = Dp_nums
            inbal_nums = len(Dp_nums)
            if inbal_nums > 1:
                print(f"Color {c} wrt color {d} has {inbal_nums}")
  
  
    return color_indeg_dict


# test it
#graph_path = '/Users/phillips/Documents/GitHub/genes_coloring/200_nodes/200_nodes.graph.txt'
#color_path = '/Users/phillips/Documents/GitHub/genes_coloring/200_nodes/200_nodes.colors.txt'
def main():
    graph_path = '/Users/phillips/Documents/GitHub/genes_coloring/Ayas_networks_from_Bryant/data/9878_nodes/9878_nodes.graph.txt'
    color_path = '/Users/phillips/Documents/GitHub/genes_coloring/Ayas_networks_from_Bryant/data/9878_nodes/9878_nodes.colors.txt'
    #out_path = '/Users/phillips/Documents/GitHub/genes_coloring/Ayas_networks_from_Bryant/data/9878_nodes/9878_nodes.stats.txt'

    analyze_graph(graph_path,color_path)


    

    #R,val,td = repair_graph(graph_path,color_path)

    #print(f"Objective value is {val}")
    
if __name__ == "__main__":
    main() 
                