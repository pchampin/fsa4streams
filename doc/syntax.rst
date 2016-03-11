=================
 FSA Description
=================

.. default-domain:: js

This page describes the JSON_ format used to describe Finite State Automata.

.. _automata_syntax:

Automata
========

The FSA is represented by a JSON object, with the following attributes:

.. attribute:: fsa.states

   A JSON object (required).
   
   Its attributes are state names,
   and its values are `state objects <#state>`_.
   It must contain one state named ``start``,
   which will be the starting state.

.. attribute:: fsa.allow_override

   A boolean (optional).

   If false (default value),
   the automaton will drop all pending matches whenever a match is found.
   If true,
   the automaton may yield overlapping matches,
   possibly involving the same events.
   See `overriding_matches`:ref: for more details.

.. attribute:: fsa.state_defaults

   A `state object <#state>`_ (optional).

   It provides default values for all states of this automaton.

   NB: it can not have `~fsa.transitions`:attr:.

.. attribute:: fsa.default_matcher

   A string (optional).

   If provided,
   it indicates the function used to compare incoming events to the `~transition.condition`:attr:.
   It must be a key present in `fsa4streams.matcher.DIRECTORY`:py:data:.

   If not provided,
   a simple matcher will be used,
   checking whether the event is equal to the `transition.condition`:attr:.

State
=====

Every state is represented by a JSON object, with the following attributes:

.. attribute:: state.terminal

   A boolean (optional).

   If false (default value),
   this state can not yield any match.
   If true,
   this is a terminal state so it may yield matches
   (but may not do,
   if the automaton manages to progress to a further terminal state).

.. attribute:: state.transitions

   A list of `transition objects <#transition>`_ (optional).

   Note that a state without any transitions must be `terminal`:attr`.

.. attribute:: state.default_transition

   A `transition object <#transition>`_ with some restrictions (optional).

   It provides a transition to follow when an unrecognized event is encountered.
   This special transition can not have any `~transition.condition`:attr: or `~transition.matcher`:attr:.

   This attribute can not be set together with `~state.max_noise`:attr:.

.. attribute:: state.max_noise

   A non-negative integer (optional).
   
   It indicates how many unrecognized events can occur on this state before the automaton fails
   (in the limit imposed by `~state.max_total_noise`:attr:, if any).
   It defaults to 0, so by default states are not noise-tolerant.

   This attribute can not be set together with `~state.default_transition`:attr:.

.. attribute:: state.max_total_noise

   A non-negative integer (optional).

   This attribute is similar to `~state.max_noise`:attr: above,
   but instead of considering only the unrecognized events occuring on the this state,
   it also considers *all* unrecognized events encountered from the ``start`` state.
   If it is unspecified, the state will not be affected by previous noise.

   This attribute is particularly useful on terminal states,
   to prevent a match when it was too noisy overall.
   However, if it is the same for all the terminal states of the automaton,
   it is a good idea to set it in the `fsa.state_defaults`:attr:,
   so that the engine can prune searches *as soon* as a candidate match is too noisy
   (rather than wait for it to reach the terminal state to reject it).

.. attribute:: state.max_duration

   A positive integer (optional).

   It indicates the maximum in which the FSA will stay in this state.
   If no matching event occurs during this duration,
   the FSA will fail to match.
   It defaults to in infinity: if no max duration is specified,
   the FSA may stay an arbitrary long time in that state
   (in the limit imposed by `fsa.max_duration`:attr:).

.. attribute:: fsa.max_total_duration

   A positive integer (optional).

   This attribute is similar to `~state.max_duration`:attr: above,
   but instead of considering the duration since the automaton entered this state,
   it considers the total duration since the automaton entered the ``start`` state.
   If it is unspecified, the automaton will accept any duration.

   This attribute is particularly useful on terminal states,
   to prevent a match when it was too long overall.
   However, if it is the same for all the terminal states of the automaton,
   it is a good idea to set it in the `fsa.state_defaults`:attr:,
   so that the engine can prune searches *as soon* as a candidate match is too long
   (rather than wait for it to reach the terminal state to reject it).

Transition
==========

Every transition is represented by a JSON object, with the following attributes:

.. attribute:: transition.condition

   Any JSON object (required).

   The condition is compared to incoming events to check if the transition can be used.
   See also `transition.matcher`:attr:.

.. attribute:: transition.target

   A string (required).

   This is the identifier (in `fsa.states`:attr:) of the target state of this transition.

.. attribute:: transition.matcher

   A string (optional).

   If provided,
   it indicates the function used to compare incoming events to the `~transition.condition`:attr:.
   It must be a key present in `fsa4streams.matcher.DIRECTORY`:py:data:.

   If not provided,
   the `~fsa.default_matcher`:attr: will be used.

.. attribute:: transition.silent

   A boolean (optional).

   If it is set to false (default value),
   the event matching this transition will be included in the match.
   Otherwise,
   the transition will be used but the event will be simply discarded.


.. _JSON: http://www.json.org/


Example
=======

.. literalinclude:: ../examples/structure.json

.. digraph:: examples_structure

      rankdir=LR
      node[shape=circle]
      start -> start [label=a]
      start -> s1 [label=a]
      start -> s2 [label=d]
      s1 -> s1 [label=b]
      s1 -> success [label=c]
      s1 -> error [label=d]
      s2 -> success [label=d]
      s2 [label="s2 [4]"]
      success [shape=doublecircle]
      error [shape=doublecircle]

.. todo::

  May be also describe the format of the JSON files used to save tokens?...

