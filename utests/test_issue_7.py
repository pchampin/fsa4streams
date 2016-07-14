from fsa4streams.fsa import FSA
from test_fsa import assert_matches
from unittest import skip

@skip('not fixed yet')
def test_issue_7():
    fsa = FSA.from_dict({
        "allow_overlap": True,
        "states": {
            "start": {
                "default_transition": {
                    "target": "s1"
                }
            },
            "s1": {
                "default_transition": {
                    "target": "s2"
                }
            },
            "s2": {
                "terminal": True
            }
        }
    })
    assert_matches(fsa, "ab", ["ab"])

