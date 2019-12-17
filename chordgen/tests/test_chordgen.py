from chordgen import _ChordGraphNode
from chordgen import Chord
from chordgen import ChordMap
from chordgen import KeyedChord
from chordgen import IM, IM_3, IM_5, IM7
from chordgen import iim
from chordgen import iiim
from chordgen import IVM, IVM_1
from chordgen import VM, VM_1
from chordgen import vim
from chordgen import chords_types_are_equal
import musthe


def chord_in(chord_root_note, chord_type, list_of_chords):
    """Return true if the chord represented by chord_string is in
    the given list of musthe.Chord objects.
    """
    for chord in list_of_chords:
        if str(chord.notes[0]) == chord_root_note:
            if chords_types_are_equal(chord.chord_type, chord_type):
                return True
    return False


def test_major_chord():
    c = Chord(1, 'M')
    assert c.degree == 1
    assert c.bass is None
    assert c.name() == 'IM'


def test_chord_aliases_equal():
    c1 = Chord(1, 'M')
    c2 = Chord(1, 'maj')
    assert c1 == c2


def test_minor_chord():
    c = Chord(3, 'm')
    assert c.degree == 3
    assert c.bass is None
    assert c.name() == 'iiim'


def test_slash_chord():
    c = Chord(4, 'M', bass=1)
    assert c.degree == 4
    assert c.bass == 1
    assert c.name() == 'IVM/1'


def test_node_name():
    c = Chord(1, 'M')
    node = _ChordGraphNode([c])
    assert node.__repr__() == '(IM)'


def test_keyed_chord():
    c = Chord(1, 'M')
    kc = KeyedChord('C', c)
    assert len(kc.notes) == 3
    assert kc.notes[0] == musthe.Note('C')
    assert kc.notes[1] == musthe.Note('E')
    assert kc.notes[2] == musthe.Note('G')


def test_map():
    cm = ChordMap()
    set([IVM_1, VM_1])
    assert set(cm.next_chords(IM)) == set([IVM_1, VM_1])
    assert set(cm.next_chords(IM_3)) == set([iim])
    assert set(cm.next_chords(IM_5)) == set([])
    assert set(cm.next_chords(iim)) == set([IM_5, iiim, VM])
    assert set(cm.next_chords(iiim)) == set([IM, IVM, vim])
    assert set(cm.next_chords(IVM)) == set([IM, IM_3, IM_5, iim, VM])
    assert set(cm.next_chords(IVM_1)) == set([IM])
    assert set(cm.next_chords(VM)) == set([IM, iiim, vim])
    assert set(cm.next_chords(VM_1)) == set([IM])
    assert set(cm.next_chords(vim)) == set([iim, IVM])


def test_map_C():
    cm = ChordMap('C')
    next_chords = cm.next_chords(IM)
    assert chord_in('F', 'maj', next_chords)
    assert chord_in('G', 'maj', next_chords)
    next_chords = cm.next_chords(iim)
    assert chord_in('G', 'maj', next_chords)
    assert chord_in('E', 'min', next_chords)
    assert chord_in('C', 'maj', next_chords)


def test_map_B_flat():
    cm = ChordMap('Bb')
    next_chords = cm.next_chords(IM)
    assert chord_in('Eb', 'maj', next_chords)
    assert chord_in('F', 'maj', next_chords)


def test_next():
    cm = ChordMap()
    after_iiim = cm.next_chords(iiim)
    assert IM in after_iiim
    assert IVM in after_iiim
    assert vim in after_iiim
    assert IM7 not in after_iiim


def test_next_all_variants():
    cm = ChordMap()
    after_iiim = cm.next_chords(iiim, all_variants=True)
    assert IM in after_iiim
    assert IVM in after_iiim
    assert vim in after_iiim
    assert IM7 in after_iiim


def test_next_chords_string():
    cm = ChordMap('C')
    next_chords = cm.next_chords('Cmaj')
    assert chord_in('F', 'maj', next_chords)
    assert chord_in('G', 'maj', next_chords)


def test_simple_sequence():
    cm = ChordMap('C')
    next_chords = cm.next_chords('Cmaj')
    next_chords = cm.next_chords(next_chords[0])
    next_chords = cm.next_chords(next_chords[0])


def test_gen_sequence():
    cm = ChordMap('C')
    for seq in cm.gen_sequence('Cmaj', 3):
        assert len(seq) == 3
        assert seq[0] == 'Cmaj'
        assert seq[1] in ('Fmaj', 'Gmaj')
        assert seq[2] in ('Cmaj', 'Cmaj7')
