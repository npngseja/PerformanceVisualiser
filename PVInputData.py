# PVInputData

import string, sys
from PVParameterSet import *
import pdb
from PVOptionalFieldExtender import *

#define indices of the required fields
STAFF = 0
VOICE = 1
KEY = 2
CLEF = 3
MEASURE = 4
BEAT_POS = 5
METRIC = 6
NOTENUM = 7
NOTE_NAME = 8
DURATION = 9
TIME_SIG = 10
SLUR = 11
DYN_MARK = 12
WEDGE = 13
TEMPO_MARK = 14
ARTICULATION = 15
OFFSET_OPTIONAL_FIELDS = 16 # the absolute index of the first optional field is 13 

class PVInputData:

    _paramSet = None
    _meta_info_dictionary = {} # this dictionary holds meta informations such as title and avg. tempo
    _raw_matrix = [] # here we load input csv as a matrix (list)
    _grouped_notes_matrix = {} # here we group notes on the same timestamp and describe them as nested lists. key: staff number, value: nested lists 
    _note_properties_for_visualisation_matrix = {} # this matrix holds necessary properties defined in the param set

    def __init__(self, params):
        self._paramSet = params
        print "[LOG] load input file"
        self._loadToRawMatrix()
        if not(params.additional_fields_file_name == None):
            # we should extend our input data matrix
            optionalFieldsExtender = PVOptionalFieldExtender(self._raw_matrix, self._paramSet.additional_fields_file_name)
            self._raw_matrix = optionalFieldsExtender.go()

        print "[LOG] grouping input note sequences with staff numbers and time stamps"
        self._groupNotesBasedOnTimeStamp()
        print "[LOG] extract specified values for the visualisation"
        self._extractSpecifiedProperties()
#        self.catDictionary(self._grouped_notes_matrix)
 
    def _parseMetaInfoLine(self, l):
        splitStr = string.split(l, ":")
        if (len(splitStr) != 2):
            print "[Error] this line is invalid:", l
            sys.exit()
        var_name = splitStr[0].replace(" ", "")
        var_name = var_name.replace("$", "")
        value = splitStr[1].replace(" ", "")
        if not(value == "n/a"):
            self._meta_info_dictionary[var_name] = value

        #calc number of fields
        if var_name == "legend":
            fields = string.split(value, ",")
            self._meta_info_dictionary["fields_count_all"] = len(fields)
            fields_count_optional = 0
            for token in fields:
                if "*" in token:
                    fields_count_optional += 1

            self._meta_info_dictionary["fields_count_optional"] = fields_count_optional
            self._meta_info_dictionary["fields_count_required"] = len(fields) - fields_count_optional

    def _loadToRawMatrix(self):
        input_fn = self._paramSet.input_file_name
        lines = open(input_fn, "r").read()
        lines = string.split(lines, "\n")
        for line in lines:
            if len(line) > 0 and line[0] == "#":
                continue # this is a comment line. skip it
            
            # CURRENTLY WE SKIP GRACE NOTES!!!
            if "(grace)" in line:
                continue

            if len(line) > 0 and line[0] == "$":
                self._parseMetaInfoLine(line)
                continue
        
            if len(line) == 0:
                continue

            if not(line[0] in "1234567890"):
                print "[Error] this line is invalid. Skip it:", line
                continue

            l = string.split(line, ",")
            if not("fields_count_all" in self._meta_info_dictionary.keys()):
                print "[Error] no legend is found. input csv should have $legend var."
                sys.exit()
            if (len(l) == self._meta_info_dictionary["fields_count_all"]):
                self._raw_matrix.append(l)
            else:
                print "[Error] this line has a missed value:", line
                sys.exit()

    def _groupNotesBasedOnTimeStamp(self):
        self._splitWithVoices()
        for sv in self._grouped_notes_matrix.keys():
            self._grouped_notes_matrix[sv] = self._groupNotesBasedOnTimeStampForEachVoice(self._grouped_notes_matrix[sv])
        
    
    def _splitWithVoices(self):
        for n in self._raw_matrix:
            staff = n[STAFF]
            if int(staff) == 0:
                staff = "1"
            voice = n[VOICE]
            # TEMPORARY WE PARSE ONLY THE FIRST VOICE! THIS MUST BE FIXED!
            if not(int(voice) == 1):
                continue

            key = str(staff)+"-"+str(voice) # key is STAFF-VOICE!!!
            if key in self._grouped_notes_matrix.keys():
                self._grouped_notes_matrix[key].append(n)
            else:
                self._grouped_notes_matrix[key] = [n]
            
        # sort each lists
        for k in self._grouped_notes_matrix.keys():
            self._grouped_notes_matrix[k] = sorted(self._grouped_notes_matrix[k], cmp=self._comparator_position)


    def _comparator_position(self, a, b):
        posA = float(a[MEASURE])+float(a[BEAT_POS])*0.1
        posB = float(b[MEASURE])+float(b[BEAT_POS])*0.1
        if posA > posB:
            return 1
        elif posA < posB:
            return -1
        else:
            return 0
    def _comparator_pitch(self, a, b):
        pa = int(a[NOTENUM])
        pb = int(b[NOTENUM])
        if pa < pb:
            return 1
        elif pa > pb:
            return -1
        else:
            return 0

    def _groupNotesBasedOnTimeStampForEachVoice(self, l):
        notesOnSameBeat = []
        last_pos = -1.1
        output = []
        for n in l:
            measure = n[MEASURE]
            beat_pos = n[BEAT_POS]
            current_pos = float(measure)+float(beat_pos)*0.1
            if len(notesOnSameBeat) == 0:
                # initial setup
                notesOnSameBeat.append(n)
                last_pos = current_pos
                continue
            
            if last_pos == current_pos:
                # this is a note on the same position
                notesOnSameBeat.append(n)
                continue
            else:
                # this is the first note on the NEXT position
                # flush the buffer
                output.append(sorted(notesOnSameBeat, cmp=self._comparator_pitch))
                notesOnSameBeat = []
                notesOnSameBeat.append(n)
                last_pos = current_pos
        
        # flush the last buffer
        output.append(notesOnSameBeat)
        return output

    def catDictionary(self, d):
        for staff in d:
            print "STAFF:", staff
            notes = d[staff]
            for n in notes:
                for t in n:
                    print t
                print"---"
        
        
    def _extractSpecifiedProperties(self):
        # init
        for staff in self._grouped_notes_matrix.keys():
            self._note_properties_for_visualisation_matrix[staff] = []

        # filter out unnecessary optional fields
        for staff in self._note_properties_for_visualisation_matrix.keys():
            notes = self._grouped_notes_matrix[staff]
            new_notes = []
            params = self._paramSet
            for n in notes:
                new_n = []
                for t in n:
                    new_t = t[:OFFSET_OPTIONAL_FIELDS]
                    if params.values_for_bar_graph_index == None:
                        new_t.append("n/s") # not specificed
                    else:
                        abs_index = OFFSET_OPTIONAL_FIELDS+params.values_for_bar_graph_index
                        new_t.append(t[abs_index])

                    if params.values_for_note_head_colors_index == None:
                        new_t.append("n/s")
                    else:
                        abs_index = OFFSET_OPTIONAL_FIELDS+params.values_for_note_head_colors_index
                        new_t.append(t[abs_index])
                    
                    if params.score_grouping_annotation_first_index == None:
                        new_t.append("n/s")
                    else:
                        abs_index = OFFSET_OPTIONAL_FIELDS+params.score_grouping_annotation_first_index
                        new_t.append(t[abs_index])
                    
                    if params.score_grouping_annotation_second_index == None:
                        new_t.append("n/s")
                    else:
                        abs_index = OFFSET_OPTIONAL_FIELDS+params.score_grouping_annotation_second_index
                        new_t.append(t[abs_index])

                    if params.performance_grouping_annotation_first_index == None:
                        new_t.append("n/s")
                    else:
                        abs_index = OFFSET_OPTIONAL_FIELDS+params.performance_grouping_annotation_first_index
                        new_t.append(t[abs_index])

                    if params.performance_grouping_annotation_second_index == None:
                        new_t.append("n/s")
                    else:
                        abs_index = OFFSET_OPTIONAL_FIELDS+params.performance_grouping_annotation_second_index
                        new_t.append(t[abs_index])

                    new_n.append(new_t)
                    
                new_notes.append(new_n)
                
            self._note_properties_for_visualisation_matrix[staff] = new_notes
                    
                    
    #
    # properties
    @property
    def note_properties_for_visualisation_matrix(self):
        return self._note_properties_for_visualisation_matrix

    @property
    def grouped_notes_matrix(self):
        return self._grouped_notes_matrix

    @property
    def raw_matrix(self):
        return self._raw_matrix
        
    @property
    def meta_info(self):
        return self._meta_info_dictionary
        
