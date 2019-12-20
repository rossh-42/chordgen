import argparse
from mellowchord import chordgen
from mellowchord import MellowchordError


def main():
    parser = argparse.ArgumentParser(description='Tool for generating chord sequences and melodies as MIDI files')
    subparsers = parser.add_subparsers(dest='command')

    chordgen_parser = subparsers.add_parser('chordgen', aliases=['c'], help='Generate a series of chord sequences')
    chordgen_parser.add_argument('key', type=str, help='key (all keys are major)')
    chordgen_parser.add_argument('start', type=str, help='name of the chord to start from')
    chordgen_parser.add_argument('num', type=int, help='number of chords in each sequence')

    melodygen_parser = subparsers.add_parser('melodygen',
                                             aliases=['m'],
                                             help='Generate a melody to match a chord sequence')

    args = parser.parse_args()
    try:
        if args.command in ('chordgen', 'c'):
            chordgen(args.key, args.start, args.num)
        elif args.command in ('melodygen', 'm'):
            print('not implemented!')
    except MellowchordError as e:
        print(e)
