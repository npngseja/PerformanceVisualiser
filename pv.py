#!/usr/bin/python

######################################################################
# Performance Visualiser On Sheet Music
#
# Input: 
# Output:
#
# Taehun Kim, Audio Communication Group, TU Berlin
# 2012
#
#######################################################################

import os, sys, string
sys.path.append("./")
import pdb # for debugging
from PVParameterSet import * #parameter set object
from PVInputData import * #note property list parsed from the input csv with parameterSet
from PVRenderer import * #rendering score with the charts of the specified values

#global variables
p_fn_params = "" # parameter set file name
p_fn_input = "" # input file name
p_fn_output = "" # output file name

#end of global variables

def intro():
    if len(sys.argv) != 2:
        print "Usage: "+sys.argv[0]+" paramerter_set_file"
        print "* You can find howto make a parameter set file in README."
        sys.exit()
    else:
        print "Performance Visualiser On Sheet Music v0.1"
        print "Taehun Kim, Audio Communication Group, TU Berlin 2012"
        print 
        print "[LOG] parameter set file:", sys.argv[1]
        global p_fn_params
        p_fn_params = sys.argv[1]
        

def main():
    intro()
    parameterSet = PVParameterSet(p_fn_params)
    inputData = PVInputData(parameterSet)
    renderer = PVRenderer(inputData, parameterSet.output_file_name)
    renderer.startRender()

#program start point
main()

