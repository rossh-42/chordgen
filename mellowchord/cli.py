from configargparse import ArgumentParser
from mellowchord import apply_inversion
from mellowchord import ChordMap
from mellowchord import make_file_name_from_chord_sequence
from mellowchord import make_file_name_from_melody
from mellowchord import MellowchordError
from mellowchord import MelodyGenerator
from mellowchord import raise_or_lower_an_octave
from mellowchord import validate_key
from mellowchord import validate_start
from mellowchord import write_chord_sequence_json
from mellowchord import read_chord_sequence_json
from mellowchord import write_midi_file
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
                        type=str, help='Directory to write MIDI or JSON files', default=os.getcwd())
    parser.add_argument('-p', '--program',
                        type=int, help='MIDI program value', default=0)
    parser.add_argument('-a', '--autoplay',
                        action='store_true', help='New MIDI automatically plays')
    subparsers = parser.add_subparsers(dest='command')

    chordgen_parser = subparsers.add_parser('chordgen', aliases=['c'], help='Generate a series of chord sequences')
    chordgen_parser.add_argument('key', type=str, help='Major or natural minor key to generate chords from')
    chordgen_parser.add_argument('start', type=str, help='Name of the chord to start from')
    chordgen_parser.add_argument('num', type=int, help='Number of chords in each sequence')

    melodygen_parser = subparsers.add_parser('melodygen',
                                             aliases=['m'],
                                             help='Generate a melody to match a chord sequence')
    melodygen_parser.add_argument('chord_sequence', type=str, help='Chord sequence JSON file that was '
                                                                   'saved by chordgen')
    melodygen_parser.add_argument('-n', '--notes_per_chord',
                                  type=int, help='Number of notes to generate for each chord', default=1)

    args = parser.parse_args()
    try:
        if args.command in ('chordgen', 'c'):
            chordgen(args.key, args.start, args.num, args.workingdir, args.program, args.autoplay)
        elif args.command in ('melodygen', 'm'):
            melodygen(args.chord_sequence, args.notes_per_chord, args.workingdir, args.program, args.autoplay)
    except MellowchordError as e:
        print(e)


def get_command(prompt, valid_cmds=None):
    while True:
        sys.stdout.write(prompt)
        sys.stdout.flush()
        cmd = readchar.readkey()
        cmd = cmd.lower()
        print(cmd)
        if cmd == 'q':
            sys.exit(0)
        if cmd in [str(c) for c in valid_cmds]:
            return cmd
        else:
            printed_commands = valid_cmds + ['q']
            print(f'Valid responses are {printed_commands}')
            continue


def print_chord_sequence(key, seq):
    print(f'key = {key}')
    for keyed_chord in seq:
        sys.stdout.write(str(keyed_chord))
        sys.stdout.write(': ')
        sys.stdout.write(keyed_chord.scientific_notation())
        sys.stdout.write('\n')


def print_melody(notes):
    num_notes = len(notes)
    sys.stdout.write('melody = ')
    for index, note in enumerate(notes):
        sys.stdout.write(str(note))
        if index < num_notes - 1:
            sys.stdout.write(' - ')
    sys.stdout.write('\n')


def chordgen(key, start, num, workingdir, program, autoplay):
    validate_key(key)
    cm = ChordMap(key, octave_adjustment=-1)
    validate_start(start, cm)
    for seq in cm.gen_sequence(start, num):
        seq_name = make_file_name_from_chord_sequence(seq)
        print(seq_name)
        midi_filename = seq_name + '.mid'
        midi_file_path = os.path.join(workingdir, midi_filename)
        midi_file = write_midi_file(seq, None, midi_file_path, program)
        json_filename = seq_name + '.json'
        json_file_path = os.path.join(workingdir, json_filename)
        if autoplay:
            midi_file.play(raise_exceptions=True)
        while True:
            cmd = get_command('>', valid_cmds=['n', 'p', 'i', 'v', 'o', 'm', 'h', 'j'])
            if cmd == 'n':
                break
            elif cmd == 'p':
                print(f'Playing {seq_name}')
                midi_file.play(raise_exceptions=True)
            elif cmd == 'i':
                print_chord_sequence(key, seq)
            elif cmd == 'v':
                chord_index = int(get_command('chord_in_sequence?>', valid_cmds=[x+1 for x in range(len(seq))])) - 1
                inversion = int(get_command('inversion?>', valid_cmds=[0, 1, 2]))
                if inversion == 0:
                    continue
                original_chord_string = str(seq[chord_index])
                seq[chord_index] = apply_inversion(seq[chord_index], inversion)
                midi_file = write_midi_file(seq, None, midi_file_path, program)
                seq_name = make_file_name_from_chord_sequence(seq)
                midi_filename = seq_name + '.mid'
                midi_file_path = os.path.join(workingdir, midi_filename)
                print(f'converted {original_chord_string} to {seq[chord_index]}')
            elif cmd == 'o':
                chord_index = int(get_command('chord_in_sequence?>', valid_cmds=[x+1 for x in range(len(seq))])) - 1
                up_or_down = get_command('+_or_-?>', valid_cmds=['+', '-'])
                seq[chord_index] = raise_or_lower_an_octave(seq[chord_index], 1 if up_or_down == '+' else 0)
                midi_file = write_midi_file(seq, None, midi_file_path, program)
                if up_or_down == '+':
                    verb = 'raised'
                else:
                    verb = 'lowered'
                print(f'{verb} {seq[chord_index]} by one octave')
            elif cmd == 'm':
                midi_file.write()
                print(f'Saved {midi_filename} to disk')
            elif cmd == 'j':
                write_chord_sequence_json(json_file_path, key, seq)
                print(f'Saved {json_filename} to disk')
            elif cmd == 'h':
                print('(n)ext (p)lay (i)nfo in(v)ert (o)ctave (j)son (m)idi (q)uit')


def melodygen(chord_sequence_file, notes_per_chord, workingdir, program, autoplay):
    key, seq = read_chord_sequence_json(chord_sequence_file)
    print_chord_sequence(key, seq)
    melody_gen = MelodyGenerator(key, seq, notes_per_chord)
    for notes in melody_gen.gen_sequence():
        print_melody(notes)
        melody_name = make_file_name_from_melody(notes)
        midi_filename = melody_name + '.mid'
        midi_file_path = os.path.join(workingdir, midi_filename)
        midi_file = write_midi_file(seq, notes, midi_file_path, program)
        if autoplay:
            midi_file.play(raise_exceptions=True)
        while True:
            cmd = get_command('>', valid_cmds=['n', 'p', 'i', 'm', 'h'])
            if cmd == 'n':
                break
            elif cmd == 'p':
                print(f'Playing {melody_name}')
                midi_file.play(raise_exceptions=True)
            elif cmd == 'i':
                print_chord_sequence(key, seq)
                print_melody(notes)
            elif cmd == 'm':
                midi_file.write()
                print(f'Saved {midi_filename} to disk')
            elif cmd == 'h':
                print('(n)ext (p)lay (i)nfo (m)idi (q)uit')


if __name__ == "__main__":
    main()
