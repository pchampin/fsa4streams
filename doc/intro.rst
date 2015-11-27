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

.. _overriding_matches:

Overriding matches
++++++++++++++++++

   The noise-torelant FSM below, fed with ``ababab``,
   will yield ``aaa`` only if :js:attr:`fsa.allow_override` is set to false,
   but it will yield ``aaa`` and ``bbb`` if it is set to true.
   Note that, if fed with ``acaca``, with :js:attr:`fsa.allow_override` set to true,
   it will yield ``aaa`` and ``cca``,
   where the last ``a`` participates in both matches.

   .. digraph:: example_allow_override

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
   regardless of `fsa.allow_override`:js:attr:.


   
