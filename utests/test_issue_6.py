from fsa4streams.fsa import FSA
from test_fsa import assert_matches
from unittest import skip

@skip('not fixed yet')
def test_issue_6_a():
    fsa = FSA.make_empty(allow_overlap=True)
    (fsa
     .add_state("start")
       .add_transition("a", "s1")
     .add_state("s1")
       .add_transition("b", "s2")
       .add_transition("b", "s3", silent=True)
     .add_state("s2", max_noise=1)
       .add_transition("c", "finish")
     .add_state("s3", max_noise=1)
       .add_transition("d", "finish")
     .add_state("finish", terminal=True)
     .check_structure()
    )
    assert_matches(fsa, "abcd", ["abc", "ad"])

@skip('not fixed yet')
def test_issue_6_b():
    fsa = FSA.make_empty(allow_overlap=True)
    (fsa
     .add_state("start")
       .add_transition("a", "s1")
     .add_state("s1")
       .add_transition("b", "s2", silent=True)
       .add_transition("b", "s3")
     .add_state("s2", max_noise=1)
       .add_transition("c", "finish")
     .add_state("s3", max_noise=1)
       .add_transition("d", "finish")
     .add_state("finish", terminal=True)
     .check_structure()
    )
    assert_matches(fsa, "abcd", ["ac", "abd"])

@skip('not fixed yet')
def test_issue_6_c():
    fsa = FSA.make_empty(allow_overlap=True)
    (fsa
     .add_state("start")
       .add_transition("a", "s1", silent=True)
     .add_state("s1")
       .add_transition("b", "s2")
     .add_state("s2")
       .add_transition("c", "finish")
     .add_state("finish", terminal=True)
     .check_structure()
    )
    assert_matches(fsa, "dbc", [])
    assert_matches(fsa, "dbcabcd", ["bc"])
