'''
Вспомогательные словари
'''

QUANTIFIER_MAP = {
    'all': '∀',
    'every': '∀',
    'each': '∀',
    'a': '∃',
    'an': '∃',
    'some': '∃',
    'exists': '∃'
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
