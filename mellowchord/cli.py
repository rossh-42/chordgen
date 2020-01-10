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
CONFIG_FILE_HELP = ' (you can also set this in {})'.format(config_file_path)


def main():
    home = str(Path.home())
    config_file_path = os.path.join(home, '.mellowchord')
    parser = ArgumentParser(default_config_files=[config_file_path],
                            description='Tool for generating chord sequences and melodies as MIDI files')
    parser.add_argument('-w', '--workingdir',
                        type=str, help='Directory to write MIDI files' + CONFIG_FILE_HELP, default=os.getcwd())
    parser.add_argument('-p', '--program',
                        type=int, help='MIDI program value' + CONFIG_FILE_HELP, default=0)
    parser.add_argument('-a', '--autoplay',
                        action='store_true', help='New MIDI automatically plays' + CONFIG_FILE_HELP)
    subparsers = parser.add_subparsers(dest='command')

    chordgen_parser = subparsers.add_parser('chordgen', aliases=['c'], help='Generate a series of chord sequences')
    chordgen_parser.add_argument('key', type=str, help='key (all keys are major)')
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


def get_command(prompt):
    sys.stdout.write(prompt)
    sys.stdout.flush()
    cmd = readchar.readkey()
    print(cmd)
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
            cmd = get_command('>')
            if cmd.lower() == 'n':
                break
            elif cmd.lower() == 'p':
                print('Playing {}'.format(seq_name))
                midi_file.play(raise_exceptions=True)
            elif cmd.lower() == 'i':
                for keyed_chord in seq:
                    sys.stdout.write(str(keyed_chord))
                    sys.stdout.write(': ')
                    sys.stdout.write(keyed_chord.scientific_notation())
                    sys.stdout.write('\n')
            elif cmd.lower() == 't':
                chord_index = int(get_command('chord_in_sequence?>'))
                assert chord_index in list(range(len(seq)))
                inversion = int(get_command('transposition?>'))
                assert inversion in (0, 1, 2)
                original_chord_string = str(seq[chord_index])
                seq[chord_index] = apply_inversion(seq[chord_index], inversion)
                midi_file = write_midi_file(seq, midi_file_path, program)
                print('converted {} to {}'.format(original_chord_string, seq[chord_index]))
            elif cmd.lower() == 'o':
                chord_index = int(get_command('chord_in_sequence?>'))
                assert chord_index in list(range(len(seq)))
                up_or_down = get_command('+_or_-?>')
                assert up_or_down in ('+', '-')
                seq[chord_index] = raise_or_lower_an_octave(seq[chord_index], up_or_down == '+')
                midi_file = write_midi_file(seq, midi_file_path, program)
                if up_or_down == '+':
                    verb = 'raised'
                else:
                    verb = 'lowered'
                print('{} {} by one octave'.format(verb, seq[chord_index]))
            elif cmd.lower() == 's':
                midi_file.write()
                print('Saved {} to disk'.format(filename))
            elif cmd.lower() == 'q':
                sys.exit(0)
            elif cmd.lower() == 'h':
                print('(n)ext (p)lay (i)nfo (t)ranspose (o)ctave (s)ave (q)uit')


if __name__ == "__main__":
    main()
