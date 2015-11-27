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

.. attribute:: fsa.max_noise

   An integer (optional).
   
   It indicates how many unrecognized events this automaton will accept before failing.
   If unspecified, the automaton will accept any amount of noise
   (provided that states themselves accept some noise).

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


State
=====

Every state is represented by a JSON object, with the following attributes:

.. attribute:: state.transitions

   A list of `transition objects <#transition>`_ (optional).

   Note that a state without any transitions must be `terminal`:attr`.

.. attribute:: state.terminal

   A boolean (optional).

   If false (default value),
   this state can not yield any match.
   If true,
   this is a terminal state so it may yield matches
   (but may not do,
   if the automaton manages to progress to a further terminal state).

.. attribute:: state.max_noise

   An integer (optional).
   
   It indicates how many unrecognized events this state will accept before failing.
   (in the limit imposed by `fsa.max_noise`:attr:).
   It defaults to 0, so by default automata are not noise-tolerant.

   This attribute can not be set together with `state.default_transition`:attr:.

.. attribute:: state.default_transition

   A `transition object <#transition>`_ with some (optional).

   It provides a transition to follow when an unrecognized event is encountered.
   This special transition can not have any `~transition.condition`:attr: or `~transition.matcher`:attr:.
   
   This attribute can not be set together with `state.max_noise`:attr:.
   

Transition
==========

Every transition is represented by a JSON object, with the following attributes:

.. attribute:: transition.condition

   A string (required).

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
   the `~transition.condition`:attr: will simply be tested for equality with the event. 

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

