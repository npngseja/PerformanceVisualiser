# PVRenderer

import sys, string
import math
from PVInputData import *
import pdb
from copy import deepcopy

#define indices
BAR_GRAPH_VALUES = 0
NOTE_HEAD_COLORING_VALUES = 1
SCORE_GROUPING_FIRST = 2
SCORE_GROUPING_SECOND = 3
PERFORMANCE_GROUPING_FIRST = 4
PERFORMANCE_GROUPING_SECOND = 5

class PVRenderer:

    _inputData = {} # key = staff, value = notes grouped as nested lists
    _output_fn = "annotated.ly"
    _output_fp = None
    _max_value_bar_graph = -10000
    _min_value_bar_graph = 10000
    _max_value_note_head = -10000
    _min_value_note_head = 10000

    def __init__(self, inputData, outputFileName):
        self._inputData = inputData
        self._output_fn = outputFileName
        self._output_fp = open(self._output_fn, "w")

    def startRender(self):
        print "[LOG] start to render ............."
        print "[LOG] output file name:", self._output_fn
        print "[LOG] finding max and min values"
        self._findMaxAndMinValues()
        print "[LOG] max and min bar graph values: "+str(self._max_value_bar_graph)+", "+str(self._min_value_bar_graph)
        print "[LOG] max and min note head coloring values: "+str(self._max_value_note_head)+", "+str(self._min_value_note_head)
        print "[LOG] write header"
        self._writeHeader()
        print "[LOG] write paper setup"
        self._writePaperSetup()
        print "[LOG] write note content"
        self._writeNoteContent()
        print "[LOG] write score definition"
        self._writeScoreDefinition()

    def _findMaxAndMinValues(self):
        n_d = self._inputData._note_properties_for_visualisation_matrix
        for k in n_d.keys():
            notes = n_d[k]
            for ns in notes:
                for n in ns:
                    if not(n[OFFSET_OPTIONAL_FIELDS+BAR_GRAPH_VALUES] == "n/s"):    
                        bar_grp_value = n[OFFSET_OPTIONAL_FIELDS+BAR_GRAPH_VALUES]
                        if not(bar_grp_value == "NA"):
                            bar_grp_value = float(bar_grp_value)
                        else:
                            continue
                        if bar_grp_value > self._max_value_bar_graph:
                            self._max_value_bar_graph = bar_grp_value
                        if bar_grp_value < self._min_value_bar_graph:
                            self._min_value_bar_graph = bar_grp_value
                    
                    if not(n[OFFSET_OPTIONAL_FIELDS+NOTE_HEAD_COLORING_VALUES] == "n/s"):
                        note_head_value = n[OFFSET_OPTIONAL_FIELDS+NOTE_HEAD_COLORING_VALUES]
                        if not(note_head_value == "NA"):
                            note_head_value = float(note_head_value)
                        else:
                            continue
                        if note_head_value > self._max_value_note_head:
                            self._max_value_note_head = note_head_value
                        if note_head_value < self._min_value_note_head:
                            self._min_value_note_head = note_head_value
        self._min_value_bar_graph = self._min_value_bar_graph*0.9
        self._min_value_note_head = self._min_value_note_head*0.9
            
    def _writeScoreDefinition(self):
        s = "% The score definition"+"\n"
        s += "\\new PianoStaff <<"+"\n"
        s += "   \\set PianoStaff.instrumentName = \"VoiceOne\""+"\n"
        s += "   \\set PianoStaff.shortInstrumentName = \"One\""+"\n"
        voices = self._inputData._note_properties_for_visualisation_matrix.keys()
        staffAndVoices = {}
        for v in voices:
            staff = int(string.split(v, "-")[0])
            voice = int(string.split(v, "-")[1])
            if staff in staffAndVoices.keys():
                staffAndVoices[staff].append(voice)
            else:
                staffAndVoices[staff] = [voice]

        staffs = sorted(staffAndVoices.keys())
        for st in staffs:
            # TEMPORALY WE SHOW ONLY THE FIRST STAFF and FIRST VOICE!
            if not(st == 1):
                continue
            s += "   \\context Staff = \""+str(st)+"\" <<"+"\n"
            vs = sorted(staffAndVoices[st])
            for v in vs:
                if not(v == 1):
                    continue

                voiceName = self._nameFromInt(int(v))
                s += "      \\context Voice = \"PartPOneVoice"+voiceName+"\" { \\PartPOneVoice"+voiceName+" }"+"\n"
            s += "   >>"+"\n"
        
        s += ">>"+"\n"
           
        self._output_fp.write(s)
            
    def _writeNoteContent(self):
        d = self._inputData.note_properties_for_visualisation_matrix
        for v in d.keys():
            print "[LOG] voice "+str(v)+" is processing ..."
            d[v] = self._findGroupingBoundaries(d[v], SCORE_GROUPING_FIRST)
            d[v] = self._findGroupingBoundaries(d[v], SCORE_GROUPING_SECOND)
            d[v] = self._findGroupingBoundaries(d[v], PERFORMANCE_GROUPING_FIRST)
            d[v] = self._findGroupingBoundaries(d[v], PERFORMANCE_GROUPING_SECOND)
            self._writeVoice(v)
           
    def _findGroupingBoundaries(self, notes, key):
        o = deepcopy(notes)
        # first we should filter out all of the rest marks! then we can find the boundaries!
        no_na = []
        isThisFormattedGrpString = False
        for i in xrange(len(notes)):
            if ":" in notes[i][0][OFFSET_OPTIONAL_FIELDS+key]:
                isThisFormattedGrpString = True

            if notes[i][0][OFFSET_OPTIONAL_FIELDS+key] == "NA":
                continue
            else:
                temp = deepcopy(notes[i])
                for t in temp:
                    t.append(i)
                no_na.append(temp) # the last element is the index of the note in the original list! 

        if isThisFormattedGrpString == False:
            return o

        for i in xrange(len(no_na)):
            if no_na[i][0][OFFSET_OPTIONAL_FIELDS+key].lower() == "n/s":
                continue

            if no_na[i][0][OFFSET_OPTIONAL_FIELDS+key].upper() == "NA":
                continue

            if i == 0:
                for t in o[no_na[i][0][-1]]:
                    t[OFFSET_OPTIONAL_FIELDS+key] = "start"
            elif i == len(no_na)-1:
                for t in o[no_na[i][0][-1]]:
                    t[OFFSET_OPTIONAL_FIELDS+key] = "stop"
            else:
                prev_str = (no_na[i-1][0][OFFSET_OPTIONAL_FIELDS+key].replace("<", "")).replace(">", "")
                cur_str = (no_na[i][0][OFFSET_OPTIONAL_FIELDS+key].replace("<", "")).replace(">", "")
                next_str = (no_na[i+1][0][OFFSET_OPTIONAL_FIELDS+key].replace("<", "")).replace(">", "")
                if not(cur_str == prev_str):
                    for t in o[no_na[i][0][-1]]:
                        t[OFFSET_OPTIONAL_FIELDS+key] = "start"
                elif not(cur_str == next_str):
                    for t in o[no_na[i][0][-1]]:
                        t[OFFSET_OPTIONAL_FIELDS+key] = "stop"
                else:
                    for t in o[no_na[i][0][-1]]:
                        t[OFFSET_OPTIONAL_FIELDS+key] = "-"

        
        return o
            
            
            
    def _nameFromInt(self, i):
        if i == 0:
            return "Zero"
        elif i == 1:
            return "One"
        elif i == 2:
            return "Two"
        elif i == 3:
            return "Three"
        elif i == 4:
            return "Four"
        elif i == 5:
            return "Five"
        else:
            return "Six"

    def _writeVoice(self, v):
        voiceName = self._nameFromInt(int(string.split(v, "-")[1]))
        varName = "PartPOneVoice"+voiceName
        notes = self._inputData.note_properties_for_visualisation_matrix[v]
        s = varName+" = {"+"\n"

        prev_clef = "NA"
        prev_key = "NA"
        prev_time_sig = "NA"
        prev_measure = 10000.0
        # find first measure number
        for k in self._inputData.note_properties_for_visualisation_matrix.keys():
            temp_note = self._inputData.note_properties_for_visualisation_matrix[k][0][0]
            if float(temp_note[MEASURE]) < prev_measure:
                prev_measure = float(temp_note[MEASURE])

        # find length of the upbeats, if necessary
        upbeatLength = 0.0
        isUpbeatWritten = False
        if prev_measure == 0.0:
            # measure 0 means this is upbeats!
            for ns in notes:
                if float(ns[0][MEASURE]) ==  0.0:
                    upbeatLength += float(ns[0][DURATION])

        for ns in notes:
            # attributes
            clef = ns[0][CLEF]
            if not(clef == prev_clef):
                prev_clef = clef
                if clef == "G" or clef == "g":
                    s += "\\clef \"treble\""+" "
                elif clef == "F" or clef == "f":
                    s += "\\clef \"bass\""+" "

            key = ns[0][KEY]
            if not(key == prev_key):
                prev_key = key
                s += "\\key "+key.lower()+" \\major"+" "

            time_sig = ns[0][TIME_SIG]
            if not(time_sig == prev_time_sig):
                prev_time_sig = time_sig
                s += "\\numericTimeSignature\\time "+time_sig+"\n"
        
                
            measure = float(ns[0][MEASURE])
            if measure == 0.0 and prev_measure == 0.0 and isUpbeatWritten == False:
                # this is UpBeat
                s += "\\partial "+self._durationToSymbol(upbeatLength)+"\n"
                isUpbeatWritten = True

            if not(measure == prev_measure):
                    # new measure begins!
                    diff_measure = measure - prev_measure # will be 1 in normal cases
                    for i in xrange(int(diff_measure-1)):
                        # if there are empty measures, this iteration will be evaluated
                        baseBeat = string.split(ns[0][TIME_SIG], "/")[1]
                        numBeat = string.split(ns[0][TIME_SIG], "/")[0]
                        s += "s"+baseBeat+"*"+numBeat+"\n"
                   # for i in xrange(int(diff_measure)):
                    s += "| "+"% "+str(measure)+"\n"
                    prev_measure = measure
            
            # write note info here!
            s += self._writeEachNotes(ns)
       
        s += "\\bar \"|.\""+"\n"
        s += "}"+"\n\n"
        
        self._output_fp.write(s)

    def _writeEachNotes(self, ns): # will also handle chorded notes
        s = "\override TextScript #'staff-padding = #7.0 \n"
        #print "[LOG] notes:", ns
        # note information
        chorded = False
        hasSlur = False
        

        if len(ns) > 1:
            # this is chorded notes
            chorded = True
       
            # groupings- score second
        if ns[0][OFFSET_OPTIONAL_FIELDS+SCORE_GROUPING_FIRST] == "start":
            s += "\\override PhrasingSlur #\'color = #blue \\phrasingSlurDashed\n"
       
        if chorded == True:
            s += "<"+"\n"

        for n in ns:
            noteName = n[NOTE_NAME]
            pitch_root = noteName[0]
            octave = noteName[-1]
            slur = n[SLUR]

            if not(slur == "NA"):
                hasSlur = True

            if noteName.upper() == "NA":
                pitch_root = "r"
                octave = 0
            
            # note head
               
            if n[OFFSET_OPTIONAL_FIELDS+NOTE_HEAD_COLORING_VALUES] == "NA" or n[OFFSET_OPTIONAL_FIELDS+NOTE_HEAD_COLORING_VALUES] == "n/s":
                pass # default black color!
            else:
                note_head_value = float(n[OFFSET_OPTIONAL_FIELDS+NOTE_HEAD_COLORING_VALUES])
                note_head_color = ((note_head_value-self._min_value_note_head)/self._max_value_note_head)
                if chorded == True:
                    s += "\\tweak #\'color #(rgb-color "+str(200.0/255.0*note_head_color)+" 0.0 "+str(100.0/255.0*note_head_color)+")"+"\n"
                else:
                    s += "\\override NoteHead #\'color = #(rgb-color "+str(200.0/255.0*note_head_color)+" 0.0 "+str(100.0/255.0*note_head_color)+")"+"\n"
            # note name
            note = ""
            note += pitch_root.lower()
            for st in noteName:
                if st == "#":
                    note += "is"
                elif st == "b":
                    note += "es"
                    
            octave = int(octave) - 3
            if octave > 0:
                note += "\'"*octave
            elif octave < 0:
                note += ","*octave
            else:
                note += ""
            
            s += note+"\n"
        # end of for loop
        if chorded == True:
            s += ">"
        else:
            s = s[:-1] # eleminate last \n 
        duration = self._durationToSymbol(n[DURATION])
        s += duration+"\n"
       
        # write slur
        if hasSlur == True:
            if slur.lower() == "start":
                s += "("+"\n"
            elif slur.lower() == "stop":
                s += ")"+"\n"

        # groupings- score first
        if ns[0][OFFSET_OPTIONAL_FIELDS+SCORE_GROUPING_SECOND] == "start":
            s += "\\startGroup\n"
        elif ns[0][OFFSET_OPTIONAL_FIELDS+SCORE_GROUPING_SECOND] == "stop":
            s += "\\stopGroup\n"

        # groupings- score second
        if ns[0][OFFSET_OPTIONAL_FIELDS+SCORE_GROUPING_FIRST] == "start":
            s += "\\(\n"
        elif ns[0][OFFSET_OPTIONAL_FIELDS+SCORE_GROUPING_FIRST] == "stop":
            s += "\\)\n"
        
        
        # bar graph
        if not(ns[0][OFFSET_OPTIONAL_FIELDS+BAR_GRAPH_VALUES] == "n/s" or ns[0][OFFSET_OPTIONAL_FIELDS+BAR_GRAPH_VALUES] == "NA"):
            bar_grp_value = float(ns[0][OFFSET_OPTIONAL_FIELDS+BAR_GRAPH_VALUES])
            bar_height = 10*((bar_grp_value - self._min_value_bar_graph)/self._max_value_bar_graph)
            s += "^\\markup { \\with-color #(rgb-color 0.0 0.54 0.42) \\filled-box #'(0 . 0.5) #'(0 . "+str(bar_height)+") #0 }"+"\n"
        # note information end

        #grouping- performance first and second
        perf_grp_first = False
        perf_grp_second = False
        if ns[0][OFFSET_OPTIONAL_FIELDS+PERFORMANCE_GROUPING_FIRST] == "stop":
            perf_grp_first = True
           
        if ns[0][OFFSET_OPTIONAL_FIELDS+PERFORMANCE_GROUPING_SECOND] == "stop":
            perf_grp_second = True
           
        if perf_grp_first == True and perf_grp_second == True:
            s += "\\override BreathingSign #\'text = \\markup { \with-color #(rgb-color 0.07 0.20 0.52 )  \\musicglyph #\"scripts.upbow\" }\n"
            s += "\\breathe\n"
        elif perf_grp_first == True:
            s += "\\override BreathingSign #\'text = \\markup { \with-color #(rgb-color 0.07 0.20 0.52 )  \\musicglyph #\"scripts.rcomma\" }\n"
            s += "\\breathe\n"
        elif perf_grp_second == True:
            s += "\\override BreathingSign #\'text = \\markup { \with-color #(rgb-color 0.07 0.20 0.52 )  \\musicglyph #\"scripts.rvarcomma\" }\n"
            s += "\\breathe\n"

            
       
        return s

    def _durationToSymbol(self, n):
        n = float(n)
        # quarter note = 1.0, eighth = 0.5
	basic_durs = [0.0625, 0.125, 0.25, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0]

        ret = "64"
        dur_root = 0.0
        dur_sub_value = 0.0
        for _d in basic_durs:
            # n = ad+r
            x = n/_d
            a = math.floor(x)
            r = n - _d*a
            if a == 1:
                dur_root = _d
                dur_sub_value = r
                break

        # now we have note beam and values for calc. dots
        ret = str(int((dur_root/4)**-1))
        if dur_sub_value > 0.0:
            # we need dots!
            num_dots = int(math.floor(dur_root/dur_sub_value)/2.0)
#            pdb.set_trace()
            ret += "."*int(num_dots)
            
	return ret

    def _writePaperSetup(self):
        s = "\\paper {"+"\n"
        s += "   system-system-spacing #'basic-distance = #25"+"\n"
        s += "   markup-system-spacing #'basic-distance = #25"+"\n"
        s += "   paper-width = 21.01\\cm"+"\n"
        s += "   paper-height = 29.7\\cm"+"\n"
        s += "   top-margin = 1.5\\cm"+"\n"
        s += "   bottom-margin = 1.5\\cm"+"\n"
        s += "   left-margin = 1.74\\cm"+"\n"
        s += "   right-margin = 1.5\\cm"+"\n"
        s += "   page-top-space = 1.99\\cm"+"\n"
        s += "   "+"\n"
        s += "   }"+"\n"
        s += ""+"\n"
        s += "\\layout {"+"\n"
        s += "   \\context { \\Score"+"\n"
        s += "      skipBars = ##t"+"\n"
        s += "      autoBeaming = ##f"+"\n"
        s += "      \\consists \"Horizontal_bracket_engraver\""+"\n"
        s += "      }"+"\n"
        s += "   }"+"\n"
        self._output_fp.write(s)

    def _writeHeader(self):
        output_str = "\\version \"2.14.2\""+"\n"
        output_str += "\n"
        output_str += "\\header {"+"\n"
        output_str += "   title = \""+self._inputData.meta_info["title"]+"\""+"\n"
        output_str += "   tagline = \"Performance Visualiser v.0.1, Audio Communication Group, TU Berlin\""+"\n"
        output_str += "   }"+"\n"
        output_str += "\n"

        self._output_fp.write(output_str)
        
    
    
