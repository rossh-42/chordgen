import itertools
from json import JSONEncoder
import musthe
import networkx as nx


roman_numerals = (None, 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII')


class Chord(object):
    def __init__(self, degree, chord_type, bass=None):
        self.degree = int(degree)
        assert chord_type in musthe.Chord.valid_types
        self.chord_type = chord_type
        self.bass = None
        if bass is not None:
            self.bass = int(bass)

    def chord_name_modifiers(self):
        modifiers = self._third
        if self._add is not None:
            modifiers += '{}'.format(self._add)
        if self._bass is not None:
            modifiers += '/{}'.format(self._bass)
        return modifiers

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
        if self.bass:
            chord_name += '/{}'.format(self.bass)
        return chord_name

    def __repr__(self):
        return self.name()

    def __hash__(self):
        normalized_chord_type = self.chord_type
        for alias in musthe.Chord.aliases:
            if self.chord_type == alias:
                normalized_chord_type = musthe.Chord.aliases[alias]
                break
        return hash((self.degree, normalized_chord_type, self.bass))

    def __eq__(self, other):
        if self.degree == other.degree:
            if chords_types_are_equal(self.chord_type, other.chord_type):
                if self.bass == other.bass:
                    return True
        return False


class KeyedChord(musthe.Chord):
    def __init__(self, key, chord_to_wrap):
        self.degree = chord_to_wrap.degree
        self.chord_type = chord_to_wrap.chord_type
        self.bass = chord_to_wrap.bass
        self.key = key
        scale = musthe.Scale(key, 'major')
        self.root_note = scale[self.degree-1]
        musthe.Chord.__init__(self, self.root_note, chord_to_wrap.chord_type)

    def name(self):
        return musthe.Chord.__str__()


class KeyedChordEncoder(JSONEncoder):
    def default(self, o):
        ret_dict = {}
        ret_dict['degree'] = o.degree
        ret_dict['chord_type'] = o.chord_type
        ret_dict['bass'] = o.bass
        ret_dict['key'] = o.key
        return ret_dict


def keyed_chord_decoder(json_object):
    return KeyedChord(json_object['key'], Chord(json_object['degree'],
                                                json_object['chord_type'],
                                                json_object['bass']))


def chords_types_are_equal(chord_type_1, chord_type_2):
    for alias in musthe.Chord.aliases:
        chord_type_set = set([alias, musthe.Chord.aliases[alias]])
        if chord_type_1 in chord_type_set and chord_type_2 in chord_type_set:
            return True
    return False


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


IM = Chord(1, 'M')
IM_3 = Chord(1, 'M', bass=3)
IM_5 = Chord(1, 'M', bass=5)
IM7 = Chord(1, 'M7')
iim = Chord(2, 'm')
iiim = Chord(3, 'm')
IVM = Chord(4, 'M')
IVM_1 = Chord(4, 'M', bass=1)
VM = Chord(5, 'M')
VM_1 = Chord(5, 'M', bass=1)
vim = Chord(6, 'm')


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
        VM_1_gn = _ChordGraphNode([VM_1])
        vim_gn = _ChordGraphNode([vim])

        self._g.add_nodes_from([IM_gn, IM_3_gn, IM_5_gn, iim_gn, iiim_gn,
                                IVM_gn, IVM_1_gn, VM_gn, VM_1_gn, vim_gn])

        self._g.add_edge(IM_gn, IVM_1_gn)
        self._g.add_edge(IM_gn, VM_1_gn)

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

        self._g.add_edge(VM_1_gn, IM_gn)

        self._g.add_edge(vim_gn, IVM_gn)
        self._g.add_edge(vim_gn, iim_gn)
        self.key = key
        if self.key:
            self.scale = musthe.Scale(self.key, 'major')

    def _find_node_by_chord(self, chord):
        for node in self._g.nodes:
            if chord in node.chords:
                return node
        assert False
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
            c = musthe.Chord(current_chord)
            scale = musthe.Scale(self.key, 'major')
            degree = None
            for d in range(7):
                if scale[d] == c.notes[0]:
                    degree = d + 1
                    break
            assert degree
            current_chord = Chord(degree, c.chord_type)
        elif isinstance(current_chord, Chord):
            pass
        elif isinstance(current_chord, KeyedChord):
            assert self.key
            assert current_chord.key == self.key
            current_chord = Chord(current_chord.degree, current_chord.chord_type, current_chord.bass)
        node = self._find_node_by_chord(current_chord)
        for successor in self._g.successors(node):
            if all_variants:
                for chord in successor.chords:
                    if self.key:
                        retval.append(KeyedChord(self.key, chord))
                    else:
                        retval.append(chord)
            else:
                if self.key:
                    retval.append(KeyedChord(self.key, successor.primary))
                else:
                    retval.append(successor.primary)
        return retval

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
                yield current_sequence
        else:
            next_keyed_chords = self.next_chords(chord_string, all_variants=True)
            for next_keyed_chord in next_keyed_chords:
                next_chord_name = str(next_keyed_chord)
                yield from self.gen_sequence(next_chord_name, num_chords, current_sequence)
        current_sequence.pop()
