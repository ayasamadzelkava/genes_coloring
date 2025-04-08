#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec  5 11:56:51 2024

@author: phillips

Interface for repair_direct_ar_prohibit_Binary_Options.py

"""
import repair_direct_ar_prohibit_Binary_Options as rep
import graphs as gra
from os import listdir, makedirs
from os.path import isfile, join
import networkx as nx
import numpy as np
import re
import pandas as pd


##basic function reads a config file, an instance file, and