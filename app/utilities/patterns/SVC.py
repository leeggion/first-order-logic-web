from .base import Base
from .utils import ROLE_TO_VAR, QUANTIFIER_RULE


class SVC(Base):
    """
    Класс для предложений структуры SVC:
    Subject – Verb – Complement (субъект – глагол-связка – комплемент).

    Обычно это именная связка ("be") или прилагательное в роли именной части сказуемого.

    Примеры предложений:
    ----------------------
    - "Every student is smart."
    - "Some cats are cute."
    - "Professors are tired."
    - "The sky is blue."

    Синтаксические признаки:
    -------------------------
    ROOT  — глагол (обычно 'be')
      ├── nsubj — субъект (обязателен)
      └── attr / acomp — комплемент субъекта (обязателен)

    Важно:
    -------
    Если есть dobj → это уже SVO, а не SVC.
    Поэтому match() дополнительно проверяет отсутствие прямого объекта.

    Логическое преобразование:
    ---------------------------
    Qx ( Subject(x) RULE  Complement(x) )

    Где:
      - Complement(x) — предикат, порождённый комплементом (например "smart" → Smart(x))
      - RULE:
            ∀ → →
            ∃ → ∧

    Примеры преобразований:
    ------------------------
    1) "Every student is smart."
       → ∀x (Student(x) → Smart(x))

    2) "Some cats are cute."
       → ∃x (Cat(x) ∧ Cute(x))

    3) "Every cat is animal."
       → ∀x (Cat(x) → Animal(x))

    Ограничения:
    -------------
    - работает только с простыми copula-предложениями ("A is B", "A is adj")
    - не поддерживает сложные комплементы, например xcomp/ccomp (всякие гигадополнения не пройдут)

    Ошибки:
    -------
    - если нет субъекта или комплемента
    - если встречается объект dobj (значит это уже SVO)

    Возвращаемая строка:
    ---------------------
    Формула FOL вида ∀x(...) или ∃x(...).
    """

    def match(self, doc):
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

        # Не должно быть dobj, чтобы не путать с SVO
        has_object = any(c.dep_ == "dobj" for c in root.children)

        return subj is not None and complement is not None and not has_object

    def convert(self, doc):
        root = self.find_root(doc)

        subj = [c for c in root.children if c.dep_ == "nsubj"][0]
        comp = [c for c in root.children if c.dep_ in ("acomp", "attr")][0]

        # subject: Every student
        subj_noun, subj_quant = self.extract_quantified_noun(subj)
        if not subj_quant:
            return "[Ошибка] У субъекта нет явного квантора."

        # complement: smart → Smart(x)
        comp_predicate = comp.lemma_.capitalize()

        var = ROLE_TO_VAR['nsubj']
        rule = QUANTIFIER_RULE[subj_quant]

        return f"{subj_quant}{var} ({subj_noun}({var}) {rule} {comp_predicate}({var}))"

    def __str__(self):
        return "SVC"
