# PVParameterSet class

import string, sys

#Fixed variable name defines
V_INPUT_FILE_NAME = "$INPUT_FILE_NAME"
V_OUTPUT_FILE_NAME = "$OUTPUT_FILE_NAME"
V_ADDITIONAL_FIELDS_FILE_NAME = "$ADDITIONAL_FIELDS_FILE_NAME"
V_SCORE_GROUPING_ANNOTATION_FIRST_INDEX = "$SCORE_GROUPING_ANNOTATION_FIRST_INDEX"
V_SCORE_GROUPING_ANNOTATION_SECOND_INDEX = "$SCORE_GROUPING_ANNOTATION_SECOND_INDEX"
V_VALUES_FOR_BAR_GRAPH_INDEX = "$VALUES_FOR_BAR_GRAPH_INDEX"
V_VALUES_FOR_NOTE_HEAD_COLORS_INDEX = "$VALUES_FOR_NOTE_HEAD_COLORS_INDEX" 
V_PERFORMANCE_GROUPING_ANNOTATION_FIRST_INDEX = "$PERFORMANCE_GROUPING_ANNOTATION_FIRST_INDEX"
V_PERFORMANCE_GROUPING_ANNOTATION_SECOND_INDEX = "$PERFORMANCE_GROUPING_ANNOTATION_SECOND_INDEX"

class PVParameterSet:
    #
    # member variables
    #
    _input_fp = None # pointer on the input file

    # variables for storing the loaded params
    _input_file_name = None
    _output_file_name = None
    _additional_fields_file_name = None
    _score_grouping_annotation_first_index = None
    _score_grouping_annotation_second_index = None
    _values_for_bar_graph_index = None
    _values_for_note_head_colors_index = None
    _performance_grouping_annotation_first_index = None
    _performance_grouping_annotation_second_index = None

    #
    # constructor
    #
    def __init__(self, fn):
        self.input_fp = open(fn, "r")
        self._loadParams()

    def _loadParams(self):
        lines = self.input_fp.read()
        lines = string.split(lines, "\n")
        for line in lines:
            # exclude comments
            if "#" in line:
                continue

            if "$" in line:
                l = string.split(line, "=")

                if (len(l) != 2):
                    print "[PVParamertSet] parameter set file is corrupted:", line
                    sys.exit()

                var_name = l[0]
                value = l[1]
                # strip white spaces
                var_name = var_name.replace(" ", "")
                value = value.replace(" ", "")
                
                # load values
                if (var_name == V_INPUT_FILE_NAME):
                    self._input_file_name = str(value)
                elif (var_name == V_OUTPUT_FILE_NAME):
                    self._output_file_name = str(value)
                elif (var_name == V_ADDITIONAL_FIELDS_FILE_NAME):
                    self._additional_fields_file_name = str(value)
                elif (var_name == V_SCORE_GROUPING_ANNOTATION_FIRST_INDEX):
                    self._score_grouping_annotation_first_index = int(value)
                elif (var_name == V_SCORE_GROUPING_ANNOTATION_SECOND_INDEX):
                    self._score_grouping_annotation_second_index = int(value)
                elif (var_name == V_VALUES_FOR_BAR_GRAPH_INDEX):
                    self._values_for_bar_graph_index = int(value)
                elif (var_name == V_VALUES_FOR_NOTE_HEAD_COLORS_INDEX):
                    self._values_for_note_head_colors_index = int(value)
                elif (var_name == V_PERFORMANCE_GROUPING_ANNOTATION_FIRST_INDEX):
                    self._performance_grouping_annotation_first_index = int(value)
                elif (var_name == V_PERFORMANCE_GROUPING_ANNOTATION_SECOND_INDEX):
                    self._performance_grouping_annotation_second_index = int(value)
                
    #
    # description
    #

    def __str__(self):
        s = "input_file_name: "+str(self._input_file_name)+"\n"
        s += "output_file_name: "+str(self._output_file_name) +"\n"
        s += "additional_fields_file_name: "+str(self._additional_fields_file_name)+"\n"
        s += "score_grouping_annotation_first_index: "+str(self._score_grouping_annotation_first_index)+"\n"
        s += "score_grouping_annotation_second_index: "+str(self._score_grouping_annotation_second_index)+"\n"
        s += "bar_graph_values_index: "+str(self._values_for_bar_graph_index)+"\n"
        s += "note_head_coloring_index: "+str(self._values_for_note_head_colors_index)+"\n"
        s += "performance_grouping_annotation_first_index: "+str(self._performance_grouping_annotation_first_index)+"\n"
        s += "performance_grouping_annotation_second_index: "+str(self._performance_grouping_annotation_second_index)
        return s
    #
    # properties
    #

    @property
    def input_file_name(self):
        return self._input_file_name

    @property
    def output_file_name(self):
        return self._output_file_name

    @property
    def additional_fields_file_name(self):
        return self._additional_fields_file_name

    @property
    def score_grouping_annotation_first_index(self):
        return self._score_grouping_annotation_first_index

    @property
    def score_grouping_annotation_second_index(self):
        return self._score_grouping_annotation_second_index

    @property
    def values_for_bar_graph_index(self):
        return self._values_for_bar_graph_index

    @property
    def values_for_note_head_colors_index(self):
        return self._values_for_note_head_colors_index

    @property
    def performance_grouping_annotation_first_index(self):
        return self._performance_grouping_annotation_first_index

    @property
    def performance_grouping_annotation_second_index(self):
        return self._performance_grouping_annotation_second_index

