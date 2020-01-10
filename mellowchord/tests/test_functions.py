from mellowchord import _split_bass
from mellowchord import apply_inversion
from mellowchord import Chord
from mellowchord import ChordMap
from mellowchord import ChordParseError
from mellowchord import IM, IM_3, IM_5, IM7
from mellowchord import iim, iiim, IVM, IVM_1, VM, VM_2, vim
from mellowchord import KeyedChord
from mellowchord import MellowchordError
from mellowchord import make_file_name_from_chord_sequence
from mellowchord import raise_or_lower_an_octave
from mellowchord import string_to_chord
from mellowchord import string_to_keyed_chord
from mellowchord import validate_key
from mellowchord import validate_start
import musthe
import pytest


def test_validate_key():
    validate_key('C')
    validate_key('D#')
    validate_key('Bb')
    with pytest.raises(MellowchordError):
        validate_key('foo')


def test_validate_start():
    cm = ChordMap('C')
    validate_start('Cmaj', cm)
    with pytest.raises(MellowchordError):
        validate_start('Bbmin', cm)
    with pytest.raises(MellowchordError):
        validate_start('foo', cm)


def test_make_file_name_from_chord_sequence():
    kc1 = KeyedChord('C', Chord(1, 'maj'))
    kc4 = KeyedChord('C', Chord(4, 'maj'))
    kc5 = KeyedChord('C', Chord(5, 'maj'))
    assert make_file_name_from_chord_sequence([kc1, kc4, kc5]) == 'Cmaj_Fmaj_Gmaj'


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
