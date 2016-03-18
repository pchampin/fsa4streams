==============
 Introduction
==============

.. todo::

   * explain how to use the library

     - demonstrating in particular the various ways to build noise-tolerant FSA's
       (silent transitions, default transitions, global and state max_noise),

     - explaining the notion of token,

     - explaining the role of `finish()`,
       and why a token on a final state may not immediately return a match;

   * the structure of tokens (as returned by `feed()` and `feed_all()`;

   * some of the design choices of the library,

     - especially why an empty sequence is never a match,
       even if the 'start' state is marked as terminal.


Bits and pieces
===============

Greedy matches
++++++++++++++

Automata will try to return the longest possible matches for a given stream.
This means that a match will not be detected as soon as it is detected,
as it may later yield a longer match.
To ensure that all pending matches are returned,
one must use the :meth:`~fsa4streams.fsa.FSA.finish` method.

For example, in the following FSA,
a match will not be returned immediately after ``a`` is received.
If the stream is ``abbbc`` (or ``abbb`` and then :meth:`~fsa4streams.fsa.FSA.finish`),
the only match will be ``abbb``.

.. digraph:: example_abstar

      rankdir=LR
      node[shape=circle,label=""]
      s0[label=start]
      s0  -> s1 [label=a]
      s1  -> s1 [label=b]
      s1[shape=doublecircle,label="end"]

This greedy behaviour must however be described more precisely:
a match A will inhibit another match B if:
* the sequence of events of B is a prefix of the sequence of events of A, **and**
* the terminal state of B has been reached at some point by A.

Hence, in the two following FSA fed with ``abbbc``, the only match will be ``abbb``,
even if ``allow_ovelap`` is set to ``true``.

.. digraph:: example_abstar_alt

      rankdir=LR
      node[shape=circle,label=""]
      s0[label=start]
      s0  -> s1 [label=a]
      s0  -> s2 [label=a]
      s1  -> s1 [label=b]
      s1  -> s2 [label=b]
      s2[shape=doublecircle,label="end"]

      t0[label=start]
      t0  -> t1 [label=a]
      t1  -> t2 [label=b]
      t2  -> t2 [label=b]
      t1[shape=doublecircle,label="end-a"]
      t2[shape=doublecircle,label="end-b"]

However, in the following FSA fed with ``abbbc`` and configured with ``allow_overlap`` set to ``true``,
two matches ``a`` and ``abbb`` will be returned,
as the former has a terminal state that was never reached by the latter.

.. digraph:: example_abstar_two_matches

      rankdir=LR
      node[shape=circle,label=""]
      s0[label=start]
      s0  -> s1 [label=a]
      s0  -> s2 [label=a]
      s2  -> s2 [label=b]
      s1[shape=doublecircle,label="end-a"]
      s2[shape=doublecircle,label="end-b"]


.. _overlapping_matches:

Overlapping matches
+++++++++++++++++++

   The noise-torelant FSM below, fed with ``ababab``,
   will only yield ``aaa`` if :js:attr:`fsa.allow_overlap` is set to false,
   but it will yield ``aaa`` and ``bbb`` if it is set to true.
   Note that, if fed with ``acaca``, with :js:attr:`fsa.allow_overlap` set to true,
   it will yield ``aaa`` and ``cca``,
   where the last ``a`` participates in both matches.

   .. digraph:: example_allow_overlap

      rankdir=LR
      node[shape=circle,label=""]
      s0[label=start]
      s0  -> sa1 [label=a]
      sa1 -> sa2 [label=a]
      sa2 -> end [label=a]
      end -> end [label=a]
      s0  -> sb1 [label=b]
      sb1 -> sb2 [label=b]
      sb2 -> end [label=b]
      s0  -> sc1 [label=c]
      sc1 -> sc2 [label=c]
      sc2 -> end [label=a]
      end[shape=doublecircle,label="end"]
      

   Note however that automata work in a greedy way,
   so the automaton above is fed with ``ccaa`` will only yield ``ccaa``,
   it will never yield ``cca``,
   regardless of `fsa.allow_overlap`:js:attr:.

   This notion of "greedyness" (greed?) can be tricky...
   It can be summed up 
   
Event sequence and timestamps
+++++++++++++++++++++++++++++

The :meth:``~fsa4streams.fsa.FSA.feed`` is used to feed the FSA with events.
It accepts an optional ``timestamp`` argument,
which is used to compute the duration
(see `~state.max_duration`:attr: and `~state.max_total_duration`:attr`).
While it would make no sense if an event had a timestamp smaller than a previous event,
it is allowed for an event to have the *same* timestamp as the previous one.
This is useful to represent that the duration between two events is zero
(*i.e.* too small to be measured).

It is important to understand, though,
that this does not override the *order* in which the events where fed,
which has precedence over the (possibly partial) order induced by the events.
In other words, if the FSA below is fed with B then A,
in that order but with the same timestamp,
it will *not* yield AB as a match.

.. digraph:: example_abstar

      rankdir=LR
      node[shape=circle,label=""]
      s0[label=start]
      s0  -> s1 [label=A]
      s1  -> s2 [label=B]
      s2[shape=doublecircle,label="end"]

