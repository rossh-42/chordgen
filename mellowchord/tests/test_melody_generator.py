from mellowchord import Chord
from mellowchord import KeyedChord
from mellowchord import MelodyGenerator
import pytest


@pytest.fixture
def test_chord_sequence():
    kc1 = KeyedChord('C', Chord(1, 'maj'))
    kc4 = KeyedChord('C', Chord(4, 'maj'))
    kc5 = KeyedChord('C', Chord(5, 'maj'))
    yield [kc1, kc4, kc5]


@pytest.mark.parametrize('notes_per_chord', [1, 2, 3, 4])
def test_melody_generator(longtests, test_chord_sequence, notes_per_chord):
    mg = MelodyGenerator('C', test_chord_sequence, notes_per_chord)
    for notes in mg.gen_sequence():
        total_number_of_notes = len(test_chord_sequence) * notes_per_chord
        assert len(notes) == total_number_of_notes
        if notes_per_chord >= 4 and not longtests:
            continue  # This is too time-consuming to run all the time
        for x in range(total_number_of_notes):
            this_chord_index = x // notes_per_chord
            next_chord_index = this_chord_index + 1
            if x % notes_per_chord == 0 or this_chord_index == len(test_chord_sequence) - 1:
                assert notes[x] in test_chord_sequence[this_chord_index].notes
            else:
                assert notes[x] in test_chord_sequence[this_chord_index].notes + test_chord_sequence[next_chord_index].notes
