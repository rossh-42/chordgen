from mellowchord import _ChordGraphNode
from mellowchord import Chord
from mellowchord import KeyedChord
from mellowchord import MidiFile
import mido
import musthe


def test_major_chord():
    c = Chord(1, 'maj')
    assert c.degree == 1
    assert c.inversion is None
    assert c.name == 'Imaj'


def test_chord_aliases_equal():
    c1 = Chord(1, 'M')
    c2 = Chord(1, 'maj')
    assert c1 == c2


def test_minor_chord():
    c = Chord(3, 'min')
    assert c.degree == 3
    assert c.inversion is None
    assert c.name == 'iiimin'


def test_chord_with_inversion():
    c = Chord(4, 'maj', inversion=2)
    assert c.degree == 4
    assert c.inversion == 2
    assert c.name == 'IVmaj/1'
    c = Chord(4, 'maj', inversion=1)
    assert c.degree == 4
    assert c.inversion == 1
    assert c.name == 'IVmaj/6'


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
    assert kc == KeyedChord('C', c)
    assert kc != KeyedChord('C', Chord(2, 'min'))


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
    assert kc.name == 'Cmaj/G'
    c = Chord(1, 'maj', inversion=1)
    kc = KeyedChord('C', c)
    assert len(kc.notes) == 3
    assert kc.notes[0] == musthe.Note('C')
    assert kc.notes[1] == musthe.Note('E')
    assert kc.notes[2] == musthe.Note('G')
    assert kc.scientific_notation() == 'E4 G4 C5'
    assert kc.name == 'Cmaj/E'


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
    assert mido_file.tracks[0][-2] != MidiFile.ALL_SOUNDS_OFF
