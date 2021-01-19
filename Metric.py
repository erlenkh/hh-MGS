
class Bar:

    def __init__(self, number_of_beats, number_of_sub_beats):
        self.beats = []
        for i in range(number_of_beats):
            self.beats.append(Beat(number_of_sub_beats))


class Beat:
    def __init__(self, number_of_sub_beats):
        self.sub_beats = []
        for i in range(number_of_sub_beats):
            self.sub_beats.append(SubBeat())


class SubBeat:
    def __init__(self):  # notes is just a list of pitch classes for now
        self.notes = []
        self.durations = []

    def add_note(self, note, duration):
        notes = set(self.notes)
        notes.add( note)
        self.notes = list(notes)
        self.durations.append(duration)
