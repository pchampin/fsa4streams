"""
.. data:: DIRECTORY
   :annotation: = a dict

   It originally contains all the matchers contained in this module.

"""

from re import match as re_match

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
    'regexp': match_regexp,
}
