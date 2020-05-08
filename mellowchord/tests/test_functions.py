import json
from mellowchord import _split_bass
from mellowchord import apply_inversion
from mellowchord import Chord
from mellowchord import ChordMap
from mellowchord import ChordParseError
from mellowchord import IM, IM_3, IM_5, IM7
from mellowchord import iim, iiim, IVM, IVM_1, VM, VM_2, vim
from mellowchord import KeyedChord
from mellowchord import KeyedChordEncoder
from mellowchord import keyed_chord_decoder
from mellowchord import MellowchordError
from mellowchord import make_file_name_from_chord_sequence
from mellowchord import raise_or_lower_an_octave
from mellowchord import scale_from_key_string
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
    with pytest.raises(MellowchordError) as ex:
        validate_start('Bbmin', cm)
    for chord_string in cm.chord_strings:
        assert chord_string in str(ex)
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
        assert string_to_chord(f'{scale[0]}maj', key) == IM
        assert string_to_chord(f'{scale[0]}maj/{scale[2]}', key) == IM_3
        assert string_to_chord(f'{scale[0]}maj/{scale[4]}', key) == IM_5
        assert string_to_chord(f'{scale[1]}min', key) == iim
        assert string_to_chord(f'{scale[2]}min', key) == iiim
        assert string_to_chord(f'{scale[3]}maj', key) == IVM
        assert string_to_chord(f'{scale[3]}maj/{scale[0]}', key) == IVM_1
        assert string_to_chord(f'{scale[4]}maj', key) == VM
        assert string_to_chord(f'{scale[4]}maj/{scale[1]}', key) == VM_2
        assert string_to_chord(f'{scale[5]}min', key) == vim

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
        assert string_to_keyed_chord(f'{scale[0]}maj', key) == KeyedChord(key, IM)
        assert string_to_keyed_chord(f'{scale[0]}maj/{scale[2]}', key) == KeyedChord(key, IM_3)
        assert string_to_keyed_chord(f'{scale[0]}maj/{scale[4]}', key) == KeyedChord(key, IM_5)
        assert string_to_keyed_chord(f'{scale[1]}min', key) == KeyedChord(key, iim)
        assert string_to_keyed_chord(f'{scale[2]}min', key) == KeyedChord(key, iiim)
        assert string_to_keyed_chord(f'{scale[3]}maj', key) == KeyedChord(key, IVM)
        assert string_to_keyed_chord(f'{scale[3]}maj/{scale[0]}', key) == KeyedChord(key, IVM_1)
        assert string_to_keyed_chord(f'{scale[4]}maj', key) == KeyedChord(key, VM)
        assert string_to_keyed_chord(f'{scale[4]}maj/{scale[1]}', key) == KeyedChord(key, VM_2)

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
    for track in ('root', 'third', 'fifth'):
        assert kc.adjusted_notes[track].octave + 1 == kc_up.adjusted_notes[track].octave
    kc_down = raise_or_lower_an_octave(kc, False)
    for track in ('root', 'third', 'fifth'):
        assert kc.adjusted_notes[track].octave - 1 == kc_down.adjusted_notes[track].octave


def test_scale_from_key_string():
    # musthe.Scale lacks a functional __eq__ operator so we must convert to string to compare
    assert str(scale_from_key_string('C')) == str(musthe.Scale('C', 'major'))
    assert str(scale_from_key_string('Cmaj')) == str(musthe.Scale('C', 'major'))
    assert str(scale_from_key_string('Amin')) == str(musthe.Scale('A', 'natural_minor'))
    assert str(scale_from_key_string('Amin(N)')) == str(musthe.Scale('A', 'natural_minor'))
    # assert str(scale_from_key_string('Amin(H)')) == str(musthe.Scale('A', 'harmonic_minor'))
    # assert str(scale_from_key_string('Amin(M)')) == str(musthe.Scale('A', 'melodic_minor'))
    with pytest.raises(ChordParseError):
        scale_from_key_string('foo')


def test_keyed_chord_encoder():
    kc1 = KeyedChord('C', Chord(1, 'maj'))
    kc4 = KeyedChord('C', Chord(4, 'maj'))
    kc5 = KeyedChord('C', Chord(5, 'maj'))
    json_string = json.dumps([kc1, kc4, kc5], cls=KeyedChordEncoder)
    loaded_seq = json.loads(json_string, object_hook=keyed_chord_decoder)
    assert loaded_seq[0] == kc1
    assert loaded_seq[1] == kc4
    assert loaded_seq[2] == kc5


def test_keyed_chord_encoder_with_octave_adjustment():
    kc1 = KeyedChord('C', Chord(1, 'maj'))
    kc1 = raise_or_lower_an_octave(kc1, up=True)
    kc4 = KeyedChord('C', Chord(4, 'maj'))
    kc5 = KeyedChord('C', Chord(5, 'maj'))
    json_string = json.dumps([kc1, kc4, kc5], cls=KeyedChordEncoder)
    loaded_seq = json.loads(json_string, object_hook=keyed_chord_decoder)
    assert loaded_seq[0] == kc1
    assert loaded_seq[1] == kc4
    assert loaded_seq[2] == kc5
