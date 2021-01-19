import random


class Scale:

    scales = {'major': [2, 2, 1, 2, 2, 2, 1],
              'minor': [2, 1, 2, 2, 1, 2, 2],
              'dorian': [2, 1, 2, 2, 2, 1, 2],
              'custom': [2, 1, 1, 2, 2, 1, 2]
              }

    scale_probs = [0.4, 0.4, 0.15, 0.05]

    chromatic_scale = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

    def __init__(self, tonic, scale_type):
        self.tonic = tonic
        self.tonic_index = Scale.chromatic_scale.index(self.tonic)
        self.scale_type = scale_type
        self.scale_indexes, self.scale = self.build_scale(self.tonic_index, self.scale_type)
        self.scaleMIDI = self.create_MIDI_pitch_numbers()

    @classmethod
    def random(cls):
        tonic = random.choice(Scale.chromatic_scale)
        scale_type = random.choices(list(Scale.scales.keys()), Scale.scale_probs, k=1)[0]
        return cls(tonic, scale_type)

    def create_MIDI_pitch_numbers(self):
        scale = self.scale_indexes
        scale.pop()
        scale_octaves = [x - 36 for x in scale] + [x - 24 for x in scale] + [x - 12 for x in scale] + scale + [x + 12 for x in scale] + [x + 24 for x in scale] + [x + 36 for x in scale] + [x + 48 for x in scale]
        scale_midi = [x + 36 for x in scale_octaves]
        return scale_midi

    @staticmethod
    def build_scale(tonic_index, scale_type):
        scale_steps = Scale.scales[scale_type]
        scale_indexes = [tonic_index]

        for i in range(len(scale_steps)):
            next_note = scale_indexes[i] + scale_steps[i]
            scale_indexes.append(next_note)

        scale = []
        for i in range(len(scale_indexes)):
            scale.append(Scale.chromatic_scale[scale_indexes[i] % 12])
        return scale_indexes, scale
