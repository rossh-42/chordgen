import argparse
from mellowchord import ChordMap
from mellowchord import make_file_name_from_chord_sequence
from mellowchord import MellowchordError
from mellowchord import MidiFile
from mellowchord import validate_key
from mellowchord import validate_start


def main():
    parser = argparse.ArgumentParser(description='Tool for generating chord sequences and melodies as MIDI files')
    subparsers = parser.add_subparsers(dest='command')

    chordgen_parser = subparsers.add_parser('chordgen', aliases=['c'], help='Generate a series of chord sequences')
    chordgen_parser.add_argument('key', type=str, help='key (all keys are major)')
    chordgen_parser.add_argument('start', type=str, help='name of the chord to start from')
    chordgen_parser.add_argument('num', type=int, help='number of chords in each sequence')
    chordgen_parser.add_argument('output', type=str, choices=['f', 'm', 'b'],
                                 help='output type (f=file, m=midi, b=both)')

    melodygen_parser = subparsers.add_parser('melodygen',
                                             aliases=['m'],
                                             help='Generate a melody to match a chord sequence')

    args = parser.parse_args()
    try:
        if args.command in ('chordgen', 'c'):
            chordgen(args.key, args.start, args.num, args.output)
        elif args.command in ('melodygen', 'm'):
            raise MellowchordError('not implemented!')
    except MellowchordError as e:
        print(e)


def chordgen(key, start, num, output):
    validate_key(key)
    cm = ChordMap(key)
    validate_start(start, cm)
    for seq in cm.gen_sequence(start, num):
        print(make_file_name_from_chord_sequence(seq))
        filename = make_file_name_from_chord_sequence(seq) + '.mid'
        midi_file = MidiFile(filename)
        for keyed_chord in seq:
            midi_file.add_chord(keyed_chord)
        if output in ('f', 'b'):
            midi_file.write()
        if output in ('m', 'b'):
            midi_file.play(raise_exceptions=True)