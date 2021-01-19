from Motif import Motif
from copy import deepcopy
import random
from Metric import Bar
from Metric import Beat
from Metric import SubBeat
import Harmonizer
import math


class Section:

    def __init__(self, melodic_info, chord_info, metric_info):

        # copy metric info:
        self.beats_per_bar = metric_info['beats_per_bar']
        self.sub_beats_per_beat = metric_info['sub_beats_per_beat']

        # copy chord info:
        self.bars_per_chord = chord_info['bars_per_chord']
        self.chord_placement = chord_info['chord_pattern']
        self.has_chords = chord_info['write_chords']
        self.force_full_cadence = chord_info['force_full_cadence']

        # copy melodic info:
        self.offset = melodic_info['motif_offset']
        self.basic_motif = melodic_info['main_motif']
        self.motif_note_dur = melodic_info['motif_note_dur']
        self.motif_markov_probs = melodic_info['motif_markov_probs']
        self.bars_per_motif = melodic_info['bars_per_motif']
        self.arpeggiate = melodic_info['arp']
        self.op_probabilities = melodic_info['motif_trans_probs']
        self.has_melody = melodic_info['write_melody']
        self.vertical_offset = melodic_info['octave']
        self.section_structure = melodic_info['melodic_structure']
        self.scale = melodic_info['scale']

        # generate melody as hierarchy of pitch successions:
        self.motifs = self.write_motifs()
        self.notes = self.to_notes()
        print("melody notes: ", self.notes)

        # map melody to metric representation:
        self.metric = []

        self.write_melody_to_metric()

        # create harmony based on metric representation of melody:
        self.chord_sequence = Harmonizer.harmonize(self)

        self.write_chords_to_metric()

    def create_strong_cadence_motif(self):
        strong_cadence_motif = deepcopy(self.basic_motif)
        strong_cadence_motif.random_operations(self.op_probabilities)
        strong_cadence_motif.make_strong_cadence()
        return strong_cadence_motif

    def create_weak_cadence_motif(self):
        weak_cadence_motif = deepcopy(self.basic_motif)
        weak_cadence_motif.random_operations(self.op_probabilities)
        weak_cadence_motif.make_weak_cadence()
        return weak_cadence_motif

    def create_new_motif(self):
        new_motif = deepcopy(self.basic_motif)
        new_motif.random_operations(self.op_probabilities)
        return new_motif

    def to_notes(self):
        notes = []
        for motif in self.motifs:
            notes.append(motif.notes)
        return notes

    def write_motifs(self):
        # generate motifs based on instructions from section_structure:
        motifs = []
        for part in self.section_structure:
            if part == 'staircase':
                staircase_motif = Motif.generate_new_staircase_motif(self.basic_motif.length, 0, self.motif_markov_probs)
                motifs = self.write_staircase(staircase_motif)
            elif part == 'main_motif':
                motifs.append(self.basic_motif)
            elif part == 'main_motif_weak_cadence':
                motifs.append(self.create_weak_cadence_motif())
            elif part == 'main_motif_strong_cadence':
                motifs.append(self.create_strong_cadence_motif())
            elif part == 'new_motif':
                motifs.append(Motif.generate_new(self.basic_motif.length, random.choice([0,2,4]), self.motif_markov_probs))
            elif part == 'main_motif_trans':
                motifs.append(deepcopy(self.basic_motif).transpose(2))
            elif part == 'none':
                motifs.append(Motif.generate_empty_motif())

        return motifs

    def write_melody_to_metric(self):
        # when mapping melody hierarchy to metric representation, timing info is added:

        main_sub_beats_idxs = self.update_sub_beat_idxs(self.basic_motif, [], self.offset)

        for j, motif in enumerate(self.motifs):

            # the first and third motif will always have the same rhythm:
            if j % 2 == 0 and motif.length == len(main_sub_beats_idxs):
                sub_beats_idxs = main_sub_beats_idxs
            else:
                sub_beats_idxs = self.update_sub_beat_idxs(motif, sub_beats_idxs, self.offset)

            motif_notes = motif.notes
            motif_bars = []
            # create empty bars needed for the motif:
            for m in range(self.bars_per_motif):
                motif_bars.append(Bar(self.beats_per_bar, self.sub_beats_per_beat))

            # go through every single note and write it to metric:
            for k, note in enumerate(motif_notes):
                note = note + self.vertical_offset  # every note is transposed to the correct octave
                note_beat = self.motif_note_dur * k + self.offset  # the beat the note should fall on (doesn't wrap)

                # sub-beat-shifting only occurs when there is no arp and when the note_duration is 1 beat
                if self.motif_note_dur == 1 and self.arpeggiate == [None, None, None]:
                    sub_beat_idx = sub_beats_idxs[k]
                else:
                    sub_beat_idx = 0
                bar_idx = math.floor(note_beat / self.beats_per_bar)
                beat_idx = note_beat % self.beats_per_bar
                dur = self.motif_note_dur - sub_beat_idx/self.sub_beats_per_beat
                motif_bars[bar_idx].beats[beat_idx].sub_beats[sub_beat_idx].add_note(note, dur)

                if self.arpeggiate and self.motif_note_dur == 1:
                    for i in range(self.sub_beats_per_beat - 1):
                        if self.arpeggiate[i] != None and sub_beat_idx + i < 4:
                            arp_note = note + self.arpeggiate[i]
                            dur = self.motif_note_dur
                            motif_bars[bar_idx].beats[beat_idx].sub_beats[sub_beat_idx + i + 1].add_note(arp_note, dur)

            for bar in motif_bars:
                self.metric.append(bar)

    def update_sub_beat_idxs(self, motif, sub_beats_idxs_prev, offset):
        sub_beats_idxs = []

        for i in range(motif.length):  # for each note in motif
            # if the note falls on first beat of a bar, it should fall on first sub-beat:
            if (i + offset)*self.motif_note_dur % self.beats_per_bar == 0:
                sub_beat_idx = 0
            # if the previous note was offset, current note should be on beat:
            elif i > 0 and sub_beats_idxs[i-1] != 0:
                sub_beat_idx = 0
            # the final note cannot be shifted:
            elif i == motif.length - 1:
                sub_beat_idx = 0
            # else: 50/50 chance of on beat or half beat
            else:
                sub_beat_idx = random.choice([0, 2])
            sub_beats_idxs.append(sub_beat_idx)

        # there is a chance of simply copying the rhythm of the previous motif:
        if len(sub_beats_idxs_prev) == motif.length:
            sub_beats_idxs = random.choices([sub_beats_idxs_prev, sub_beats_idxs], [3, 7], k=1)[0]
        return sub_beats_idxs

    def write_staircase(self, staircase_motif):
        motifs = []
        for i in range(staircase_motif.length):
            if i == 0:
                motifs.append(self.basic_motif)
            else:
                new_motif = deepcopy(motifs[i-1])
                new_motif.transpose(staircase_motif.intervals[i-1])
                if i == staircase_motif.length - 1:
                    new_motif.make_strong_cadence()
                motifs.append(new_motif)
        return motifs

    def write_chords_to_metric(self):
        if self.has_chords and not self.has_melody:
            self.metric = []
            for j, motif in enumerate(self.motifs):
                for m in range(self.bars_per_motif):
                    self.metric.append(Bar(self.beats_per_bar, self.sub_beats_per_beat))

        if self.has_chords:
            for i, chord in enumerate(self.chord_sequence):
                for k in range(self.bars_per_chord):
                    chord_bar = self.metric[i * self.bars_per_chord + k]
                    for j, beat in enumerate(chord_bar.beats):
                        if self.chord_placement[j] != None:
                            for deg in self.chord_placement[j]:
                                note_to_add = chord[deg] - 7
                                crash = False
                                for x in range(len(beat.sub_beats[0].notes)):
                                    note_to_add_in_scale = self.scale.scaleMIDI[note_to_add]
                                    existing_note_in_scale = self.scale.scaleMIDI[beat.sub_beats[0].notes[x]]
                                    abs_diff = abs(note_to_add_in_scale - existing_note_in_scale)
                                    if abs_diff == 1:
                                        crash = True
                                if not crash:
                                    beat.sub_beats[0].add_note(note_to_add, 2)
                                else:
                                    beat.sub_beats[0].add_note(note_to_add - 7, 2)
