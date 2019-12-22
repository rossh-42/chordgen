from mellowchord import ChordMap
from mellowchord import MellowchordError
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
