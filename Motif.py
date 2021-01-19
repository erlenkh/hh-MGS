import random
import math


class Motif:

    scale_intervals = {'unison': 0,
                       'step': 1,
                       'third': 2,
                       'fourth': 3,
                       'fifth': 4,
                       'sixth': 5,
                       'seventh': 6,
                       'octave': 7,
                       }

    shapes = {'up': [1, 1],
              'down': [-1, -1],
              'hat': [1, -1],
              'v': [-1, 1],
              }

    def __init__(self, length, shape, directions, notes, intervals, transpostions, inverted, retrograded):
        self.length = length
        self.shape = shape
        self.directions = directions
        self.notes = notes
        self.intervals = intervals
        self.transposition = transpostions
        self.inverted = inverted
        self.retrograded = retrograded

    @classmethod
    def generate_new(cls, length, first_note, markov_probs):
        shape = random.choice(list(Motif.shapes.items()))
        directions = cls.make_directions(shape, length)
        transposition = 0
        inverted = False
        retrograded = False
        # first_note = 0
        notes, intervals = cls.generate(length, directions, first_note, markov_probs)
        return cls(length, shape, directions, notes, intervals, transposition, inverted, retrograded)

    @classmethod
    def generate_new_staircase_motif(cls, length, first_note, markov_probs):
        # length = random.randint(3, 7) #used to be 3-5
        shape = random.choice([('hat',Motif.shapes['hat']),('v', Motif.shapes['v'])])
        directions = cls.make_directions(shape, length)
        transposition = 0
        inverted = False
        retrograded = False
        # first_note = 0
        notes, intervals = cls.generate(length, directions, first_note, markov_probs)
        return cls(length, shape, directions, notes, intervals, transposition, inverted, retrograded)


    @classmethod
    def generate_from_motif(cls, motif_orig, markov_probs):
        length = motif_orig.length #+ random.randint(1,2)
        shape = motif_orig.shape
        directions = cls.make_directions(shape, length)
        transposition = motif_orig.transposition
        inverted = motif_orig.inverted
        retrograded = motif_orig.retrograded
        first_note = motif_orig.notes[0]
        notes, intervals = cls.generate(length, directions, first_note, markov_probs)

        return cls(length, shape, directions, notes, intervals, transposition, inverted, retrograded)

    @classmethod
    def generate_empty_motif(cls):
        length = 0
        shape = None
        directions = []
        transposition = 0
        inverted = False
        retrograded = False
        # first_note = 0
        notes = []
        intervals = []
        return cls(length, shape, directions, notes, intervals, transposition, inverted, retrograded)

    def random_operations(self, probabilities):
        if random.uniform(0, 1) < probabilities['transpose']:
            self.transpose(random.randint(-2, 2))
        if random.uniform(0, 1) < probabilities['invert']:
            self.invert()
        if random.uniform(0, 1) < probabilities['retrograde']:
            self.retrograde()

    def transpose(self, steps):
        for i in range(self.length):
            self.notes[i] += steps
        self.transposition += steps
        return self

    def transpose_last_note(self, steps):
        self.notes[self.length - 1] += steps
        self.intervals[self.length - 1] += steps

    def invert(self):
        self.intervals = [element * -1 for element in self.intervals]
        first_note = self.notes[0]
        notes = [first_note]
        for i in range(self.length - 1):
            next_note = notes[i] + self.intervals[i]
            notes.append(next_note)
        self.notes = notes
        self.inverted = not self.inverted

    def retrograde(self):
        self.notes.reverse()
        self.intervals.reverse()
        self.retrograded = not self.retrograded
        return self

    def make_weak_cadence(self):
        next_to_last = self.notes[self.length - 2]
        if next_to_last >= 2:
            self.notes[self.length-1] = random.choice([4, 6])  # make last note either 5th or 7th (create suspension)
        if next_to_last < 2:
            self.notes[self.length - 1] = random.choice([-3, -1])

        return self

    def make_strong_cadence(self):
        last_note = self.notes[-1]
        self.notes[-1] = int(round(last_note / 7.0) * 7.0)  # makes final note tonic
        return self


    @staticmethod
    def generate(length, directions, first_note, markov_probs):
        notes = [first_note]
        intervals = []
        for i in range(length - 1):
            next_interval = random.choices(list(Motif.scale_intervals.keys()), weights=markov_probs, k=1)[0]
            next_interval_number = Motif.scale_intervals[next_interval]
            direction = directions[i]
            intervals.append(next_interval_number * direction)
            next_note = notes[i] + next_interval_number * direction
            notes.append(next_note)

        return notes, intervals


    @staticmethod
    def make_directions(shape, length):
        shape = shape[1]
        if length % 2 == 0:
            directions1 = [shape[0]] * int(length/2 - 1) + [shape[1]] * int(length/2)
            directions2 = [shape[0]] * int(length/2) + [shape[1]] * int(length/2 - 1)
            directions = random.choice([directions1, directions2])
        else:
            directions = [shape[0]] * math.floor(length/2) + [shape[1]] * math.floor(length/2)
        return directions
