from .base import Base
from .utils import ROLE_TO_VAR, QUANTIFIER_RULE


class SV(Base):
    """
    Класс для предложений структуры SV:
    Subject – Verb (простое предложение с субъектом и сказуемым).

    Примеры предложений:
    ----------------------
    - "A student sleeps."
    - "Every dog barks."
    - "Birds fly."
    - "Some people laugh."

    Структурные признаки:
    ----------------------
    ROOT  — глагол
      └── nsubj — субъект (обязателен)

    И при этом:
      - нет прямого объекта (dobj)
      - нет комплемента (attr, acomp)
      - нет xcomp / ccomp
      → иначе это SVO или SVC

    Логическое преобразование:
    ---------------------------
    Формула вида:

        Qx ( Subject(x) RULE Predicate(x) )

    Где:
      - Predicate(x) — глагол с субъектом
      - RULE:
            ∀ → →
            ∃ → ∧

    Примеры преобразований:
    ------------------------
    1) "A student sleeps."
       → ∃x (Student(x) ∧ Sleep(x))

    2) "Every dog barks."
       → ∀x (Dog(x) → Bark(x))

    3) "A student runs."
       → ∃x (Student(x) ∧ Run(x))

    Логика match():
    ----------------
    match(doc) возвращает True, если:
      - есть субъект (nsubj)
      - нет dobj/iobj/pobj
      - нет комплемента attr/acomp/xcomp/ccomp

    Ошибки:
    -------
    - если предложение не попало под SV и не совпало с другими структурами

    Возвращаемая строка:
    ---------------------
    Формула логики предикатов в виде ∀x(...) или ∃x(...).
    """

    def match(self, doc):
        root = self.find_root(doc)
        if not root:
            return False

        subj = None
        has_object = False
        has_complement = False

        for child in root.children:

            # субъект обязателен
            if child.dep_ == "nsubj":
                subj = child

            # если есть объект — это уже не SV
            if child.dep_ in ("dobj", "iobj", "pobj"):
                has_object = True

            # если есть комплемент — это не SV
            if child.dep_ in ("attr", "acomp", "xcomp", "ccomp"):
                has_complement = True

        # SV только если:
        return subj is not None and not has_object and not has_complement

    def convert(self, doc):
        root = self.find_root(doc)
        subj_token = [c for c in root.children if c.dep_ == "nsubj"][0]

        subj_noun, subj_quant = self.extract_quantified_noun(subj_token)
        if not subj_quant:
            return "[Ошибка] У субъекта нет явного квантора."

        var = ROLE_TO_VAR['nsubj']
        predicate = root.lemma_.capitalize()

        rule = QUANTIFIER_RULE[subj_quant]

        return f"{subj_quant}{var} ({subj_noun}({var}) {rule} {predicate}({var}))"

    def __str__(self):
        return "SV"
