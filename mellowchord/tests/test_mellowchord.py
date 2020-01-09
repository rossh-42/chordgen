from mellowchord import apply_inversion
from mellowchord import _split_bass
from mellowchord import string_to_chord
from mellowchord import string_to_keyed_chord
from mellowchord import _ChordGraphNode
from mellowchord import Chord
from mellowchord import ChordMap
from mellowchord import ChordParseError
from mellowchord import KeyedChord
from mellowchord import IM, IM_3, IM_5, IM7
from mellowchord import iim
from mellowchord import iiim
from mellowchord import IVM, IVM_1
from mellowchord import VM, VM_2
from mellowchord import vim
from mellowchord import MidiFile
from mellowchord import raise_or_lower_an_octave
import mido
import musthe
import pytest


def chord_in(chord_string, list_of_chords):
    """Return true if the chord represented by chord_string is in
    the given list of musthe.Chord objects.
    """
    for chord in list_of_chords:
        if chord_string == str(chord):
            return True
    return False


def test_major_chord():
    c = Chord(1, 'maj')
    assert c.degree == 1
    assert c.inversion is None
    assert c.name() == 'Imaj'


def test_chord_aliases_equal():
    c1 = Chord(1, 'M')
    c2 = Chord(1, 'maj')
    assert c1 == c2


def test_minor_chord():
    c = Chord(3, 'min')
    assert c.degree == 3
    assert c.inversion is None
    assert c.name() == 'iiimin'


def test_chord_with_inversion():
    c = Chord(4, 'maj', inversion=2)
    assert c.degree == 4
    assert c.inversion == 2
    assert c.name() == 'IVmaj/1'
    c = Chord(4, 'maj', inversion=1)
    assert c.degree == 4
    assert c.inversion == 1
    assert c.name() == 'IVmaj/6'


def test_node_name():
    c = Chord(1, 'maj')
    node = _ChordGraphNode([c])
    assert node.__repr__() == '(Imaj)'


def test_keyed_chord():
    c = Chord(1, 'maj')
    kc = KeyedChord('C', c)
    assert len(kc.notes) == 3
    assert kc.notes[0] == musthe.Note('C')
    assert kc.notes[1] == musthe.Note('E')
    assert kc.notes[2] == musthe.Note('G')
    assert kc.scientific_notation() == 'C4 E4 G4'
    assert kc.inversion is None


def test_keyed_chord_seventh():
    c = Chord(1, 'maj7')
    kc = KeyedChord('C', c)
    assert len(kc.notes) == 4
    assert kc.notes[0] == musthe.Note('C')
    assert kc.notes[1] == musthe.Note('E')
    assert kc.notes[2] == musthe.Note('G')
    assert kc.notes[3] == musthe.Note('B')
    assert kc.scientific_notation() == 'C4 E4 G4 B4'
    assert kc.inversion is None


def test_keyed_chord_with_inversion():
    c = Chord(1, 'maj', inversion=2)
    kc = KeyedChord('C', c)
    assert len(kc.notes) == 3
    assert kc.notes[0] == musthe.Note('C')
    assert kc.notes[1] == musthe.Note('E')
    assert kc.notes[2] == musthe.Note('G')
    assert kc.scientific_notation() == 'G3 C4 E4'
    assert kc.name() == 'Cmaj/G'
    c = Chord(1, 'maj', inversion=1)
    kc = KeyedChord('C', c)
    assert len(kc.notes) == 3
    assert kc.notes[0] == musthe.Note('C')
    assert kc.notes[1] == musthe.Note('E')
    assert kc.notes[2] == musthe.Note('G')
    assert kc.scientific_notation() == 'E4 G4 C5'
    assert kc.name() == 'Cmaj/E'


def test_keyed_chord_midi():
    midi_file = MidiFile('test.mid')
    kc1 = KeyedChord('C', Chord(1, 'maj7'))
    midi_file.add_chord(kc1)
    kc4 = KeyedChord('C', Chord(4, 'maj'))
    midi_file.add_chord(kc4)
    kc5 = KeyedChord('C', Chord(5, 'maj'))
    midi_file.add_chord(kc5)
    midi_file.write()
    kc2 = KeyedChord('C', Chord(2, 'min'))
    midi_file.add_chord(kc2)
    midi_file.write()

    # Assert that there's only one ALL_SOUNDS_OFF at the end
    mido_file = mido.MidiFile('test.mid')
    assert mido_file.tracks[0][-1] == mido.MetaMessage('end_of_track')
    assert mido_file.tracks[0][-2] == MidiFile.ALL_SOUNDS_OFF
    assert mido_file.tracks[0][-3] != MidiFile.ALL_SOUNDS_OFF


def test_map():
    cm = ChordMap()
    set([IVM_1, VM_2])
    assert set(cm.next_chords(IM)) == set([IVM_1, VM_2])
    assert set(cm.next_chords(IM_3)) == set([iim])
    assert set(cm.next_chords(IM_5)) == set([])
    assert set(cm.next_chords(iim)) == set([IM_5, iiim, VM])
    assert set(cm.next_chords(iiim)) == set([IM, IVM, vim])
    assert set(cm.next_chords(IVM)) == set([IM, IM_3, IM_5, iim, VM])
    assert set(cm.next_chords(IVM_1)) == set([IM])
    assert set(cm.next_chords(VM)) == set([IM, iiim, vim])
    assert set(cm.next_chords(VM_2)) == set([IM])
    assert set(cm.next_chords(vim)) == set([iim, IVM])


def test_map_C():
    cm = ChordMap('C')
    next_chords = cm.next_chords(IM)
    assert chord_in('Fmaj/C', next_chords)
    assert chord_in('Gmaj/D', next_chords)
    next_chords = cm.next_chords(iim)
    assert chord_in('Gmaj', next_chords)
    assert chord_in('Emin', next_chords)
    assert chord_in('Cmaj/G', next_chords)


def test_map_B_flat():
    cm = ChordMap('Bb')
    next_chords = cm.next_chords(IM)
    assert chord_in('Ebmaj/Bb', next_chords)
    assert chord_in('Fmaj/C', next_chords)


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
    assert chord_in('Fmaj/C', next_chords)
    assert chord_in('Gmaj/D', next_chords)


def test_simple_sequence():
    cm = ChordMap('C')
    next_chords = cm.next_chords('Cmaj')
    next_chords = cm.next_chords(next_chords[0])
    next_chords = cm.next_chords(next_chords[0])


def test_gen_sequence():
    cm = ChordMap('C')
    for seq in cm.gen_sequence('Cmaj', 3):
        assert len(seq) == 3
        assert str(seq[0]) == 'Cmaj'
        assert str(seq[1]) in ('Fmaj/C', 'Gmaj/D')
        assert str(seq[2]) in ('Cmaj', 'Cmaj7')


def test_split_bass():
    assert _split_bass('Cmaj') == ('Cmaj', None)
    assert _split_bass('Cmaj/1') == ('Cmaj', 1)
    with pytest.raises(ChordParseError):
        _split_bass('Cmaj/C')
    assert _split_bass('Cmaj/C', 'C') == ('Cmaj', 1)
    with pytest.raises(ChordParseError):
        _split_bass('Fmaj/F')
    assert _split_bass('Fmaj/F', 'C') == ('Fmaj', 4)

    assert _split_bass('IV/1') == ('IV', 1)
    assert _split_bass('V/1') == ('V', 1)


def test_string_to_chord_keyless():
    assert string_to_chord('IM') == IM
    assert string_to_chord('IM/3') == IM_3
    assert string_to_chord('IM/5') == IM_5
    assert string_to_chord('IM7') == IM7
    assert string_to_chord('iim') == iim
    assert string_to_chord('iiim') == iiim
    assert string_to_chord('IVM') == IVM
    assert string_to_chord('IVM/1') == IVM_1
    assert string_to_chord('VM') == VM
    assert string_to_chord('VM/2') == VM_2
    assert string_to_chord('vim') == vim


def test_string_to_chord():
    for note in musthe.Note.all():
        key = str(note)
        scale = musthe.Scale(key, 'major')
        assert string_to_chord('{}maj'.format(scale[0]), key) == IM
        assert string_to_chord('{}maj/{}'.format(scale[0], scale[2]), key) == IM_3
        assert string_to_chord('{}maj/{}'.format(scale[0], scale[4]), key) == IM_5
        assert string_to_chord('{}min'.format(scale[1]), key) == iim
        assert string_to_chord('{}min'.format(scale[2]), key) == iiim
        assert string_to_chord('{}maj'.format(scale[3]), key) == IVM
        assert string_to_chord('{}maj/{}'.format(scale[3], scale[0]), key) == IVM_1
        assert string_to_chord('{}maj'.format(scale[4]), key) == VM
        assert string_to_chord('{}maj/{}'.format(scale[4], scale[1]), key) == VM_2
        assert string_to_chord('{}min'.format(scale[5]), key) == vim

        with pytest.raises(ChordParseError):
            string_to_chord('Hmaj', key)
        with pytest.raises(ChordParseError):
            string_to_chord('Afoo', key)
        with pytest.raises(ChordParseError):
            string_to_chord('Amin/foo', key)
        with pytest.raises(ChordParseError):
            string_to_chord('Amin/8', key)


def test_string_to_keyed_chord():
    for note in musthe.Note.all():
        key = str(note)
        scale = musthe.Scale(key, 'major')
        assert string_to_keyed_chord('{}maj'.format(scale[0]), key) == KeyedChord(key, IM)
        assert string_to_keyed_chord('{}maj/{}'.format(scale[0], scale[2]), key) == KeyedChord(key, IM_3)
        assert string_to_keyed_chord('{}maj/{}'.format(scale[0], scale[4]), key) == KeyedChord(key, IM_5)
        assert string_to_keyed_chord('{}min'.format(scale[1]), key) == KeyedChord(key, iim)
        assert string_to_keyed_chord('{}min'.format(scale[2]), key) == KeyedChord(key, iiim)
        assert string_to_keyed_chord('{}maj'.format(scale[3]), key) == KeyedChord(key, IVM)
        assert string_to_keyed_chord('{}maj/{}'.format(scale[3], scale[0]), key) == KeyedChord(key, IVM_1)
        assert string_to_keyed_chord('{}maj'.format(scale[4]), key) == KeyedChord(key, VM)
        assert string_to_keyed_chord('{}maj/{}'.format(scale[4], scale[1]), key) == KeyedChord(key, VM_2)

        with pytest.raises(ChordParseError):
            string_to_keyed_chord('Hmaj', key)
        with pytest.raises(ChordParseError):
            string_to_keyed_chord('Afoo', key)
        with pytest.raises(ChordParseError):
            string_to_keyed_chord('Amin/foo', key)
        with pytest.raises(ChordParseError):
            string_to_keyed_chord('Amin/8', key)


def test_apply_inversion():
    kc = KeyedChord('C', Chord(1, 'maj'))
    kc_1 = apply_inversion(kc, 1)
    assert kc_1.inversion == 1
    kc_2 = apply_inversion(kc, 2)
    assert kc_2.inversion == 2
    kc_0 = apply_inversion(kc_2, 0)
    assert kc_0.inversion is None


def test_raise_or_lower_an_octave():
    kc = KeyedChord('C', Chord(1, 'maj'))
    kc_up = raise_or_lower_an_octave(kc, True)
    for index, note in enumerate(kc_up.notes):
        assert note.octave == kc.notes[index].octave + 1
    kc_down = raise_or_lower_an_octave(kc, False)
    for index, note in enumerate(kc_down.notes):
        assert note.octave == kc.notes[index].octave - 1
