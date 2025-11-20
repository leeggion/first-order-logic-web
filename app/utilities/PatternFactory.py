from utilities.patterns import PATTERNS


class PatternFactory:
    def __init__(self):
        self.patterns = PATTERNS

    def get_pattern(self, doc):
        for pattern in self.patterns:
            if pattern.match(doc):
                return pattern
        return None
