import sys, string, os, pdb
from copy import deepcopy
from define import *
#define indices of the required fields
OFFSET_OPTIONAL_FIELDS = ATTACK  

R_MEASURE = 0
R_BEAT_POS = 1
R_TIME_SIG = 2
R_NOTE_NUM = 3
R_DURATION = 4

R_INTERVAL_GRP = -4
R_DURATION_GRP = -3
R_TEMPO_GRP = -2
R_DYNAMICS_GRP = -1

class PVOptionalFieldExtender:
    _input_raw_matrix = []
    _additional_fields_file_fp = None
    _additional_fields_matrix = []

    def __init__(self, input_raw_matrix, additional_fields_file_name):
        self._input_raw_matrix = input_raw_matrix
        self._additional_fields_file_fp = open(additional_fields_file_name, "r")
    
    def go(self):
        self._loadAdditionalFieldsToMatrix()
        self._extendRawMatrix()
        
        return self._input_raw_matrix

    def _loadAdditionalFieldsToMatrix(self):
        lines = self._additional_fields_file_fp.read()
        lines = string.split(lines, "\n")
        for line in lines:
            if line == "":
                continue

            if not(line[0] in "0123456789"):
                continue
            splitLine = string.split(line, "|")
            scoreFeatures = string.split(splitLine[0])
            grps = string.split(splitLine[-1], ",")
            combined = scoreFeatures+grps
            self._additional_fields_matrix.append(combined)
        

    def _extendRawMatrix(self):
        max_state_number = -1000
        min_state_number = 1000
        for t in self._additional_fields_matrix:
            state_number = int(t[R_INTERVAL_GRP])
            if state_number > max_state_number:
                max_state_number = state_number
            if state_number < min_state_number:
                min_state_number = state_number
            
        temp = deepcopy(self._additional_fields_matrix)
        for i in xrange(len(self._additional_fields_matrix)):
            if i == 0:
                temp[i][R_INTERVAL_GRP] = "start"
                temp[i][R_DURATION_GRP] = "start"
                temp[i][R_TEMPO_GRP] = "start"
                temp[i][R_DYNAMICS_GRP] = "start"
                
            elif i == len(self._additional_fields_matrix)-1:
                temp[i][R_INTERVAL_GRP] = "stop"
                temp[i][R_DURATION_GRP] = "stop"
                temp[i][R_TEMPO_GRP] = "stop"
                temp[i][R_DYNAMICS_GRP] = "stop"
            else:
                prev_t = self._additional_fields_matrix[i-1]
                cur_t = self._additional_fields_matrix[i]
                # interval group
                if (int(prev_t[R_INTERVAL_GRP]) == max_state_number) and (int(cur_t[R_INTERVAL_GRP]) == min_state_number):
                    temp[i][R_INTERVAL_GRP] = "start"
                    temp[i-1][R_INTERVAL_GRP] = "stop"
                # interval group
                if int(prev_t[R_DURATION_GRP]) == max_state_number and int(cur_t[R_DURATION_GRP]) == min_state_number:
                    temp[i][R_DURATION_GRP] = "start"
                    temp[i-1][R_DURATION_GRP] = "stop"
                # interval group
                if int(prev_t[R_TEMPO_GRP]) == max_state_number and int(cur_t[R_TEMPO_GRP]) == min_state_number:
                    temp[i][R_TEMPO_GRP] = "start"
                    temp[i-1][R_TEMPO_GRP] = "stop"
                # interval group
                if int(prev_t[R_DYNAMICS_GRP]) == max_state_number and int(cur_t[R_DYNAMICS_GRP]) == min_state_number:
                    temp[i][R_DYNAMICS_GRP] = "start"
                    temp[i-1][R_DYNAMICS_GRP] = "stop"
            
        temp_raw_matrix = deepcopy(self._input_raw_matrix)
        for t in temp:
            measure = float(t[R_MEASURE])
            beat_pos = float(t[R_BEAT_POS])
            ref_pos = measure+beat_pos*0.1
            interval_grp = t[R_INTERVAL_GRP]
            duration_grp = t[R_DURATION_GRP]
            tempo_grp = t[R_TEMPO_GRP]
            dynamics_grp = t[R_DYNAMICS_GRP]
            for i in xrange(len(temp_raw_matrix)):
                n = temp_raw_matrix[i]
                n_measure = float(n[MEASURE])
                n_beat_pos = float(n[BEAT_POS])
                n_pos = n_measure+n_beat_pos*0.1
                if ref_pos == n_pos:
                    #same position. update grouping string
                    self._input_raw_matrix[i] = self._input_raw_matrix[i]+[interval_grp, duration_grp, tempo_grp, dynamics_grp]

            
            
        
            
