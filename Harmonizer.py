import constraint

chords = {'I': [0, 2, 4],
          'Imaj7': [0, 2, 6, 8],
          'II': [1, 3, 5],
          'III': [2, 4, 6],
          'IV': [0, 3, 5],
          'V': [1, 4, 6],
          'V7': [1, 3, 4, 6],
          'VI': [0, 2, 5],
          'VII': [1, 3, 6],
          }

base_constraints = {'first_or_last_note_in_chord': [True, 6],
                    'first_note_in_chord': [True, 4],
                    'last_note_in_chord': [True, 3],
                    'neighbour_chords_different': [True, 4.5],
                    'notes_overlap_in_neighbour_chords': [True, 2],
                    'all_notes_in_chord': [True, 1],
                    'all_different': [True, 1]
                    }


def harmonize(section):
    bars = section.metric
    bars_per_chord = section.bars_per_chord
    force_fc = section.force_full_cadence

    melody_notes_per_chord = []
    for i, bar in enumerate(bars):
        if i % bars_per_chord == 0:
            # new chord must be created:
            melody_notes_this_chord = []
            for j in range(bars_per_chord):
                melody_notes_this_chord += get_melody_notes(bars[i + j])
            if not melody_notes_this_chord:
                melody_notes_this_chord = melody_notes_per_chord[i-1]
            melody_notes_per_chord.append(melody_notes_this_chord)

    print(melody_notes_per_chord)

    solution, chord_seq = satisfy_constraints(melody_notes_per_chord, base_constraints, force_fc)

    chord_sequence = []
    chord_notes_sequence = []

    for i in range(len(chord_seq)):
        chord_sequence.append(solution[chord_seq[i]])
    print("chord_sequence: ", chord_sequence)

    for i, chord in enumerate(chord_sequence):
        chord_notes_sequence.append(chords[chord])

    return chord_notes_sequence


def get_melody_notes(bar):
    melody_notes = []
    for beat in bar.beats:
        for sub_beat in beat.sub_beats:
            if sub_beat.notes:
                for note in sub_beat.notes:
                    melody_notes.append(note)
    return list(melody_notes)


def satisfy_constraints(melody_notes_per_chord, constraints, force_fc):

    problem = constraint.Problem(constraint.MinConflictsSolver())

    print("force_fc: ", force_fc)

    melody_last_seq = []
    melody_first_seq = []
    melody_first_last_seq = []

    chord_seq = []
    print(melody_notes_per_chord)

    for i in range(int(len(melody_notes_per_chord))):

        last_note = melody_notes_per_chord[i][-1]
        problem.addVariable('melody_bar_last_' + str(i), [last_note])
        melody_last_seq.append('melody_bar_last_' + str(i))

        first_note = melody_notes_per_chord[i][0]
        problem.addVariable('melody_bar_first_' + str(i), [first_note])
        melody_first_seq.append('melody_bar_first_' + str(i))

        problem.addVariable('melody_bar_first_and_last_' + str(i), [first_note, last_note])
        melody_first_last_seq.append('melody_bar_first_and_last_' + str(i))

        if i == 0:
            problem.addVariable('chord_' + str(i), 'I')

        elif i == len(melody_notes_per_chord) - 1 and force_fc:
            problem.addVariable('chord_' + str(i), 'I')

        else:
            problem.addVariable('chord_' + str(i), list(chords.keys()))

        chord_seq.append('chord_' + str(i))

    def note_in_chord(chord, note):
        if note in chords[chord]:
            return True
        if note + 7 in chords[chord]:
            return True
        if note - 7 in chords[chord]:
            return True

    def notes_overlap_in_neighbour_chords(chord_1, chord_2):
        if any(x in chords[chord_1] for x in chords[chord_2]):
            return True

    def chords_different(chord_1, chord_2):
        if chord_1 != chord_2:
            return True

    if constraints['first_or_last_note_in_chord'][0]:
        for i in range(len(chord_seq)):
            problem.addConstraint(note_in_chord, [chord_seq[i], melody_first_last_seq[i]])

    if constraints['last_note_in_chord'][0]:
        for i in range(len(chord_seq)):
            problem.addConstraint(note_in_chord, [chord_seq[i], melody_last_seq[i]])

    if constraints['first_note_in_chord'][0]:
        for i in range(len(chord_seq)):
            problem.addConstraint(note_in_chord, [chord_seq[i], melody_first_seq[i]])

    if constraints['notes_overlap_in_neighbour_chords'][0]:
        for i in range(len(chord_seq) - 1):
            problem.addConstraint(notes_overlap_in_neighbour_chords, [chord_seq[i], chord_seq[i + 1]])

    if constraints['neighbour_chords_different'][0]:
        for i in range(len(chord_seq) - 1):
            problem.addConstraint(chords_different, [chord_seq[i], chord_seq[i + 1]])

    if constraints['all_different'][0]:
        problem.addConstraint(constraint.AllDifferentConstraint())

    solution = problem.getSolution()

    if solution:
        print("solution found!")
        sol = solution
        return sol, chord_seq

    else:
        print("No solutions available... relaxing lowest priority constraint:")
        constraints = relax_lowest_priority_constraint(constraints)
        print("new constraints, ", constraints)
        return satisfy_constraints(melody_notes_per_chord, constraints, force_fc)


def relax_lowest_priority_constraint(constraints):
    # create dictionary of every activated constraint
    activated_constraints = {}
    for constr, info in constraints.items():
        value = constraints[constr]
        activated = value[0]
        if activated:
            activated_constraints[constr] = info

    # find activated_constraint with lowest priority and deactivate:
    if activated_constraints:
        lowest_priority_constr = min(activated_constraints, key=lambda k: activated_constraints[k])
        lowest_priority_constr_priority = constraints[lowest_priority_constr][1]

        constraints[lowest_priority_constr] = [False, lowest_priority_constr_priority]

    return constraints



