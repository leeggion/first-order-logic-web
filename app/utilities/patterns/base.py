class Base:
    """
    Базовый класс для всех паттернов предложения.
    Каждый паттерн должен уметь:
    - match(doc) — является ли предложение данным типом
    - convert(doc) — преобразовать в FOL
    """

    def match(self, doc):
        raise NotImplementedError

    def convert(self, doc):
        raise NotImplementedError

    # вспомогательные методы
    def find_root(self, doc):
        for token in doc:
            if token.dep_ == 'ROOT':
                return token
        return None

    def extract_quantified_noun(self, token):
        # noun name
        noun = token.lemma_.capitalize()

        # quantifier
        quantifier = None
        for child in token.children:
            if child.dep_ == "det":
                from .utils import QUANTIFIER_MAP
                quantifier = QUANTIFIER_MAP.get(child.lemma_)
                break

        return noun, quantifier
