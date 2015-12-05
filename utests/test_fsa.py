from fsa4streams.fsa import FSA, LOG

from nose.tools import assert_equal, assert_set_equal
from os.path import dirname, join
from unittest import skip

def match_list(tokens):
    return

def assert_matches(fsa, events, expected_matches, ordered=True):
    tokens = fsa.feed_all(events)
    got = [ "".join(token['history_events']) for token in tokens ]
    if ordered:
        assert_equal(expected_matches, got)
    else:
        assert_set_equal(set(expected_matches), set(got))
    LOG.debug("---")

def assert_outcomes(fsa, events, expected_outcomes, ordered=True):
    tokens = fsa.feed_all(events)
    got = [ token['state'] for token in tokens ]
    if ordered:
        assert_equal(expected_outcomes, got)
    else:
        assert_set_equal(set(expected_outcomes), set(got))
    LOG.debug("---")


def test_super_simple():
    fsa = FSA.make_empty()
    (fsa
     .add_state("start")
       .add_transition("a", "finish")
     .add_state("finish", terminal=True)
     .check_structure()
    )
    yield assert_matches, fsa, "a", ["a"]
    yield assert_matches, fsa, "b", []
    yield assert_matches, fsa, "babab", ["a", "a"]


def test_a_star():
    fsa = FSA.make_empty()
    (fsa
     .add_state("start", terminal=True)
       .add_transition("a", "start")
     .check_structure()
    )
    yield assert_matches, fsa, "", []
    yield assert_matches, fsa, "a", ["a"]
    yield assert_matches, fsa, "aa", ["aa"]
    yield assert_matches, fsa, "aaa", ["aaa"]
    yield assert_matches, fsa, "b", []
    yield assert_matches, fsa, "ba", ["a"]
    yield assert_matches, fsa, "baa", ["aa"]
    yield assert_matches, fsa, "ab", ["a"]
    yield assert_matches, fsa, "aab", ["aa"]
    yield assert_matches, fsa, "aabaaa", ["aa", "aaa"]


def test_a_b_star():
    fsa = FSA.make_empty()
    (fsa
     .add_state("start")
       .add_transition("a", "finish")
     .add_state("finish", terminal=True)
       .add_transition("b", "finish")
     .check_structure()
    )
    yield assert_matches, fsa, "a", ["a"]
    yield assert_matches, fsa, "ab", ["ab"]
    yield assert_matches, fsa, "abb", ["abb"]
    yield assert_matches, fsa, "abbb", ["abbb"]
    yield assert_matches, fsa, "c", []
    yield assert_matches, fsa, "ac", ["a"]
    yield assert_matches, fsa, "abc", ["ab"]
    yield assert_matches, fsa, "abbc", ["abb"]
    yield assert_matches, fsa, "ca", ["a"]
    yield assert_matches, fsa, "cab", ["ab"]
    yield assert_matches, fsa, "cabb", ["abb"]
    yield assert_matches, fsa, "abbabbb", ["abb", "abbb"]


def test_noise():
    fsa = FSA.make_empty()
    (fsa
     .add_state("start")
       .add_transition("a", "s1")
     .add_state("s1", max_noise=2)
       .add_transition("a", "s2")
     .add_state("s2", max_noise=2)
       .add_transition("a", "finish")
     .add_state("finish", terminal=True)
     .check_structure()
    )
    yield assert_matches, fsa, "aaa", ["aaa"]
    yield assert_matches, fsa, "abaa", ["aaa"]
    yield assert_matches, fsa, "abbaa", ["aaa"]
    yield assert_matches, fsa, "abbbaa", []
    yield assert_matches, fsa, "aaba", ["aaa"]
    yield assert_matches, fsa, "aabba", ["aaa"]
    yield assert_matches, fsa, "aabbba", []
    yield assert_matches, fsa, "ababa", ["aaa"]
    yield assert_matches, fsa, "abbaba", ["aaa"]
    yield assert_matches, fsa, "ababba", ["aaa"]
    yield assert_matches, fsa, "abbabba", ["aaa"]

def test_noise_global():
    fsa = FSA.make_empty(max_noise=3)
    (fsa
     .add_state("start")
       .add_transition("a", "s1")
     .add_state("s1", max_noise=2)
       .add_transition("a", "s2")
     .add_state("s2", max_noise=2)
       .add_transition("a", "finish")
     .add_state("finish", terminal=True)
     .check_structure()
    )
    yield assert_matches, fsa, "aaa", ["aaa"]
    yield assert_matches, fsa, "abaa", ["aaa"]
    yield assert_matches, fsa, "abbaa", ["aaa"]
    yield assert_matches, fsa, "abbbaa", []
    yield assert_matches, fsa, "aaba", ["aaa"]
    yield assert_matches, fsa, "aabba", ["aaa"]
    yield assert_matches, fsa, "aabbba", []
    yield assert_matches, fsa, "ababa", ["aaa"]
    yield assert_matches, fsa, "abbaba", ["aaa"]
    yield assert_matches, fsa, "ababba", ["aaa"]
    yield assert_matches, fsa, "abbabba", []


def test_non_deterministic():
    fsa = FSA.make_empty()
    (fsa
     .add_state("start")
       .add_transition("a", "s1")
       .add_transition("a", "s2")
     .add_state("s1")
       .add_transition("b", "finish")
     .add_state("s2")
       .add_transition("c", "finish")
     .add_state("finish", terminal=True)
     .check_structure()
    )
    yield assert_matches, fsa, "ab",   ["ab"]
    yield assert_matches, fsa, "ac",   ["ac"]
    yield assert_matches, fsa, "abc",  ["ab"]
    yield assert_matches, fsa, "acb",  ["ac"]
    yield assert_matches, fsa, "adbc", []


def test_non_deterministic_noise():
    fsa = FSA.make_empty(max_noise=1)
    (fsa
     .add_state("start")
       .add_transition("a", "s1")
       .add_transition("a", "s2")
     .add_state("s1", max_noise=1)
       .add_transition("b", "finish")
     .add_state("s2", max_noise=1)
       .add_transition("c", "finish")
     .add_state("finish", terminal=True)
     .check_structure()
    )
    yield assert_matches, fsa, "ab",   ["ab"]
    yield assert_matches, fsa, "ac",   ["ac"]
    yield assert_matches, fsa, "abc",  ["ab"]
    yield assert_matches, fsa, "acb",  ["ac"]
    yield assert_matches, fsa, "adbc", ["ab"]


def test_non_deterministic_noise_overlap():
    fsa = FSA.make_empty(max_noise=1,
                         allow_overlap=True,
                         state_defaults={'max_noise': 1})
    (fsa
     .add_state("start")
       .add_transition("a", "s1")
       .add_transition("a", "s2")
     .add_state("s1")
       .add_transition("b", "finish")
     .add_state("s2")
       .add_transition("c", "finish")
     .add_state("finish", terminal=True)
     .check_structure()
    )
    yield assert_matches, fsa, "ab",   ["ab"]
    yield assert_matches, fsa, "ac",   ["ac"]
    yield assert_matches, fsa, "abc",  ["ab", "ac"]
    yield assert_matches, fsa, "acb",  ["ac", "ab"]
    yield assert_matches, fsa, "adbc", ["ab"]


def test_default_transition():
    fsa = FSA.make_empty()
    (fsa
     .add_state("start")
       .add_transition("a", "s1")
     .add_state("s1", default_transition={'target': 'error'})
       .add_transition("a", "s2")
     .add_state("s2", default_transition={'target': 'error'})
       .add_transition("a", "finish")
     .add_state("finish", terminal=True)
     .add_state("error", terminal=True)
     .check_structure()
    )
    yield assert_outcomes, fsa, "ab", ['error']
    yield assert_outcomes, fsa, "aab", ['error']
    yield assert_outcomes, fsa, "aaa", ['finish']
    yield assert_outcomes, fsa, "aaab", ['finish']
    yield assert_outcomes, fsa, "aaaab", ['finish', 'error']
    yield assert_matches, fsa, "ab", ["ab"]
    yield assert_matches, fsa, "aab", ["aab"]


def test_default_transition_overlap():
    fsa = FSA.make_empty(allow_overlap=True)
    (fsa
     .add_state("start")
       .add_transition("a", "s1")
     .add_state("s1", default_transition={'target': 'error'})
       .add_transition("a", "s2")
     .add_state("s2", default_transition={'target': 'error'})
       .add_transition("a", "finish")
     .add_state("finish", terminal=True)
     .add_state("error", terminal=True)
     .check_structure()
    )
    yield assert_outcomes, fsa, "ab", ['error']
    yield assert_outcomes, fsa, "aab", ['error', 'error']
    yield assert_outcomes, fsa, "aaa", ['finish']
    yield assert_outcomes, fsa, "aaab", ['finish', 'error', 'error']
    yield assert_outcomes, fsa, "aaaab", ['finish', 'finish', 'error', 'error']
    yield assert_matches, fsa, "ab", ["ab"]
    yield assert_matches, fsa, "aab", ["ab", "aab"], False


def test_silent_default_transition():
    fsa = FSA.make_empty()
    (fsa
     .add_state("start")
       .add_transition("a", "s1")
     .add_state("s1", default_transition={'target': 'error', 'silent': True})
       .add_transition("a", "s2")
     .add_state("s2", default_transition={'target': 'error', 'silent': True})
       .add_transition("a", "finish")
     .add_state("finish", terminal=True)
     .add_state("error", terminal=True)
     .check_structure()
    )
    yield assert_matches, fsa, "ab", ["a"]
    yield assert_matches, fsa, "aab", ["aa"]


def test_silent_default_transition_loop():
    fsa = FSA.make_empty()
    (fsa
     .add_state("start")
       .add_transition("a", "s1")
     .add_state("s1", default_transition={'target': 's1', 'silent':True})
       .add_transition("a", "finish")
     .add_state("finish", terminal=True)
     .check_structure()
    )
    yield assert_matches, fsa, "abba", ["aa"]
    tokens = fsa.feed_all("abba")
    if tokens:
        yield assert_equal, ['s1'], tokens[0]['history_states']
    else:
        yield assert_equal, 1, len(tokens) # fail because tokens is empty


def test_immediate_match():
    fsa = FSA.make_empty()
    (fsa
     .add_state("start")
       .add_transition("a", "s1")
     .add_state("s1")
       .add_transition("b", "finish")
     .add_state("finish", terminal=True)
     .check_structure()
    )
    tokens = fsa.feed_all("ab", finish=False)
    assert_equal(1, len(tokens))


def test_differ_match():
    fsa = FSA.make_empty()
    (fsa
     .add_state("start")
       .add_transition("a", "s1")
     .add_state("s1")
       .add_transition("b", "finish")
     .add_state("finish", terminal=True)
       .add_transition("c", "finish")
     .check_structure()
    )
    tokens = fsa.feed_all("ab", finish=False)
    assert_equal(0, len(tokens))
    tokens = fsa.feed("c")
    assert_equal(0, len(tokens))
    tokens = fsa.feed("c")
    assert_equal(0, len(tokens))
    tokens = fsa.finish()
    assert_equal(1, len(tokens))


def test_differ_match_tricky():
    fsa = FSA.make_empty(allow_overlap=True)
    (fsa
     .add_state("start")
       .add_transition("a", "s1")
     .add_state("s1")
       .add_transition("b", "s2f")
     .add_state("s2f", terminal=True)
       .add_transition("c", "s3")
       .add_transition("c", "s7")
     .add_state("s3")
       .add_transition("d", "s4f")
     .add_state("s4f", terminal=True)
       .add_transition("e", "s5")
     .add_state("s5")
       .add_transition("f", "s6f")
     .add_state("s6f", terminal=True)
     .add_state("s7")
       .add_transition("h", "s8f")
       .set_default_transition("s7", silent=True)
     .add_state("s8f", terminal=True)
     .check_structure()
    )
    yield assert_matches, fsa, "ab", ["ab"]
    yield assert_matches, fsa, "abc", ["ab"]
    yield assert_matches, fsa, "abcd", ["abcd"]
    yield assert_matches, fsa, "abcde", ["abcd"]
    yield assert_matches, fsa, "abcdef", ["abcdef"]
    yield assert_matches, fsa, "abcdefh", ["abcdef", "abch"], False
    yield assert_matches, fsa, "abcdefz", ["abcdef"]
    yield assert_matches, fsa, "abcdh", ["abcd", "abch"], False
    yield assert_matches, fsa, "abcdhef", ["abcd", "abch"], False
    yield assert_matches, fsa, "abcdz", ["abcd"]
    yield assert_matches, fsa, "abce", ["ab"]
    yield assert_matches, fsa, "abch", ["abch"]
    yield assert_matches, fsa, "abchd", ["abch"]


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


def test_import_export_tokens():
    fsa = FSA.make_empty(max_noise=1, allow_overlap=True)
    (fsa
     .add_state("start")
       .add_transition("a", "s1")
     .add_state("s1")
       .add_transition("b", "s1")
       .add_transition("b", "s2")
       .add_transition("c", "finish")
     .add_state("s2", max_noise=1)
       .add_transition("d", "finish")
     .add_state("finish", terminal=True)
     .check_structure()
    )
    fsa.feed_all("abbb", False)
    saved = fsa.export_tokens_as_string()
    fsa.reset()
    fsa.load_tokens_from_str(saved)
    assert_matches(fsa, "cd", ["abbbc", "abbbd"], False)


def test_examples():
    dir = join(dirname(dirname(__file__)), "examples")
    with open(join(dir, "structure.json")) as f:
        fsa = FSA.from_file(f)
    yield assert_matches,  fsa, "daaad", ["dd", "aaad"], False
    yield assert_outcomes, fsa, "daaad", ["success", "error"], False

    with open(join(dir, "tokens.json")) as f:
        fsa.load_tokens_from_file(f)
    yield assert_matches,  fsa, "d", ["dd", "aaad"], False

    with open(join(dir, "tokens.json")) as f:
        fsa.load_tokens_from_file(f)
    yield assert_outcomes, fsa, "d", ["success", "error"], False

def test_default_matcher():
    fsa = FSA.make_empty()
    (fsa
     .add_state("start")
       .add_transition("[a-z]", "finish")
     .add_state("finish", terminal=True)
     .check_structure()
    )
    fsa.default_matcher = "regexp"
    assert_matches(fsa, ["[a-z]"], [])
    assert_matches(fsa, ["A"], [])
    assert_matches(fsa, ["M"], [])
    assert_matches(fsa, ["Z"], [])
    assert_matches(fsa, ["1"], [])
    assert_matches(fsa, ["!"], [])
    assert_matches(fsa, ["a"], ["a"])
    assert_matches(fsa, ["m"], ["m"])
    assert_matches(fsa, ["z"], ["z"])

def test_simultaneous_matches():
    fsa = FSA.make_empty()
    (fsa
     .add_state("start")
       .add_transition("a", "s1")
       .add_transition("a", "s2")
     .add_state("s1")
       .add_transition("b", "s3")
     .add_state("s2", max_noise=1)
       .add_transition("c", "s4")
     .add_state("s3", max_noise=1)
       .add_transition("d", "finish")
     .add_state("s4")
       .add_transition("d", "finish")
     .add_state("finish", terminal=True)
     .check_structure()
    )
    fsa.allow_overlap = True
    matches = fsa.feed_all("abcd")
    assert_equal(2, len(matches))
    
    fsa.reset()
    fsa.allow_overlap = False
    matches = fsa.feed_all("abcd")
    assert_equal(1, len(matches))
    

