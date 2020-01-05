# mellowchord

This project is very experimental and I'm not 100% sure of what it will become.  Here's what works now:
* ChordMap class which generates chord sequences following these charts:  https://www.mugglinworks.com/chordmaps/chartmaps.htm
* Simple command line interface to generate chord sequences
* Output MIDI files so that generated chord sequences can be played
* Output MIDI messages directly to a MIDI port to play chord sequences

Here's where this might go in the future:
* Melody generator that generates melodies to chord sequences (and vice versa?)
* A series of command line tools to easily chain these operations together

# Installing

This module is not (yet) on pypi.  For now install it directly from github like this:

```pip install git+https://github.com/rossh-42/mellowchord.git```

If you want to play directly to a MIDI device you will need to install a backend for mido.  You can read about the details of that at https://mido.readthedocs.io/en/latest/backends/index.html.  I have tested with the mido-recommended RtMidi backend installed, which I can also recommend:

```pip install python-rtmidi```
