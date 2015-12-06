from fsa4streams.fsa import FSA, LOG

from nose.tools import assert_equal, assert_set_equal

from test_fsa import assert_matches

def test_multiple_choices_matcher():
    fsa = FSA.make_empty()
    (fsa
     .add_state("start")
       .add_transition(['b', 'c', 'd', 'f'], "s1", matcher="multiple-choices")
     .add_state("s1")
       .add_transition(['a', 'e', 'i', 'o', 'u'], "s2", matcher="multiple-choices")
     .add_state("s2")
       .add_transition(['b', 'c', 'd', 'f'], "finish", matcher="multiple-choices")
     .add_state("finish", terminal=True)
     .check_structure()
    )
    yield assert_matches, fsa, "a", []
    yield assert_matches, fsa, "ab", []
    yield assert_matches, fsa, "b", []
    yield assert_matches, fsa, "ba", []
    yield assert_matches, fsa, "bac", ['bac']
    yield assert_matches, fsa, "def", ['def']
    yield assert_matches, fsa, "bace", ['bac']
    yield assert_matches, fsa, "baec", []


def test_regexp_matcher():
    fsa = FSA.make_empty()
    (fsa
     .add_state("start")
       .add_transition("[b-df-hj-np-tv-xz]", "s1", matcher="regexp")
     .add_state("s1")
       .add_transition("[aeiouy]", "s2", matcher="regexp")
     .add_state("s2")
       .add_transition("[b-df-hj-np-tv-xz]", "finish", matcher="regexp")
     .add_state("finish", terminal=True)
     .check_structure()
    )
    yield assert_matches, fsa, "a", []
    yield assert_matches, fsa, "ab", []
    yield assert_matches, fsa, "b", []
    yield assert_matches, fsa, "ba", []
    yield assert_matches, fsa, "bac", ['bac']
    yield assert_matches, fsa, "def", ['def']
    yield assert_matches, fsa, "bace", ['bac']
    yield assert_matches, fsa, "baec", []


