import copy
import mido
import musthe
import networkx as nx
import re


roman_numerals = (None, 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII')


class MellowchordError(Exception):
    pass


class ChordParseError(MellowchordError):
    pass


class InvalidArgumentError(MellowchordError):
    pass


class Chord(object):
    def __init__(self, degree, chord_type, inversion=None):
        self.degree = int(degree)
        assert chord_type in musthe.Chord.valid_types
        self.chord_type = chord_type
        assert inversion in (None, 1, 2)
        self.inversion = inversion

    def name(self):
        roman = roman_numerals[self.degree]
        try:
            recipe = musthe.Chord.recipes[self.chord_type]
        except KeyError:
            key = musthe.Chord.aliases[self.chord_type]
            recipe = musthe.Chord.recipes[key]
        if 'm3' in recipe:
            chord_name = roman.lower()
        else:
            chord_name = roman.upper()
        chord_name += self.chord_type
        if self.inversion == 1:
            chord_name += '/{}'.format((self.degree + 2) % 7)
        elif self.inversion == 2:
            chord_name += '/{}'.format((self.degree + 4) % 7)
        return chord_name

    def __repr__(self):
        return self.name()

    def __str__(self):
        return self.name()

    def __hash__(self):
        normalized_chord_type = self.chord_type
        for alias in musthe.Chord.aliases:
            if self.chord_type == alias:
                normalized_chord_type = musthe.Chord.aliases[alias]
                break
        return hash((self.degree, normalized_chord_type, self.inversion))

    def __eq__(self, other):
        if self.degree == other.degree:
            if chords_types_are_equal(self.chord_type, other.chord_type):
                if self.inversion == other.inversion:
                    return True
        return False


def apply_inversion(keyed_chord, inversion):
    if inversion == 0:
        inversion = None
    inverted_chord = Chord(keyed_chord.degree, keyed_chord.chord_type, inversion)
    return KeyedChord(keyed_chord.key, inverted_chord)


def raise_or_lower_an_octave(keyed_chord, up):
    retval_keyed_chord = copy.deepcopy(keyed_chord)
    for index, note in enumerate(retval_keyed_chord.notes):
        original_octave = note.octave
        if up:
            new_octave = original_octave + 1
        else:
            new_octave = original_octave - 1
        retval_keyed_chord.notes[index] = note.to_octave(new_octave)
    return retval_keyed_chord


class KeyedChord(musthe.Chord):
    def __init__(self, key, chord_to_wrap):
        self.degree = chord_to_wrap.degree
        self.chord_type = chord_to_wrap.chord_type
        self.inversion = chord_to_wrap.inversion
        self.key = key
        self.scale = musthe.Scale(key, 'major')
        self.root_note = self.scale[self.degree-1]
        musthe.Chord.__init__(self, self.root_note, chord_to_wrap.chord_type)

    def name(self):
        name = '{}{}'.format(str(self.root_note), self.chord_type)
        if self.inversion == 1:
            name += '/{}'.format(str(self.scale[self.degree + 1]))
        elif self.inversion == 2:
            name += '/{}'.format(str(self.scale[self.degree + 3]))
        return name

    def __str__(self):
        return self.name()

    def __repr__(self):
        return self.name()

    @property
    def inverted_notes(self):
        retval = {}
        for index, note in enumerate(self.notes):
            if self.inversion == 1 and index == 0:
                inverted_note = note.to_octave(note.octave + 1)
                retval['root'] = inverted_note
            elif self.inversion == 2 and index == 2:
                inverted_note = note.to_octave(note.octave - 1)
                retval['fifth'] = inverted_note
            else:
                track_names = ('root', 'third', 'fifth', 'seventh')
                retval[track_names[index]] = note
        return retval

    def scientific_notation(self):
        retval = ''
        if len(self.notes) == 3:
            track_order = ('root', 'third', 'fifth')
        elif len(self.notes) == 4:
            track_order = ('root', 'third', 'fifth', 'seventh')

        if self.inversion == 1:
            track_order = ('third', 'fifth', 'root')
        elif self.inversion == 2:
            track_order = ('fifth', 'root', 'third')
        for track_name in track_order:
            retval += '{}'.format(self.inverted_notes[track_name].scientific_notation())
            retval += ' '
        return retval.strip()


class MidiFile(object):
    BUFFER_TIME = 500
    ALL_SOUNDS_OFF = mido.Message('control_change', control=120, value=0, time=BUFFER_TIME)

    def __init__(self, filename, program=0):
        self._filename = filename
        self._tracks = {}
        for track_name in ('root', 'third', 'fifth', 'seventh'):
            track = mido.MidiTrack()
            track.name = track_name
            self._tracks[track_name] = track
            track.append(mido.Message('program_change', program=program, time=0))
            track.append(MidiFile.ALL_SOUNDS_OFF)

    def _add_track_note(self, track_name, note, velocity, on_time, off_time):
        self._tracks[track_name].append(mido.Message('note_on',
                                                     note=note,
                                                     velocity=velocity,
                                                     time=off_time))
        self._tracks[track_name].append(mido.Message('note_off',
                                                     note=note,
                                                     velocity=velocity,
                                                     time=on_time))

    def add_chord(self, keyed_chord, velocity=64, time=1000):
        # bass_note = keyed_chord.root_note.to_octave(2)
        # self._add_track_note('bass', bass_note.midi_note(), velocity, time, 5)

        notes_dict = keyed_chord.inverted_notes
        for track_name in ['root', 'third', 'fifth']:
            self._add_track_note(track_name, notes_dict[track_name].midi_note(), velocity, time, 5)

        if len(keyed_chord.notes) >= 4:
            self._add_track_note('seventh', keyed_chord.notes[3].midi_note(), velocity, time, 5)
        else:
            self._tracks['seventh'].append(mido.Message('note_off',
                                                        note=0,
                                                        velocity=velocity,
                                                        time=time+5))

    def _make_midi_file(self):
        midi_file = mido.MidiFile()
        tracks_copy = copy.copy(self._tracks)
        for track_name in ('root', 'third', 'fifth', 'seventh'):
            self._tracks[track_name].append(MidiFile.ALL_SOUNDS_OFF)
            midi_file.tracks.append(tracks_copy[track_name])
        return midi_file

    def write(self):
        midi_file = self._make_midi_file()
        midi_file.save(self._filename)

    def play(self, portname=None, raise_exceptions=False):
        midi_file = self._make_midi_file()
        try:
            with mido.open_output(portname=portname, autoreset=True) as port:
                for msg in midi_file.play():
                    port.send(msg)
        except IOError as e:
            if raise_exceptions:
                raise MellowchordError(str(e))


# class KeyedChordEncoder(JSONEncoder):
#     def default(self, o):
#         ret_dict = {}
#         ret_dict['degree'] = o.degree
#         ret_dict['chord_type'] = o.chord_type
#         ret_dict['bass'] = o.bass
#         ret_dict['key'] = o.key
#         return ret_dict


# def keyed_chord_decoder(json_object):
#     return KeyedChord(json_object['key'], Chord(json_object['degree'],
#                                                 json_object['chord_type'],
#                                                 json_object['bass']))


def chords_types_are_equal(chord_type_1, chord_type_2):
    for alias in musthe.Chord.aliases:
        chord_type_set = set([alias, musthe.Chord.aliases[alias]])
        if chord_type_1 in chord_type_set and chord_type_2 in chord_type_set:
            return True
    return False


def _split_bass(chord_string, key=None):
    m = re.search(r'(.*)/(.+)$', chord_string)
    if m:
        degree_int = None
        try:
            degree_int = int(m.group(2))
            if degree_int not in range(1, 8):
                raise ChordParseError('Can\'t parse chord string "{}"'.format(chord_string))
        except ValueError:
            try:
                n = musthe.Note(m.group(2))
            except ValueError:
                raise ChordParseError('Can\'t parse chord string "{}"'.format(chord_string))
            if key is None:
                raise ChordParseError('Can\'t parse chord string "{}" without a key'.format(chord_string))
            scale = musthe.Scale(key, 'major')
            for degree in range(1, 9):
                compare_n = scale[degree-1]
                if n.letter == compare_n.letter:
                    degree_int = degree
                    break
        assert degree_int
        return (m.group(1), degree_int)
    return (chord_string, None)


def string_to_chord(chord_string, key=None):
    (chord_string_minus_bass, bass) = _split_bass(chord_string, key)

    def bass_to_inversion(bass, degree):
        if bass is None:
            return None
        elif bass == (degree + 2) % 7:
            return 1
        elif bass == (degree + 4) % 7:
            return 2
        assert False, 'Unsupported slash chord {}'.format(chord_string)

    try:
        c = musthe.Chord(chord_string_minus_bass)
        degree = None
        scale = musthe.Scale(key, 'major')
        for d in range(7):
            if scale[d].letter == c.notes[0].letter:
                degree = d + 1
                break
        assert degree
        return Chord(degree, c.chord_type, bass_to_inversion(bass, degree))
    except ValueError:
        pass
    m = re.search(r'(VII|VI|V|III|II|IV|I|vii|vi|v|iii|ii|iv|i)([^\/]*)($|\/\d)', chord_string)
    if m is None:
        raise ChordParseError('Can\'t parse chord string "{}"'.format(chord_string))
    degree_string = m.group(1)
    chord_type_string = m.group(2)
    for degree, numeral in enumerate(roman_numerals):
        if numeral == degree_string.upper():
            return Chord(degree, chord_type_string, bass_to_inversion(bass, degree))
    raise ChordParseError('Can\'t parse chord string "{}"'.format(chord_string))


def string_to_keyed_chord(chord_string, key):
    c = string_to_chord(chord_string, key)
    return KeyedChord(key, c)


def make_file_name_from_chord_sequence(seq):
    name = ''
    for chord in seq:
        chord_string = str(chord)
        chord_string = chord_string.replace('/', '-')
        if len(name) != 0:
            name += '_'
        name += chord_string
    return name


def chord_in(chord_string, list_of_chords):
    """Return true if the chord represented by chord_string is in
    the given list of musthe.Chord objects.
    """
    for chord in list_of_chords:
        if chord_string == str(chord):
            return True
    return False


def validate_key(key):
    try:
        musthe.Note(key)
    except Exception:
        raise InvalidArgumentError('Invalid key "{}"'.format(key))
    return True


def validate_start(start, chord_map):
    assert chord_map.key is not None
    chord = string_to_chord(start, chord_map.key)
    node = chord_map._find_node_by_chord(chord)
    if node is None:
        raise InvalidArgumentError('Chord ({}) not found in map for this key ({})'.format(start, chord_map.key))


class _ChordGraphNode(object):
    def __init__(self, chords):
        self.chords = chords
        self.primary = self.chords[0]

    def __repr__(self):
        retval = '('
        num_chords = len(self.chords)
        for index, chord in enumerate(self.chords):
            retval += '{}'.format(chord.name())
            if index != num_chords-1:
                retval += ', '
        retval += ')'
        return retval


IM = Chord(1, 'maj')
IM_3 = Chord(1, 'maj', inversion=1)
IM_5 = Chord(1, 'maj', inversion=2)
IM7 = Chord(1, 'maj7')
iim = Chord(2, 'min')
iiim = Chord(3, 'min')
IVM = Chord(4, 'maj')
IVM_1 = Chord(4, 'maj', inversion=2)
VM = Chord(5, 'maj')
VM_2 = Chord(5, 'maj', inversion=2)
vim = Chord(6, 'min')

VIM = Chord(6, 'maj')
VIIM = Chord(7, 'maj')
IIM = Chord(2, 'maj')
IIIM = Chord(3, 'maj')


class ChordMap(nx.DiGraph):
    def __init__(self, key=None):
        self._g = nx.DiGraph()

        IM_gn = _ChordGraphNode([IM, IM7])
        IM_3_gn = _ChordGraphNode([IM_3])
        IM_5_gn = _ChordGraphNode([IM_5])
        iim_gn = _ChordGraphNode([iim])
        iiim_gn = _ChordGraphNode([iiim])
        IVM_gn = _ChordGraphNode([IVM])
        IVM_1_gn = _ChordGraphNode([IVM_1])
        VM_gn = _ChordGraphNode([VM])
        VM_2_gn = _ChordGraphNode([VM_2])
        vim_gn = _ChordGraphNode([vim])

        VIM_gn = _ChordGraphNode([VIM])
        VIIM_gn = _ChordGraphNode([VIIM])
        IIM_gn = _ChordGraphNode([IIM])
        IIIM_gn = _ChordGraphNode([IIIM])

        self._g.add_nodes_from([IM_gn, IM_3_gn, IM_5_gn, iim_gn, iiim_gn,
                                IVM_gn, IVM_1_gn, VM_gn, VM_2_gn, vim_gn])

        self._g.add_edge(IM_gn, IVM_1_gn)
        self._g.add_edge(IM_gn, VM_2_gn)

        self._g.add_edge(IM_3_gn, iim_gn)

        self._g.add_edge(iim_gn, IM_5_gn)
        self._g.add_edge(iim_gn, iiim_gn)
        self._g.add_edge(iim_gn, VM_gn)

        self._g.add_edge(iiim_gn, IM_gn)
        self._g.add_edge(iiim_gn, IVM_gn)
        self._g.add_edge(iiim_gn, vim_gn)

        self._g.add_edge(IVM_gn, IM_gn)
        self._g.add_edge(IVM_gn, IM_3_gn)
        self._g.add_edge(IVM_gn, IM_5_gn)
        self._g.add_edge(IVM_gn, iim_gn)
        self._g.add_edge(IVM_gn, VM_gn)

        self._g.add_edge(IVM_1_gn, IM_gn)

        self._g.add_edge(VM_gn, IM_gn)
        self._g.add_edge(VM_gn, iiim_gn)
        self._g.add_edge(VM_gn, vim_gn)

        self._g.add_edge(VM_2_gn, IM_gn)

        self._g.add_edge(vim_gn, IVM_gn)
        self._g.add_edge(vim_gn, iim_gn)

        self._g.add_edge(VIM_gn, iim_gn)
        self._g.add_edge(VIIM_gn, iiim_gn)
        self._g.add_edge(IM_gn, IVM_gn)
        self._g.add_edge(IIM_gn, VM_gn)
        self._g.add_edge(IIIM_gn, vim_gn)

        self.key = key
        if self.key:
            self.scale = musthe.Scale(self.key, 'major')

    def _find_node_by_chord(self, chord):
        for node in self._g.nodes:
            if chord in node.chords:
                return node
        return None

    def find_node_by_chord_string(self, chord_root_note, chord_type):
        for node in self._g:
            for chord in node.chords:
                kc = KeyedChord(self.key, chord)
                if kc.root_note.letter.name == chord_root_note:
                    if chords_types_are_equal(kc.chord_type, chord_type):
                        return node
        return None

    def next_chords(self, current_chord, all_variants=False):
        retval = []
        if isinstance(current_chord, str):
            assert self.key
            current_chord = string_to_chord(current_chord, self.key)
        elif isinstance(current_chord, Chord):
            pass
        elif isinstance(current_chord, KeyedChord):
            assert self.key
            assert current_chord.key == self.key
            current_chord = Chord(current_chord.degree, current_chord.chord_type, current_chord.inversion)
        node = self._find_node_by_chord(current_chord)
        assert node is not None
        for successor in self._g.successors(node):
            if all_variants:
                for chord in successor.chords:
                    self._append_chord(chord, self.key, retval)
            else:
                self._append_chord(successor.primary, self.key, retval)
        return retval

    def _append_chord(self, chord, key, chord_list):
        if key:
            chord_list.append(KeyedChord(key, chord))
        else:
            chord_list.append(chord)

    def next_nodes(self, current_node):
        retval = []
        for successor in self._g.successors(current_node):
            retval.append(successor)
        return retval

    def gen_sequence(self, chord_string, num_chords, current_sequence=[], already_yielded=set()):
        current_sequence.append(chord_string)
        assert len(current_sequence) <= num_chords
        if len(current_sequence) == num_chords:
            if tuple(current_sequence) not in already_yielded:
                already_yielded.add(tuple(current_sequence))
                yield [string_to_keyed_chord(c, self.key) for c in current_sequence]
        else:
            next_keyed_chords = self.next_chords(chord_string, all_variants=True)
            for next_keyed_chord in next_keyed_chords:
                next_chord_name = str(next_keyed_chord)
                yield from self.gen_sequence(next_chord_name, num_chords, current_sequence)
        current_sequence.pop()
