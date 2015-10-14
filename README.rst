Finite State Automata for streams
=================================

This is a library for running Finite State Automata (FSA)
on bound and unbound streams of event.

It supports

* non-determininistic FSA's,
* noise-tolerant FSA's (i.e. ignoring some or all non-relevant events),
* overlapping matched,
* extensible matching functions for transitions.


TODO: proper documentation
--------------------------

It should describe:

* how to use the library, through tutorials

  - demonstrating in particular the various ways to build noise-tolerant FSA's
    (silent transitions, default transitions, global and state max_noise),

  - explaining the notion of token,

  - explaining the role of `finish()`,
    and why a token on a final state may not immediately return a match;

* the structure of tokens (as returned by `feed()` and `feed_all()`;

* the format of the JSON files used to store FSA structures,

  - may be also the format of the JSON files used to save tokens;

* how to write additional matcher functions,

  - and how they may be used to extend the expressiveness of FSA beyond regular grammars;

* some of the design choices of the library,

  - especially why an empty sequence is never a match,
    even if the 'start' state is marked as terminal.


Ideas for future extensions
---------------------------

* export to dot (for graphical presentation)
* toolkit for handling FSA's
  - optimizing
  - merging
* more built-in matchers?
  - prefix
  - more flexible regexp (i.e. not enforcing ^ and $)
* converter of regexp to automata
