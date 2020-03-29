from configargparse import ArgumentParser
from mellowchord import apply_inversion
from mellowchord import ChordMap
from mellowchord import make_file_name_from_chord_sequence
from mellowchord import MellowchordError
from mellowchord import MidiFile
from mellowchord import raise_or_lower_an_octave
from mellowchord import validate_key
from mellowchord import validate_start
import os
from pathlib import Path
import readchar
import sys


home = str(Path.home())
config_file_path = os.path.join(home, '.mellowchord')


def main():
    home = str(Path.home())
    config_file_path = os.path.join(home, '.mellowchord')
    parser = ArgumentParser(default_config_files=[config_file_path],
                            description='Tool for generating chord sequences and melodies as MIDI files.')
    parser.add_argument('-w', '--workingdir',
                        type=str, help='Directory to write MIDI files', default=os.getcwd())
    parser.add_argument('-p', '--program',
                        type=int, help='MIDI program value', default=0)
    parser.add_argument('-a', '--autoplay',
                        action='store_true', help='New MIDI automatically plays')
    subparsers = parser.add_subparsers(dest='command')

    chordgen_parser = subparsers.add_parser('chordgen', aliases=['c'], help='Generate a series of chord sequences')
    chordgen_parser.add_argument('key', type=str, help='major or natural minor key to generate chords from')
    chordgen_parser.add_argument('start', type=str, help='name of the chord to start from')
    chordgen_parser.add_argument('num', type=int, help='number of chords in each sequence')

    subparsers.add_parser('melodygen',
                          aliases=['m'],
                          help='Generate a melody to match a chord sequence')

    args = parser.parse_args()
    try:
        if args.command in ('chordgen', 'c'):
            chordgen(args.key, args.start, args.num, args.workingdir, args.program, args.autoplay)
        elif args.command in ('melodygen', 'm'):
            raise MellowchordError('not implemented!')
    except MellowchordError as e:
        print(e)


def get_command(prompt, valid_cmds=None):
    while True:
        sys.stdout.write(prompt)
        sys.stdout.flush()
        cmd = readchar.readkey()
        print(cmd)
        if cmd == 'q':
            sys.exit(0)
        if valid_cmds:
            if cmd in [str(c) for c in valid_cmds]:
                return cmd
            else:
                printed_commands = valid_cmds + ['q']
                print(f'Valid responses are {printed_commands}')
                continue
        return cmd


def write_midi_file(seq, midi_file_path, program):
    midi_file = MidiFile(midi_file_path, program)
    for keyed_chord in seq:
        midi_file.add_chord(keyed_chord)
    return midi_file


def chordgen(key, start, num, workingdir, program, autoplay):
    validate_key(key)
    cm = ChordMap(key)
    validate_start(start, cm)
    for seq in cm.gen_sequence(start, num):
        seq_name = make_file_name_from_chord_sequence(seq)
        print(seq_name)
        filename = make_file_name_from_chord_sequence(seq) + '.mid'
        midi_file_path = os.path.join(workingdir, filename)
        midi_file = write_midi_file(seq, midi_file_path, program)
        if autoplay:
            midi_file.play(raise_exceptions=True)
        while True:
            cmd = get_command('>', valid_cmds=['n', 'p', 'i', 't', 'o', 's', 'h'])
            if cmd == 'n':
                break
            elif cmd == 'p':
                print(f'Playing {seq_name}')
                midi_file.play(raise_exceptions=True)
            elif cmd == 'i':
                for keyed_chord in seq:
                    sys.stdout.write(str(keyed_chord))
                    sys.stdout.write(': ')
                    sys.stdout.write(keyed_chord.scientific_notation())
                    sys.stdout.write('\n')
            elif cmd == 't':
                chord_index = int(get_command('chord_in_sequence?>', valid_cmds=list(range(len(seq)))))
                inversion = int(get_command('transposition?>', valid_cmds=[0, 1, 2]))
                original_chord_string = str(seq[chord_index])
                seq[chord_index] = apply_inversion(seq[chord_index], inversion)
                midi_file = write_midi_file(seq, midi_file_path, program)
                print(f'converted {original_chord_string} to {seq[chord_index]}')
            elif cmd == 'o':
                chord_index = int(get_command('chord_in_sequence?>', valid_cmds=list(range(len(seq)))))
                up_or_down = get_command('+_or_-?>', valid_cmds=['+', '-'])
                seq[chord_index] = raise_or_lower_an_octave(seq[chord_index], up_or_down == '+')
                midi_file = write_midi_file(seq, midi_file_path, program)
                if up_or_down == '+':
                    verb = 'raised'
                else:
                    verb = 'lowered'
                print(f'{verb} {seq[chord_index]} by one octave')
            elif cmd == 's':
                midi_file.write()
                print(f'Saved {filename} to disk')
            elif cmd == 'h':
                print('(n)ext (p)lay (i)nfo (t)ranspose (o)ctave (s)ave (q)uit')


if __name__ == "__main__":
    main()
