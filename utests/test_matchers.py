from fsa4streams.fsa import FSA, LOG

from .test_fsa import assert_matches

from pytest import mark

@mark.parametrize("string, matches", [
    ("a",    []),
    ("ab",   []),
    ("b",    []),
    ("ba",   []),
    ("bac",  ['bac']),
    ("def",  ['def']),
    ("bace", ['bac']),
    ("baec", []),
])
def test_multiple_choices_matcher(string, matches):
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
    assert_matches(fsa, string, matches)

@mark.parametrize("string, matches", [
    ("a",    []),
    ("ab",   []),
    ("b",    []),
    ("ba",   []),
    ("bac",  ['bac']),
    ("def",  ['def']),
    ("bace", ['bac']),
    ("baec", []),
])
def test_regexp_matcher(string, matches):
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
    assert_matches(fsa, string, matches)
