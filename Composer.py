import random
import math
from Motif import Motif
from Section import Section
from Scale import Scale
from midiutil import MIDIFile
from copy import deepcopy


class Composer:

    def __init__(self, seed):

        self.name = str(seed)
        random.seed(seed)

        # Generate general characteristics of composition:
        self.tempo = int(random.uniform(90, 160))
        self.scale = Scale.random()
        self.general_structure = self.generate_general_structure()

        # Generate metric info:
        self.beats_per_bar = random.choices([3, 4], [0.3, 0.7], k=1)[0]
        self.sub_beats_per_beat = 4

        # Generate melodic info:
        self.motif_trans_probs = {'transpose': random.gauss(0.5, 0.1),
                                  'retrograde': random.gauss(0.2, 0.1),
                                  'invert': random.gauss(0.2, 0.1),
                                  }
        self.motif_markov_probs = [0.7, 0.7, 0.15, 0.05, 0.08, 0.05, 0.05, 0.05]
        self.base_motif_changes_per_new_section = random.choice([3, 4])

        self.bm_first_note = random.choice([0, 2, 4])
        self.bm_length = random.randint(3, 6)
        self.base_motif = Motif.generate_new(self.bm_length, self.bm_first_note, self.motif_markov_probs)

        if self.bm_length > 4:
            self.motif_note_dur = 1
        else:
            self.motif_note_dur = random.choices([1, 2], [0.7, 0.3], k=1)[0]

        self.offset = int(random.gauss(0, 1.3))

        min_bars_per_motif = math.ceil((self.bm_length + self.offset) * self.motif_note_dur / self.beats_per_bar)

        if min_bars_per_motif == 3:
            self.bars_per_motif = 4
        elif min_bars_per_motif > 4:
            self.bars_per_motif = 8
        else:
            self.bars_per_motif = min_bars_per_motif

        # generate the melodic outline (main motif and melodic structure) of each unique section:
        self.unique_sections_mo = self.gen_sections_mo()

        # SECTION DICTS:
        self.chord_info = {'bars_per_chord': random.choice([1, 2]),
                           'chord_pattern': self.generate_chord_pattern(),
                           'write_chords': True,
                           'force_full_cadence': False
                           }

        self.metric_info = {'beats_per_bar': self.beats_per_bar,
                            'sub_beats_per_beat': self.sub_beats_per_beat
                            }

        self.melodic_info = {'main_motif': self.base_motif,
                             'melodic_structure': self.unique_sections_mo['A'][1],
                             'motif_trans_probs': self.motif_trans_probs,
                             'motif_markov_probs': self.motif_markov_probs,
                             'motif_note_dur': self.motif_note_dur,
                             'motif_offset': self.offset,
                             'bars_per_motif': self.bars_per_motif,
                             'octave': random.choices([0, 7], [0.75, 0.25], k=1)[0],
                             'arp': random.choices([[None, None, None], self.generate_arp()], [0.75, 0.25], k=1)[0],
                             'write_melody': True,
                             'scale': self.scale
                             }

        print("scale: ", self.scale.tonic, self.scale.scale_type)

        # generate each unique section:

        self.sections_dict = self.generate_sections()

        self.structure = []
        for i, section in enumerate(self.general_structure):
            self.structure.append(self.sections_dict[i])

        self.bars = []
        for section in self.structure:
            self.bars += section.metric

        # write full composition in metric representation to MIDI
        self.to_midi()

        print(self.__dict__)

    def gen_sections_mo(self):  # generate a melodic outline (mo) for each unique section
        unique_sections = list(set(self.general_structure))
        unique_sections.sort()
        unique_sections_mo = {}

        sections_structures = self.generate_melody_structures()
        for i, section in enumerate(unique_sections):
            if i == 0:
                section_main_motif = self.base_motif
            else:
                section_main_motif = deepcopy(self.base_motif)
                for j in range(self.base_motif_changes_per_new_section):
                    section_main_motif.random_operations(self.motif_trans_probs)

            unique_sections_mo[section] = [section_main_motif, sections_structures[i]]
        return unique_sections_mo

    def generate_sections(self):
        sections_dict = {}
        self.melodic_info['write_melody'] = True

        for i, section in enumerate(self.general_structure):

            self.melodic_info['main_motif'] = self.unique_sections_mo[section][0]
            self.melodic_info['melodic_structure'] = self.unique_sections_mo[section][1]

            if i == len(self.general_structure) - 1:
                self.chord_info['force_full_cadence'] = True

            # example of how section info can be changed before section generation:
            if i % 2 == 0 and i > 0:
                # self.melodic_info['arp'] = self.generate_arp()
                self.chord_info['chord_pattern'] = self.generate_chord_pattern()

            sections_dict[i] = Section(self.melodic_info, self.chord_info, self.metric_info)

        return sections_dict

    def generate_melody_structures(self):  # selection from pre-made list of candidates (with certain conditions)
        period = ['main_motif', 'main_motif_weak_cadence', 'main_motif', 'main_motif_strong_cadence']
        weak_sentence = ['main_motif', 'main_motif', 'main_motif_trans', 'main_motif_weak_cadence']
        strong_sentence = ['main_motif', 'main_motif', 'main_motif_trans', 'main_motif_strong_cadence']

        s1 = ['new_motif', 'new_motif', 'new_motif', 'main_motif_strong_cadence']
        s2 = ['staircase']

        section_structures = []
        unique_sections = list(set(self.general_structure))
        unique_sections.sort()
        for i, section in enumerate(unique_sections):
            if section == self.general_structure[-1]:  # last section must end on strong cadence
                section_structures.append(random.choice([period, strong_sentence]))
            elif section == self.general_structure[0]:  # first section must be a little safe
                section_structures.append(random.choice([period, weak_sentence, strong_sentence]))
            else:
                if self.beats_per_bar == 4:
                    section_structures.append(random.choice([period, weak_sentence, strong_sentence, s2]))
                else:
                    section_structures.append(random.choice([period, weak_sentence, strong_sentence, s1]))

        return section_structures

    def generate_chord_pattern(self):  # selection from pre-made list of candidates
        # in 4/4 time:
        ffp1 = [[0, 1, 2], None, [0, 1, 2], None]
        ffp2 = [[0, 1, 2], [0], [0, 1, 2], [0]]
        ffp3 = [[0, 2], [0], [0, 2], [0]]
        ffp4 = [[0], [1], [2], [1]]
        ffp4 = [[0], [0], [0, 1, 2], [0]]
        ffp = [ffp1, ffp2, ffp3, ffp4]

        # in 3/4 time:
        tfp1 = [[0], [1], [2]]
        tfp2 = [[0], [1, 2], None]
        tfp3 = [[0, 1, 2], None, None]
        tfp4 = [[0, 1, 2], None, [0]]
        tfp = [tfp1, tfp2, tfp3, tfp4]

        if self.beats_per_bar == 3:
            return random.choice(tfp)
        if self.beats_per_bar == 4:
            return random.choice(ffp)

    def generate_arp(self):  # selection from pre-made list of candidates
        arp_b = int(random.gauss(0, 3))
        arp1 = [None, arp_b, None]
        arp2 = [arp_b, arp_b, arp_b]
        arp3 = [0, 0, 0]
        arp4 = [None, 0, None]
        arp5 = [arp_b + int(random.gauss(0,3)), arp_b, arp_b + int(random.gauss(0,3))]

        arps = [arp1, arp2, arp3, arp4, arp5]
        arp_probs = [0.4, 0.04, 0.01, 0.01,  0.05]

        return random.choices(arps, arp_probs, k=1)[0]

    @staticmethod
    def generate_general_structure():  # selection from pre-made list of candidates
        s_1 = ['A', 'B', 'A', 'C', 'A']
        s_2 = ['A', 'B', 'A', 'B']
        s_3 = ['A', 'A', 'B', 'A']
        structs = [s_1, s_2, s_3]
        return random.choice(structs)

    def to_midi(self):
        track = 0
        time = 0  # In beats
        volume = 40

        composition_midi = MIDIFile(2)

        composition_midi.addTempo(track, time, self.tempo)
        composition_midi.addTimeSignature(track, time, self.beats_per_bar, 2, 1)
        composition_midi.addTrackName(0, 0, self.name)

        c = 0  # octave correction. random chance of pitching entire composition down an octave
        if random.choices([True, False], [0.7, 0.3], k=1)[0]:
            c = -12

        stut = 0  # rhythmic stutter to allow for a more "natural" rhythm
        scale_MIDI_indexes = self.scale.scaleMIDI

        for i, bar in enumerate(self.bars):
            bar_number = i
            for j, beat in enumerate(bar.beats):
                beat_number = j + bar_number * self.beats_per_bar
                for k, sub_beat in enumerate(beat.sub_beats):
                    sub_beat_number = k + beat_number * self.sub_beats_per_beat
                    if sub_beat.notes:
                        volume = abs(volume + random.randint(-3, 3))
                        # (should be improved in future to avoid re-use of code):
                        if self.beats_per_bar % 2 == 0:  # emphasize every second beat
                            for i, note in enumerate(sub_beat.notes):
                                stut = stut + random.uniform(-0.01, 0.01)
                                dur = sub_beat.durations[i]
                                if beat_number % 2 == 0 and sub_beat_number % 4 == 0:
                                    composition_midi.addNote(0, 0, scale_MIDI_indexes[note + 21] + 24 + c,
                                                             abs(sub_beat_number / self.sub_beats_per_beat + stut), dur,
                                                             volume + 20)
                                else:
                                    composition_midi.addNote(0, 0, scale_MIDI_indexes[note + 21] + 24 + c,
                                                             abs(sub_beat_number / self.sub_beats_per_beat + stut), dur,
                                                             volume)

                        else:  # waltz time. emphasize second and third beat.
                            for i, note in enumerate(sub_beat.notes):
                                stut = stut + random.uniform(-0.01, 0.01)
                                dur = sub_beat.durations[i]
                                if beat_number % 3 == 0 and sub_beat_number % 4 == 0:
                                    composition_midi.addNote(0, 0, scale_MIDI_indexes[note + 21] + 24 + c,
                                                             abs(sub_beat_number / self.sub_beats_per_beat + stut), dur,
                                                             volume)
                                else:
                                    composition_midi.addNote(0, 0, scale_MIDI_indexes[note + 21] + 24 + c,
                                                             abs(sub_beat_number / self.sub_beats_per_beat + stut), dur,
                                                             volume + 20)

        with open("composition.mid", "wb") as output_file:
            composition_midi.writeFile(output_file)