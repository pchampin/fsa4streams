_NOT_SET = object()

def _make_state_property(name, default, check_value, doc):
    def getter(self):
        ret = self._data.get(name, _NOT_SET)
        if ret is _NOT_SET:
            defaults = self._fsa._structure.get('state_defaults')
            if defaults:
                ret = defaults.get(name, _NOT_SET)
        if ret is _NOT_SET:
            ret = default
        return ret

    def setter(self, value):
        if not check_value(value):
            raise ValueError('Invalid value for State.%s: %r'
                             % name, value)
    def deleter(self):
        del self._data[name]

    return property(getter, setter, deleter, doc)


class State(object):
    """A proxy object for a state in a FSA."""

    def __init__(self, fsa, stateid):
        self._fsa = fsa
        self._id = stateid
        self._data = fsa._structure['states'][stateid]

    @property
    def fsa(self):
        return self._fsa

    @property
    def id(self):
        return self._id

    terminal = _make_state_property('terminal',
                                    False,
                                    lambda v: type(v) is bool,
                                    "TODO doc")

    max_noise = _make_state_property('max_noise',
                                     0,
                                     lambda v: type(v) is int  and  int >=0,
                                     "TODO doc")

    max_total_noise = _make_state_property('max_total_noise',
                                     None,
                                     lambda v: type(v) is int  and  int >=0,
                                     "TODO doc")

    max_duration = _make_state_property('max_duration',
                                        None,
                                        lambda v: type(v) is int  and  int >0,
                                        "TODO doc")

    max_total_duration = _make_state_property('max_total_duration',
                                        None,
                                        lambda v: type(v) is int  and  int >0,
                                        "TODO doc")

    default_transition = _make_state_property('default_transition',
                                     None,
                                     lambda v: type(v) is dict,
                                     "TODO doc")

    @property
    def transitions(self):
        """TODO doc"""
        ret = self._data.get('transitions')
        if ret is None:
            ret = self._data['transitions'] = []
        return ret

    def add_state(self, *args, **kw):
        """Shortcut method to self.fsa.add_state,
        useful for chaining them."""
        return self._fsa.add_state(*args, **kw)

    def check_structure(self, raises=True):
        """Shortcut method to self.fsa.check_structure,
        useful for chaining them."""
        return self._fsa.check_structure(raises)

    def add_transition(self, condition, target, **kw):
        """TODO doc
        return this state to allow chaining
        IMPORTANT: 'target' may not exist yet, so it not checked.
        Hence, check_structure should be called in the end.
        """

        transition = {
            'condition': condition,
            'target': target,
        }
        transition.update(kw)
        self._data['transitions'].append(transition)
        return self

    def set_default_transition(self, target, **kw):
        """TODO doc
        return this state to allow chaining
        IMPORTANT: 'target' may not exist yet, so it not checked.
        Hence, check_structure should be called in the end.
        """
        transition = {
            'target': target,
        }
        transition.update(kw)
        self._data['default_transition'] = transition
        return self
