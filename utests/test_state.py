from fsa4streams import FSA

class TestGlobalDefaults(object):

    def setup(self):
        self.to_error = {'target': 'error'}
        self.fsa = FSA.make_empty()
        (self.fsa
         .add_state("start")
           .add_transition("a", "s1")
         .add_state("s1", default_transition=self.to_error)
           .add_transition("b", "s2")
         .add_state("s2", max_noise=7)
           .add_transition("c", "finish")
         .add_state("finish", terminal=True)
         .add_state("error", terminal=True)
         .check_structure()
        )

    def test_default_max_noise(self):
        assert 0 == self.fsa['start'].max_noise

    def test_default_terminal(self):
        assert False == self.fsa['start'].terminal

    def test_default_default_transition(self):
        assert self.fsa['start'].default_transition is None

    def test_overridden_max_noise(self):
        assert 7 == self.fsa['s2'].max_noise

    def test_overridden_terminal(self):
        assert True == self.fsa['finish'].terminal

    def test_overridden_default_transition(self):
        assert self.fsa['s1'].default_transition is self.to_error


class TestLocalDefaults1(object):
    # NB: can not test together max_noise and default_transition,
    # as they are mutually incompatible.
    # So we have two variants of this test case.

    def setup(self):
        self.defaults = {
            'max_noise': 7,
            'terminal': True,
        }
        self.fsa = FSA.make_empty(state_defaults=self.defaults)
        (self.fsa
         .add_state("start", terminal=False, max_noise=0)
           .add_transition("a", "start")
           .add_transition("a", "s1")
         .add_state("s1")
           .add_transition("b", "s2")
         .add_state("s2")
         .add_state("error")
         .check_structure()
        )

    def test_default_max_noise(self):
        assert 7 == self.fsa['s1'].max_noise

    def test_default_terminal(self):
        assert True == self.fsa['s1'].terminal

    def test_overridden_max_noise(self):
        assert 0 == self.fsa['start'].max_noise

    def test_overridden_terminal(self):
        assert False == self.fsa['start'].terminal


class TestLocalDefaults2(object):

    def setup(self):
        self.defaults = {
            'default_transition': {
                'target': 'error'
            }
        }
        self.fsa = FSA.make_empty(state_defaults=self.defaults)
        (self.fsa
         .add_state("start")
           .add_transition("a", "start")
           .add_transition("a", "s1")
         .add_state("s1")
           .add_transition("b", "s2")
         .add_state("s2", termina=True)
         .add_state("error", terminal=True, default_transition=None)
         .check_structure()
        )

    def test_default_default_transition(self):
        assert self.fsa['s1'].default_transition \
               is self.defaults['default_transition']

    def test_overridden_default_transition(self):
        assert self.fsa['error'].default_transition is None
