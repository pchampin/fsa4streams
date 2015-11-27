.. FSA for streams documentation master file, created by
   sphinx-quickstart on Tue Nov 24 16:16:37 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

=================
 FSA for streams
=================

This is a library for running Finite State Automata (FSA)
on bound and unbound streams of event.

It supports

* non-determininistic FSA's,
* noise-tolerant FSA's (i.e. ignoring some or all non-relevant events),
* overlapping matched,
* extensible matching functions for transitions.

.. rubric:: Contents

.. toctree::
   :maxdepth: 2
              
   intro
   syntax
   dev   

   
.. rubric:: Indices and tables

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. todo::

  Explain somewhere how to write additional matcher functions,
  and how they may be used to extend the expressiveness of FSA beyond regular grammars...

