from re import match as re_match

def match_regexp(transition, event, _token, _fsa):
    return re_match('^%s$' % transition['condition'], event)

DIRECTORY = {
    'regexp': match_regexp,
}
