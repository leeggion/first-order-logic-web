'''
Вспомогательные словари
'''

QUANTIFIER_MAP = {
    'all': '∀',
    'every': '∀',
    'each': '∀',
    'no': '∀',      # Special case: Universal + Negation
    'none': '∀',    # Special case
    'a': '∃',
    'an': '∃',
    'some': '∃',
    'exists': '∃',
    'the': '∃'      # Обычно конкретный объект, упростим до существования
}

QUANTIFIER_RULE = {
    '∀': '→',
    '∃': '∧'
}

ROLE_TO_VAR = {
    'nsubj': 'x',
    'dobj': 'y',
    'attr': 'z'
}