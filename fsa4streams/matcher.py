"""
.. data:: DIRECTORY
   :annotation: = a dict

   It originally contains all the matchers contained in this module.

"""

from re import match as re_match

def match_multiple_choices(transition, event, _token, _fsa):
    """
    The 'multiple-choices' matcher.

    With this matcher,
    transition conditions must be lists of strings.
    It matches an event if that event is equal to *one* of the items of the list.
    """
    return event in transition['condition']

def match_regexp(transition, event, _token, _fsa):
    """
    The 'regexp' matcher.

    With this matcher,
    transition conditions are interpreted as regular expressions.
    Note that the *whole* event must match the regular expression
    (this is ensured by automatically prepending ``^`` and appending ``$`` to the condition).
    """
    return re_match('^%s$' % transition['condition'], event)

DIRECTORY = {
    'multiple-choices': match_multiple_choices,
    'regexp': match_regexp,
}
