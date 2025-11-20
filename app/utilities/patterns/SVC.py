from typing import Any
from .base import Base
from .utils import ROLE_TO_VAR, QUANTIFIER_RULE


class SVC(Base):
    """
    Класс для предложений структуры **Subject – Verb – Complement (SVC)**.
    Относится к простым категорическим утверждениям ("A is B", "A is adj").

    Примеры:
    - "Every student is smart."
    - "Some cats are cute."

    ### Структурные требования (match):
    1.  Наличие **nsubj** (субъекта).
    2.  Наличие **attr** (номинальный комплемент) или **acomp** (адъективный комплемент).
    3.  **Отсутствие** прямого объекта (**dobj**).

    ### Логическое преобразование (convert):
    Формула вида: `Qx ( Subject(x) RULE ¬Complement(x) )`,
    где отрицание (`¬`) вычисляется через XOR отрицаний квантора субъекта и глагола.
    """

    def match(self, doc: Any) -> bool:
        """
        Проверяет наличие субъекта и комплемента, а также отсутствие прямого объекта.
        """
        root = self.find_root(doc)
        if not root:
            return False

        subj = None
        complement = None

        for child in root.children:
            if child.dep_ == "nsubj":
                subj = child
            if child.dep_ in ("attr", "acomp"):
                complement = child

        # Проверка на отсутствие dobj (иначе это SVO)
        has_object = any(c.dep_ == "dobj" for c in root.children)

        return subj is not None and complement is not None and not has_object

    def convert(self, doc: Any) -> str:
        """
        Преобразует SVC-предложение в формулу логики первого порядка.
        """
        root = self.find_root(doc)

        subj_token = [c for c in root.children if c.dep_ == "nsubj"][0]
        comp_token = [c for c in root.children if c.dep_ in ("acomp", "attr")][0]

        # 1. Субъект (noun, quantifier, is_neg?)
        subj_noun, subj_quant, subj_is_neg = self.extract_quantified_noun(subj_token)
        
        # 2. Глагол (is not?)
        verb_is_neg = self.is_negated(root)

        # 3. Итоговое отрицание (XOR)
        # "No student is lazy" -> True ^ False = True (Negate pred)
        # "Student is not lazy" -> False ^ True = True (Negate pred)
        # "No student is not lazy" -> True ^ True = False (Positive pred)
        final_negation = subj_is_neg ^ verb_is_neg
        neg_symbol = "¬" if final_negation else ""

        # Предикат комплемента
        comp_predicate = comp_token.lemma_.capitalize()

        var = ROLE_TO_VAR['nsubj']
        rule = QUANTIFIER_RULE[subj_quant]

        # Формируем: Qx (Subj(x) RULE ¬Comp(x))
        return f"{subj_quant}{var} ({subj_noun}({var}) {rule} {neg_symbol}{comp_predicate}({var}))"

    def __str__(self) -> str:
        """
        Возвращает строковое имя паттерна.
        """
        return "SVC"