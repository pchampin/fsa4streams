"""
Finite State Automata
"""
from __future__ import unicode_literals

from copy import deepcopy
from itertools import chain
import json
import logging
from uuid import uuid4

from matcher import DIRECTORY as matcher_directory
from state import State

LOG = logging.getLogger(__name__)

class FSA(object):
    """A Finite State Automaton."""

    # FSA constuction
    
    def __init__(self, structure, check_structure=True):
        """
        DON'T USE THIS CONSTRUCTOR DIRECTLY.
        YOU SHOULD RATHER USE ONE OF THE from_* STATIC METHODS.
        """
        self._structure = structure
        self._tokens = { 'clock': 0, 'running': {}, 'pending': {} }
        if check_structure:
            self.check_structure(True)

    @classmethod
    def from_str(cls, json_str):
        return cls(json.loads(json_str))

    @classmethod
    def from_file(cls, json_filelike):
        return cls(json.load(json_filelike))

    @classmethod
    def from_dict(cls, dictobj):
        return cls(deepcopy(dictobj))

    @classmethod
    def make_empty(cls, **kw):
        "TODO doc: must call :meth:`check_structure` in the end"
        data = { 'states': {}}
        data.update(kw)
        return cls(data, False)

    def add_state(self, stateid, **kw):
        """TODO doc

        IMPORTANT: 'target' may not exist yet, so it not checked.
        Hence, :meth:`check_structure` should be called in the end.
        """
        if stateid in self._structure['states']:
            raise ValueError("State %r already present in FSA" % stateid)
        self._structure['states'][stateid] = data = { 'transitions': [] }
        data.update(kw)
        return State(self, stateid)

    def check_structure(self, raises=True):
        problems = []

        default_matcher = self._structure.get('default_matcher')
        if default_matcher is not None \
        and default_matcher not in matcher_directory:
            problems.append("Unsupported default matcher %r" % default_matcher)

        states = self._structure['states']
        if not 'start' in states:
            problems.append("No start state")
        terminals = 0
        for stateid in states:
            state = State(self, stateid)
            terminal = state.terminal
            transitions = list(state.transitions)
            deftrans = state.default_transition
            if terminal:
                terminals += 1
            if not transitions and not deftrans and not terminal:
                problems.append("Non-terminal state %r has no transition" %
                                stateid)
                # NB: we do not check if it has only self-targeted transition
                # which would be equally bad...
                # TODO Should we?
            if deftrans:
                if state.max_noise != 0:
                    problems.append("State %r can not have both a default "
                                    "transition and max_noise > 0" % stateid)
                transitions = chain(transitions, [deftrans])
            for transition in transitions:
                if transition['target'] not in states:
                    problems.append("Transition to non-existing state %r" %
                                    transition['target'])
                matcher = transition.get('matcher')
                if matcher is not None \
                and matcher not in matcher_directory:
                    problems.append("Unsupported matcher %r" % matcher)
        if terminals == 0:
            problems.append("No terminal state")
            # NB: we do not check that the terminal state is reachable from starte state...
            # TODO Should we?

        if problems:
            raise ValueError("\n".join(problems))
        return problems
                

    # access to structure

    def __getitem__(self, stateid):
        return State(self, stateid)

    @property
    def max_noise(self):
        return self._structure.get('max_noise')
    @max_noise.setter
    def max_noise(self, value):
        if type(value) is not int  or  value < 0:
            raise ValueError('FSA.max_noise must be a non-negative int')
        self._structure['max_noise'] = value
    @max_noise.deleter
    def max_noise(self):
        del self._structure['max_noise']

    @property
    def max_duration(self):
        return self._structure.get('max_duration')
    @max_duration.setter
    def max_duration(self, value):
        if type(value) is not int  or  value <= 0:
            raise ValueError('FSA.max_duration must be a positive int')
        self._structure['max_duration'] = value
    @max_duration.deleter
    def max_duration(self):
        del self._structure['max_duration']

    @property
    def allow_overlap(self):
        return self._structure.get('allow_overlap', False)
    @allow_overlap.setter
    def allow_overlap(self, value):
        if type(value) is not bool:
            raise ValueError('FSA.allow_overlap must be a bool')
        self._structure['allow_overlap'] = value
    @allow_overlap.deleter
    def allow_overlap(self):
        del self._structure['allow_overlap']

    @property
    def default_matcher(self):
        return self._structure.get('default_matcher')
    @default_matcher.setter
    def default_matcher(self, value):
        if value not in matcher_directory:
            raise ValueError('FSA.default_matcher must be in matcher.DIRECTORY')
        self._structure['default_matcher'] = value
    @default_matcher.deleter
    def default_matcher(self):
        del self._structure['default_matcher']

    def export_structure_as_dict(self):
        return deepcopy(self._structure)

    def export_structure_as_string(self, *args, **kw):
        return json.dumps(self._structure, *args, **kw)

    def export_strutcure_to_file(self, fp, *args, **kw):
        return json.dump(self._structure, fp, *args, **kw)


    # tokens management

    def reset(self):
        self._tokens['running'].clear()
        self._tokens['pending'].clear()
        self._tokens['clock'] = 0

    def is_busy(self):
        return len(self._tokens['running']) > 0 \
            or len(self._tokens['pending']) > 0

    def load_tokens_from_str(self, json_str, force=False):
        if self.is_busy() and not force:
            raise ValueError('Can not load a tokens on a busy FSA')
        self._tokens = json.loads(json_str)
        self._check_tokens()

    def load_tokens_from_file(self, json_filelike, force=False):
        if self.is_busy() and not force:
            raise ValueError('Can not load a tokens on a busy FSA')
        self._tokens = json.load(json_filelike)
        self._check_tokens()

    def load_tokens_from_dict(self, dictobj, force=False):
        if self.is_busy() and not force:
            raise ValueError('Can not load a tokens on a busy FSA')
        self._tokens = deepcopy(dictobj)
        self._check_tokens()

    def _check_tokens(self):
        states = self._structure['states']
        all_tokens = chain(self._tokens['running'].iteritems(),
                           self._tokens['pending'].iteritems())
        for tokenid, token in all_tokens:
            if token['state'] not in states:
                raise ValueError("Inconsistent position "
                                 "(non-existing state %r)"
                                     % token['state'])

    def export_tokens_as_dict(self):
        return deepcopy(self._tokens)

    def export_tokens_as_string(self, *args, **kw):
        return json.dumps(self._tokens, *args, **kw)

    def export_tokens_to_file(self, fp, *args, **kw):
        return json.dump(self._tokens, fp, *args, **kw)


    # running the FSA

    def match(self, transition, event, token):
        transition_type = transition.get('matcher') or self.default_matcher
        if transition_type is None:
            return transition['condition'] == event
        else:
            return matcher_directory[transition_type](transition, event, token, self)

    def _delete_token(self, tokenid, token, token_state,
                      running, pending, matches):
        del running[tokenid]
        is_match = token_state.terminal
        if is_match:
            LOG.debug('    matched')
            matches.append(token)
        else:
            LOG.debug('    was dropped')
        otherid = token.get('inhibits')
        if otherid is None:
            return
        other = pending.get(otherid)
        if other is None:
            # it has already been deleted
            return
        LOG.debug('    it was inhibiting a pending match in %r', other['state'])
        must_delete = is_match and (
            other['state'] == token['state']
            or other['state'] in token ['history_states']
        )
        if must_delete:
            del pending[otherid]
        else:
            if not [ t for t in running.itervalues() if t.get('inhibits') == otherid ]:
                # noone else was inhibiting 'other',
                # so 'other' is not inhibited anymore
                del pending[otherid]
                matches.append(other)
                LOG.debug('      making it an actual match')


    def feed(self, event, timestamp=None):
        """
        I ingest `event`, and I return a list of matching tokens.

        A matching token is a token that has reached a final state,
        and can not further progress in the FSA.

        If provided,
        ``timestamp`` must be an integer greater than all previous timestamps;
        the default value is the previous timestamp + 1.
        Timestamps are used to check ``max_duration`` constraints.
        """
        clock = self._tokens['clock']
        running = self._tokens['running']
        pending = self._tokens['pending']
        skip_create = False
        matches = []

        if timestamp is None:
            timestamp = clock
        else:
            assert timestamp >= clock

        LOG.debug('event %r at timestamp %s', event, timestamp)

        # Make each running token take the event into account
        # - some of them will walk through a transition,
        # - some of them will stay in place (if their noise counter allows it),
        # - the others will be removed.
        # A token removed from a final state is a match,
        # else it is plainly discarded.
        for tokenid, token in running.items():

            oldstateid = token['state']
            LOG.debug('  token in %r', oldstateid)
            oldstate = self[oldstateid]

            # delete token if a max_duration has expired
            duration = timestamp-token['updated']
            if self.max_duration \
            and timestamp-token['created'] > self.max_duration \
            or oldstate.max_duration \
            and timestamp-token['updated'] > oldstate.max_duration:
                LOG.debug('    was dropped because it exceeded max_duration')
                self._delete_token(tokenid, token, oldstate, running, pending, matches)
                continue


            possible_transitions = [ t for t in oldstate.transitions
                            if self.match(t, event, token) ]
            if not possible_transitions:
                deftrans = oldstate.default_transition
                if deftrans:
                    possible_transitions = [ deftrans ]

            # deleting token (it may or may not match)
            if not possible_transitions:
                LOG.debug('    added noise')
                token['noise_state'] += 1
                token['noise_global'] += 1
                if token['noise_state'] > oldstate.max_noise \
                or self.max_noise is not None \
                and token['noise_global'] > self.max_noise:
                    self._delete_token(tokenid, token, oldstate, running, pending, matches)
                continue

            if oldstateid == 'start':
                # an old token is on start,
                # so any new token starting there would be redundant
                skip_create = True

            # this token *might* be a match
            # if no further transition leads to a match;
            if oldstate.terminal:
                LOG.debug('    keeping a pending match')
                otherid = token.pop('inhibits', None)
                if otherid:
                    # pending token is overriden by this new match
                    previous = pending.pop(otherid, None)
                    # NB: inhibited token may have been deleted already
                    if previous is not None:
                        LOG.debug('      and dropping previous pending match in %r',
                                  previous['state'])
                # create new pending token
                newid = uuid4().hex
                pending_token = deepcopy(token)
                pending[newid] = pending_token
                token['inhibits'] = newid

            # pushing token through first transition
            LOG.debug('    moved to %r', possible_transitions[0]['target'])
            token['state'] = possible_transitions[0]['target']
            token['noise_state'] = 0
            token['updated'] = timestamp
            if not possible_transitions[0].get('silent'):
                token['history_events'].append(event)
                token['history_states'].append(oldstateid)
            else:
                LOG.debug('      (silently)')

            # cloning token through other transitions (non-deterministic FSA)
            for transition in possible_transitions[1:]:
                LOG.debug('    also moved to %r', transition['target'])
                newtoken = deepcopy(token)
                newtoken['state'] = transition['target']
                newid = uuid4().hex
                running[newid] = newtoken

        # Create a new token for each transition of the 'start' state
        # that is satisfied by the current event
        # (unless an existing token just left the start state).
        if not skip_create:
            starting_transitions = [ t for t in self['start'].transitions
                                     if self.match(t, event, None) ]
            if starting_transitions:
                forbidden = set( t['state'] for t in running.itervalues()
                                 if t['noise_state'] == 0 )

                for transition in starting_transitions:
                    if transition['target'] in forbidden:
                        continue
                    LOG.debug('  new token in %r', transition['target'])
                    newtoken = {
                        "state": transition['target'],
                        "created": timestamp,
                        "updated": timestamp,
                        "noise_state": 0,
                        "noise_global": 0,
                        "history_events": [ event ],
                        "history_states": []
                    }
                    newid = uuid4().hex
                    running[newid] = newtoken

        # Immediately handle tokens on a final state with no transition
        # (no need to wait for the next event to do that...)
        # This may not result to an immediate match if another running token
        # has the exact same history...
        for tokenid, token in running.items():
            token_state = self[token['state']]
            if token_state.terminal and len(token_state.transitions) == 0:
                LOG.debug('  token now in %r (final)', token['state'])
                inhibited = False
                for otherid, other in running.items():
                    if other is token:
                        continue
                    if other['history_events'] == token['history_events']:
                        LOG.debug('    is kept pending (inhibited by token in %r)', other['state'])
                        inhibitedid = other.get('inhibits')
                        if inhibitedid is not None:
                            dropped = pending.pop(inhibitedid, None)
                            if dropped:
                                if dropped['state'] == token['state'] \
                                or dropped['state'] in token['history_states']:
                                    LOG.debug('      dropping older pending token in %r',
                                              dropped['state'])
                                else:
                                    matches.append(dropped)
                                    LOG.debug('      freeing older pending token in %r to match',
                                              dropped['state'])
                        other['inhibits'] = tokenid
                        inhibited = True
                if inhibited:
                    pending[tokenid] = token
                    del running[tokenid]
                else:
                    self._delete_token(tokenid, token, token_state, running, pending, matches)

        self._tokens['clock'] = clock = timestamp+1

        if matches and not self.allow_overlap:
            # drop all remaining tokens overlapping with matches,
            max_updated = max (match['updated'] for match in matches )
            for d in (running, pending):
                for tokenid, token in d.items():
                    if token['created'] <= max_updated:
                        del d[tokenid]
                        LOG.debug('  dropping token %r to prevent overlap',
                                  tokenid)
            # drop all matches that are overlapped by another match
            if len(matches) > 1:
                min_created = min( match['created'] for match in matches)
                matches = [ match for match in matches
                            if match['created'] == min_created ]
                if len(matches) > 1:
                    matches = matches[:1]
                LOG.debug("to prevent overlap, only 1 match kept")

        return matches

    def feed_all(self, iterable, finish=True):
        ret = []
        for event in iterable:
            ret += self.feed(event)
        if finish:
            ret += self.finish()
            self.reset()
        return ret

    def feed_all_timestamps(self, iterable, finish=True):
        ret = []
        for event, timestamp in iterable:
            ret += self.feed(event, timestamp)
        if finish:
            ret += self.finish()
            self.reset()
        return ret

    def finish(self):
        LOG.debug('finishing')
        running = self._tokens['running']
        pending = self._tokens['pending']
        matches = []
        for tokenid, token in running.items():
            LOG.debug('  token in %r', token['state'])
            token_state = self[token['state']]
            self._delete_token(tokenid, token, token_state,
                               running, pending, matches)
        if matches and not self.allow_overlap:
            min_created = min( match['created'] for match in matches)
            matches = [ match for match in matches
                        if match['created'] == min_created ]
        self.reset()
        LOG.debug('  returns %s match(es)', len(matches))
        return matches
