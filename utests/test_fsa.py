from fsa4streams.fsa import FSA, LOG

from os.path import dirname, join

from pytest import mark

def process(fsa, events, ordered=True, timestamps=None):
    if timestamps:
        pairs = zip(events, timestamps)
        tokens = fsa.feed_all_timestamps(pairs)
    else:
        tokens = fsa.feed_all(events)
    matches = [ "".join(token['history_events']) for token in tokens ]
    outcomes = [ token['state'] for token in tokens ]
    if not ordered:
        matches = set(matches)
        outcomes = set(outcomes)
    return matches, outcomes

def assert_matches(fsa, events, expected_matches, ordered=True, timestamps=None):
    got, _ = process(fsa, events, ordered, timestamps)
    if ordered:
        assert expected_matches == got
    else:
        assert set(expected_matches) == got
    LOG.debug("---")

def assert_outcomes(fsa, events, expected_outcomes, ordered=True, timestamps=None):
    _, got = process(fsa, events, ordered, timestamps)
    if ordered:
        assert expected_outcomes == got
    else:
        assert set(expected_outcomes) == got
    LOG.debug("---")


@mark.parametrize('string, matches', [
    ("a",     ["a"]),
    ("b",     []),
    ("babab", ["a", "a"]),
])
def test_super_simple(string, matches):
    fsa = FSA.make_empty()
    (fsa
     .add_state("start")
       .add_transition("a", "finish")
     .add_state("finish", terminal=True)
     .check_structure()
    )
    assert_matches(fsa, string, matches)


@mark.parametrize('string, matches', [
    ("",       []),
    ("a",      ["a"]),
    ("aa",     ["aa"]),
    ("aaa",    ["aaa"]),
    ("b",      []),
    ("ba",     ["a"]),
    ("baa",    ["aa"]),
    ("ab",     ["a"]),
    ("aab",    ["aa"]),
    ("aabaaa", ["aa", "aaa"]),
])
def test_a_star(string, matches):
    fsa = FSA.make_empty()
    (fsa
     .add_state("start", terminal=True)
       .add_transition("a", "start")
     .check_structure()
    )
    assert_matches(fsa, string, matches)


@mark.parametrize('string, matches', [
    ("a",       ["a"]),
    ("aa",      ["a", "a"]),
    ("ab",      ["ab"]),
    ("abb",     ["abb"]),
    ("abbb",    ["abbb"]),
    ("c",       []),
    ("ac",      ["a"]),
    ("abc",     ["ab"]),
    ("abbc",    ["abb"]),
    ("ca",      ["a"]),
    ("cab",     ["ab"]),
    ("cabb",    ["abb"]),
    ("abbabbb", ["abb", "abbb"]),
])
def test_a_b_star(string, matches):
    fsa = FSA.make_empty()
    (fsa
     .add_state("start")
       .add_transition("a", "finish")
     .add_state("finish", terminal=True)
       .add_transition("b", "finish")
     .check_structure()
    )
    assert_matches(fsa, string, matches)

@mark.parametrize('string, matches', [
    ("aaa",     ["aaa"]),
    ("abaa",    ["aaa"]),
    ("abbaa",   ["aaa"]),
    ("abbbaa",  []),
    ("aaba",    ["aaa"]),
    ("aabba",   ["aaa"]),
    ("aabbba",  []),
    ("ababa",   ["aaa"]),
    ("abbaba",  ["aaa"]),
    ("ababba",  ["aaa"]),
    ("abbabba", ["aaa"]),
])
def test_noise(string, matches):
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
    assert_matches(fsa, string, matches)


@mark.parametrize('string, matches', [
    ("aaa",     ["aaa"]),
    ("abaa",    ["aaa"]),
    ("abbaa",   ["aaa"]),
    ("abbbaa",  []),
    ("aaba",    ["aaa"]),
    ("aabba",   ["aaa"]),
    ("aabbba",  []),
    ("ababa",   ["aaa"]),
    ("abbaba",  ["aaa"]),
    ("ababba",  ["aaa"]),
    ("abbabba", []),
])
def test_total_noise(string, matches):
    fsa = FSA.make_empty()
    (fsa
     .add_state("start")
       .add_transition("a", "s1")
     .add_state("s1", max_noise=2)
       .add_transition("a", "s2")
     .add_state("s2", max_noise=2)
       .add_transition("a", "finish")
     .add_state("finish", terminal=True, max_total_noise=3)
     .check_structure()
    )
    assert_matches(fsa, string, matches)


@mark.parametrize('string, matches', [
    ("ab",   ["ab"]),
    ("ac",   ["ac"]),
    ("abc",  ["ab"]),
    ("acb",  ["ac"]),
    ("adbc", []),
])
def test_non_deterministic(string, matches):
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
    assert_matches(fsa, string, matches)


@mark.parametrize('string, matches', [
    ("ab",   ["ab"]),
    ("ac",   ["ac"]),
    ("abc",  ["ab"]),
    ("acb",  ["ac"]),
    ("adbc", ["ab"]),
])
def test_non_deterministic_noise(string, matches):
    fsa = FSA.make_empty()
    (fsa
     .add_state("start")
       .add_transition("a", "s1")
       .add_transition("a", "s2")
     .add_state("s1", max_noise=1)
       .add_transition("b", "finish")
     .add_state("s2", max_noise=1)
       .add_transition("c", "finish")
     .add_state("finish", terminal=True, max_total_noise=1)
     .check_structure()
    )
    assert_matches(fsa, string, matches)


@mark.parametrize('string, matches', [
    ("ab",   ["ab"]),
    ("ac",   ["ac"]),
    ("abc",  ["ab", "ac"]),
    ("acb",  ["ac", "ab"]),
    ("adbc", ["ab"]),
])
def test_non_deterministic_noise_overlap(string, matches):
    fsa = FSA.make_empty(allow_overlap=True,
                         state_defaults={'max_noise': 1, 'max_total_noise': 1})
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
    assert_matches(fsa, string, matches)


@mark.parametrize('string, matches', [
    ("abc", ["ab", "bc", "ac"]),
])
def test_overlapping_pairs(string, matches):
    fsa = FSA.make_empty(allow_overlap=True)
    (fsa
     .add_state("start")
       .add_transition(".", "s1", matcher="regexp")
       .add_transition(".", "s2", matcher="regexp")
     .add_state("s1", max_noise=1)
       .add_transition("b", "finish")
     .add_state("s2", max_noise=1)
       .add_transition("c", "finish")
     .add_state("finish", terminal=True)
     .check_structure()
    )
    assert_matches(fsa, string, matches, ordered=False)


@mark.parametrize('string, matches, outcomes', [
    ("ab",    ["ab"],        ['error'],),
    ("aab",   ["aab"],       ['error'],),
    ("aaa",   ["aaa"],       ['finish']),
    ("aaab",  ["aaa"],       ['finish']),
    ("aaaab", ["aaa", "ab"], ['finish', 'error']),
])
class TestDefaultTransition:
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

    def test_outcomes(self, string, matches, outcomes):
        assert_outcomes(self.fsa, string, outcomes)

    def test_matches(self, string, matches, outcomes):
        assert_matches(self.fsa, string, matches)


class TestDefaultTransitionOverlap:
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

    @mark.parametrize("string, outcomes", [
        ("ab",    ['error']),
        ("aab",   ['error', 'error']),
        ("aaa",   ['finish']),
        ("aaab",  ['finish', 'error', 'error']),
        ("aaaab", ['finish', 'finish', 'error', 'error']),
    ])
    def test_outcomes(self, string, outcomes):
        assert_outcomes(self.fsa, string, outcomes)

    @mark.parametrize("string, matches", [
        ("ab",  ["ab"]),
        ("aab", ["ab", "aab"]),
    ])
    def test_matches(self, string, matches):
        assert_matches(self.fsa, string, matches, ordered=False)


@mark.parametrize("string, matches", [
    ("ab",  ["a"]),
    ("aab", ["aa"]),
])
def test_silent_default_transition(string, matches):
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
    assert_matches(fsa, string, matches)


class TestSilentDefaultTransitionLoop:
    fsa = FSA.make_empty()
    (fsa
     .add_state("start")
       .add_transition("a", "s1")
     .add_state("s1", default_transition={'target': 's1', 'silent':True})
       .add_transition("a", "finish")
     .add_state("finish", terminal=True)
     .check_structure()
    )

    def test_matches(self):
        assert_matches(self.fsa, "abba", ["aa"])

    def test_history_states(self):
        tokens = self.fsa.feed_all("abba")
        assert len(tokens) == 1
        assert ['s1'] == tokens[0]['history_states']


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
    assert 1 == len(tokens)


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
    assert 0 == len(tokens)
    tokens = fsa.feed("c")
    assert 0 == len(tokens)
    tokens = fsa.feed("c")
    assert 0 == len(tokens)
    tokens = fsa.finish()
    assert 1 == len(tokens)


@mark.parametrize("string, matches, ordered", [
    ("ab", ["ab"], True),
    ("abc", ["ab"], True),
    ("abcd", ["abcd"], True),
    ("abcde", ["abcd"], True),
    ("abcdef", ["abcdef"], True),
    ("abcdefh", ["abcdef", "abch"], False),
    ("abcdefz", ["abcdef"], True),
    ("abcdh", ["abcd", "abch"], False),
    ("abcdhef", ["abcd", "abch"], False),
    ("abcdz", ["abcd"], True),
    ("abce", ["ab"], True),
    ("abch", ["abch"], True),
    ("abchd", ["abch"], True),
])
def test_differ_match_tricky(string, matches, ordered):
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
    assert_matches(fsa, string, matches, ordered)


def test_import_export_tokens():
    fsa = FSA.make_empty(allow_overlap=True)
    (fsa
     .add_state("start")
       .add_transition("a", "s1")
     .add_state("s1")
       .add_transition("b", "s1")
       .add_transition("b", "s2")
       .add_transition("c", "finish")
     .add_state("s2", max_noise=1)
       .add_transition("d", "finish")
     .add_state("finish", terminal=True, max_total_noise=1)
     .check_structure()
    )
    fsa.feed_all("abbb", False)
    saved = fsa.export_tokens_as_string()
    fsa.reset()
    fsa.load_tokens_from_str(saved)
    assert_matches(fsa, "cd", ["abbbc", "abbbd"], False)


def test_examples():
    folder = join(dirname(dirname(__file__)), "examples")
    with open(join(folder, "structure.json")) as f:
        fsa = FSA.from_file(f)
    gotm, goto = process(fsa, "daaad", False)
    assert {"dd", "aaad"} == gotm
    assert {"success", "error"} == goto

    with open(join(folder, "tokens.json")) as f:
        fsa.load_tokens_from_file(f)
    assert {"dd", "aaad"} == gotm
    assert {"success", "error"} == goto


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
    assert 2 == len(matches)

    fsa.reset()
    fsa.allow_overlap = False
    matches = fsa.feed_all("abcd")
    assert 1 == len(matches)


def test_non_trivial_greedy():
    fsa = FSA.from_dict({
        "allow_overlap": True,
        "states": {
            "start": {
                "transitions": [
                    { "condition": "a", "target": "s2" },
                    { "condition": "a", "target": "s1" },
                ],
            },
            "s1": {
                "transitions": [
                    { "condition": "b", "target": "s1" },
                    { "condition": "b", "target": "s2" },
                ],
            },
            "s2": {
                "terminal": True,
            }
        }
    })
    matches = fsa.feed_all("abbb")
    assert 1 == len(matches)
    assert ["a", "b", "b", "b"] == matches[0]['history_events']


def test_even_less_trivial_greedy():
    fsa = FSA.from_dict({
        "allow_overlap": True,
        "states": {
            "start": {
                "transitions": [
                    { "condition": "a", "target": "s1" },
                    { "condition": "a", "target": "s2" },
                ],
            },
            "s1": {
                "terminal": True,
            },
            "s2": {
                "transitions": [
                    { "condition": "b", "target": "s2" },
                    { "condition": "b", "target": "s3" },
                ],
            },
            "s3": {
                "terminal": True,
            }
        }
    })
    matches = fsa.feed_all("abbb")
    assert 2 == len(matches)
    histories = [ m['history_events'] for m in matches ]
    assert ["a"] in histories
    assert ["a", "b", "b", "b"] in histories


def test_redundant_paths():
    fsa = FSA.from_dict({
        "allow_overlap": True,
        "states": {
            "start": {
                "transitions": [
                    { "condition": "a", "target": "s1" },
                    { "condition": "a", "target": "s2" },
                ],
            },
            "s1": {
                "transitions": [
                    { "condition": "b", "target": "s3" },
                ],
            },
            "s2": {
                "transitions": [
                    { "condition": "b", "target": "s3" },
                ],
            },
            "s3": {
                "terminal": True,
            }
        }
    })
    matches = fsa.feed_all("ab")
    assert 1 == len(matches)


@mark.parametrize("string, matches, ordered, timestamps", [
    ("a", ["a"], True, [1]),
    ("aa", ["a", "a"], True, [1, 3]),
    ("ab", ["ab"], True, [1, 3]),
    ("abb", ["abb"], True, [3, 5, 8]),
    ("abbb", ["abbb"], True, [13, 21, 34, 45]),
    ("c", [], True, [79]),
    ("ac", ["a"], True, [1, 3]),
    ("abc", ["ab"], True, [3, 5, 8]),
    ("abbc", ["abb"], True, [13, 21, 34, 45]),
    ("ca", ["a"], True, [3, 5]),
    ("cab", ["ab"], True, [5, 8, 13, 21]),
    ("cabb", ["abb"], True, [34, 45, 79, 124]),
    ("abbabbb", ["abb", "abbb"], True, [1,3,5,7,9,11,13]),
    ("abbabbb", ["abb", "abbb"], True, [1,3,5,7,9,11,13]),
])
def test_a_b_star_with_timestamps(string, matches, ordered, timestamps):
    fsa = FSA.make_empty()
    (fsa
     .add_state("start")
       .add_transition("a", "finish")
     .add_state("finish", terminal=True)
       .add_transition("b", "finish")
     .check_structure()
    )
    assert_matches(fsa, string, matches, ordered, timestamps)


@mark.parametrize("assert_matches_args", [
    ("a", ["a"]),
    ("aa", ["a", "a"]),
    ("ab", ["ab"]),
    ("abb", ["abb"]),
    ("abbb", ["abb"]),
    ("c", []),
    ("ac", ["a"]),
    ("abc", ["ab"]),
    ("abbc", ["abb"]),
    ("ca", ["a"]),
    ("cab", ["ab"]),
    ("cabb", ["abb"]),
    ("abbabbb", ["abb", "abb"]),
    ("ab", ["a"], True, [1, 4]),
])
def test_a_b_star_with_max_total_duration(assert_matches_args):
    fsa = FSA.make_empty()
    (fsa
     .add_state("start")
       .add_transition("a", "finish")
     .add_state("finish", terminal=True, max_total_duration=2)
       .add_transition("b", "finish")
     .check_structure()
    )
    assert_matches(fsa, *assert_matches_args)


@mark.parametrize("string, matches, ordered, timestamps", [
    ("a", ["a"], True, [1]),
    ("aa", ["a", "a"], True, [1, 2]),
    ("ab", ["ab"], True, [1, 3]),
    ("abb", ["abb"], True, [1, 2, 3]),
    ("abb", ["ab"], True, [1, 2, 5]),
])
def test_a_b_star_with_state_max_duration(string, matches, ordered, timestamps):
    fsa = FSA.make_empty()
    (fsa
     .add_state("start")
       .add_transition("a", "finish")
     .add_state("finish", terminal=True, max_duration=2)
       .add_transition("b", "finish")
     .check_structure()
    )
    assert_matches(fsa, string, matches, ordered, timestamps)


def test_negative_timestamp():
    fsa = FSA.make_empty()
    (fsa
     .add_state("start")
       .add_transition("a", "finish")
     .add_state("finish", terminal=True, max_duration=2)
       .add_transition("b", "finish")
     .check_structure()
    )
    assert_matches(fsa, "ab", ["ab"], True, [-2, -1])


def test_negative_timestamp_after_reset():
    fsa = FSA.make_empty()
    (fsa
     .add_state("start")
       .add_transition("a", "finish")
     .add_state("finish", terminal=True, max_duration=2)
       .add_transition("b", "finish")
     .check_structure()
    )
    fsa.feed("a", 42)
    fsa.reset()
    assert_matches(fsa, "ab", ["ab"], True, [-2, -1])


def test_equal_timestamp():
    fsa = FSA.make_empty()
    (fsa
     .add_state("start")
       .add_transition("a", "finish")
     .add_state("finish", terminal=True, max_duration=2)
       .add_transition("b", "finish")
     .check_structure()
    )
    assert_matches(fsa, "ab", ["ab"], True, [42, 42])
