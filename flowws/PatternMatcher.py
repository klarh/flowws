
identity = lambda x: x

class MatchError(Exception):
    def __init__(self, pattern, value):
        self.pattern = pattern
        self.value = value

    def __repr__(self):
        return 'MatchError(pattern={}, value={})'.format(pattern, value)

class PatternMatcher:
    MATCH_FUNCTIONS = {}

    @classmethod
    def register(cls, key_type):
        def result(function):
            PatternMatcher.MATCH_FUNCTIONS[key_type] = function
            return function
        return result

    @classmethod
    def match(cls, pattern, value):
        if pattern is eval:
            if isinstance(value, str):
                return eval(value)
            return value
        elif callable(pattern):
            try:
                result = pattern(value)
                return result
            except:
                raise MatchError(pattern, value)
        elif pattern == value:
            return result

        handler = cls.MATCH_FUNCTIONS.get(type(pattern), None)
        if handler is None:
            raise MatchError(pattern, value)

        return handler(pattern, value)

@PatternMatcher.register(list)
def match_list(pattern, value):
    if len(pattern) == 0:
        return list(value)

    assert len(pattern) == 1, 'only zero- or single-element homogeneous list patterns are currently supported'

    elt_type = pattern[0]
    return [match(elt_type, val) for val in value]

@PatternMatcher.register(tuple)
def match_tuple(pattern, value):
    if len(pattern) == 0:
        return tuple(value)

    if len(pattern) != len(value):
        raise MatchError(pattern, value)

    result = []
    for (p, v) in zip(pattern, value):
        result.append(match(p, v))

    return tuple(result)

@PatternMatcher.register(dict)
def match_dict(pattern, value):
    if len(pattern) == 0:
        return dict(value)

    assert len(pattern) <= 1, 'only zero- or single-element dict patterns are currently supported'

    for (key_type, val_type) in pattern.items():
        pass

    result = {}
    for key in value:
        result[match(key_type, key)] = match(val_type, value[key])

    return result

match = PatternMatcher.match
