from mellowchord import chord_in
from mellowchord import ChordMap
from mellowchord import IM, IM_3, IM_5, IM7
from mellowchord import iim
from mellowchord import iiim
from mellowchord import IVM, IVM_1
from mellowchord import VM, VM_2
from mellowchord import vim
from mellowchord import IIM, IIIM, VIM, VIIM


def test_map():
    cm = ChordMap()
    set([IVM_1, VM_2])
    assert set(cm.next_chords(IM)) == set([IVM_1, VM_2, IVM])
    assert set(cm.next_chords(IM_3)) == set([iim])
    assert set(cm.next_chords(IM_5)) == set([])
    assert set(cm.next_chords(iim)) == set([IM_5, iiim, VM])
    assert set(cm.next_chords(iiim)) == set([IM, IVM, vim])
    assert set(cm.next_chords(IVM)) == set([IM, IM_3, IM_5, iim, VM])
    assert set(cm.next_chords(IVM_1)) == set([IM])
    assert set(cm.next_chords(VM)) == set([IM, iiim, vim])
    assert set(cm.next_chords(VM_2)) == set([IM])
    assert set(cm.next_chords(vim)) == set([iim, IVM])
    assert set(cm.next_chords(IIM)) == set([VM])
    assert set(cm.next_chords(IIIM)) == set([vim])
    assert set(cm.next_chords(VIM)) == set([iim])
    assert set(cm.next_chords(VIIM)) == set([iiim])


def test_map_C():
    cm = ChordMap('C')
    next_chords = cm.next_chords(IM)
    assert chord_in('Fmaj/C', next_chords)
    assert chord_in('Gmaj/D', next_chords)
    next_chords = cm.next_chords(iim)
    assert chord_in('Gmaj', next_chords)
    assert chord_in('Emin', next_chords)
    assert chord_in('Cmaj/G', next_chords)


def test_map_A_minor():
    a_min = ChordMap('Amin')
    next_chords = a_min.next_chords('Amin')
    assert chord_in('Dmin/A', next_chords)
    assert chord_in('Emin/B', next_chords)
    next_chords = a_min.next_chords('Bmin')
    assert chord_in('Cmaj', next_chords)
    assert chord_in('Emin', next_chords)
    assert chord_in('Amin/E', next_chords)


def test_map_B_flat():
    cm = ChordMap('Bb')
    next_chords = cm.next_chords(IM)
    assert chord_in('Ebmaj/Bb', next_chords)
    assert chord_in('Fmaj/C', next_chords)


def test_next():
    cm = ChordMap()
    after_iiim = cm.next_chords(iiim)
    assert IM in after_iiim
    assert IVM in after_iiim
    assert vim in after_iiim
    assert IM7 not in after_iiim


def test_next_all_variants():
    cm = ChordMap()
    after_iiim = cm.next_chords(iiim, all_variants=True)
    assert IM in after_iiim
    assert IVM in after_iiim
    assert vim in after_iiim
    assert IM7 in after_iiim


def test_next_chords_string():
    cm = ChordMap('C')
    next_chords = cm.next_chords('Cmaj')
    assert chord_in('Fmaj/C', next_chords)
    assert chord_in('Gmaj/D', next_chords)


def test_simple_sequence():
    cm = ChordMap('C')
    next_chords = cm.next_chords('Cmaj')
    next_chords = cm.next_chords(next_chords[0])
    next_chords = cm.next_chords(next_chords[0])


def test_gen_sequence():
    cm = ChordMap('C')
    for seq in cm.gen_sequence('Cmaj', 3):
        assert len(seq) == 3
        assert str(seq[0]) == 'Cmaj'
        assert str(seq[1]) in ('Fmaj', 'Fmaj/C', 'Gmaj/D')
        assert str(seq[2]) in ('Gmaj', 'Dmin', 'Cmaj/G', 'Cmaj/E', 'Cmaj', 'Cmaj7')
