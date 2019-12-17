import argparse
from chordgen import ChordMap


def main():
    parser = argparse.ArgumentParser(description='Generate a series of chord sequences')
    parser.add_argument('key', type=str, help='key')
    parser.add_argument('start', type=str, help='name of the chord to start from')
    parser.add_argument('num', type=int, help='number of chords in each sequence')

    args = parser.parse_args()
    cm = ChordMap(args.key)
    for seq in cm.gen_sequence(args.start, args.num):
        print(seq)
