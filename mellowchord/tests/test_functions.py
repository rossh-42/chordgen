from mellowchord import Chord
from mellowchord import ChordMap
from mellowchord import KeyedChord
from mellowchord import MellowchordError
from mellowchord import make_file_name_from_chord_sequence
from mellowchord import validate_key
from mellowchord import validate_start
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
        validate_start('Dmaj', cm)
    with pytest.raises(MellowchordError):
        validate_start('foo', cm)


def test_make_file_name_from_chord_sequence():
    kc1 = KeyedChord('C', Chord(1, 'maj'))
    kc4 = KeyedChord('C', Chord(4, 'maj'))
    kc5 = KeyedChord('C', Chord(5, 'maj'))
    assert make_file_name_from_chord_sequence([kc1, kc4, kc5]) == 'Cmaj_Fmaj_Gmaj'
