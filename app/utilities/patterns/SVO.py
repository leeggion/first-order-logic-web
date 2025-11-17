from .base import Base
from .utils import ROLE_TO_VAR, QUANTIFIER_RULE


class SVO(Base):
    """
    Класс для преобразования предложений структуры SVO:
    Subject – Verb – Object (субъект – глагол – прямое дополнение).

    Примеры предложений:
    ----------------------
    - "Some professor teaches a course."
    - "Every student reads a book."
    - "Teachers help students."

    Требуемая синтаксическая структура:
    -----------------------------------
    ROOT  — глагол (основной предикат)
      ├── nsubj — субъект действия (обязателен)
      └── dobj  — объект действия (обязателен)

    Логическое преобразование:
    ---------------------------
    Формула имеет вид:

        Qₛ x ( Subject(x) RULEₛ   Qₒ y ( Object(y) RULEₒ  Predicate(x, y) ) )

    Где:
      - Qₛ, Qₒ — кванторы (∀ или ∃)
      - RULEₛ, RULEₒ — логические связки:
            ∀ → →
            ∃ → ∧
      - Predicate(x, y) — действие, представленное глаголом

    Примеры преобразования:
    ------------------------
    1) "Some professor teaches a course."
       → ∃x (Professor(x) ∧ ∃y (Course(y) ∧ Teach(x, y)))

    2) "Every student reads a book."
       → ∀x (Student(x) → ∃y (Book(y) ∧ Read(x, y)))

    3) "All teachers help each student."
       → ∀x (Teacher(x) → ∀y (Student(y) → Help(x, y)))

    Проверка соответствия структуре:
    ---------------------------------
    Метод match(doc) возвращает True, если:
      - найден субъект (nsubj)
      - найден прямой объект (dobj)

    Ошибки:
    -------
    - если субъект или объект не имеют определителя и требуется квантор
    - если структура не соответствует SVO — класс не используется

    Возвращаемая строка:
    ---------------------
    Корректная формула логики предикатов (FOL)
    """

    def match(self, doc):
        root = self.find_root(doc)
        if not root:
            return False

        subj = None
        obj = None

        for child in root.children:
            if child.dep_ == "nsubj":
                subj = child
            if child.dep_ == "dobj":
                obj = child

        return subj is not None and obj is not None

    def convert(self, doc):
        root = self.find_root(doc)

        subj = [c for c in root.children if c.dep_ == "nsubj"][0]
        obj = [c for c in root.children if c.dep_ == "dobj"][0]

        subj_noun, subj_quant = self.extract_quantified_noun(subj)
        obj_noun,  obj_quant = self.extract_quantified_noun(obj)

        if not subj_quant or not obj_quant:
            return "[Ошибка] Нужны явные кванторы у субъекта и объекта."

        pred = root.lemma_.capitalize()

        xv = ROLE_TO_VAR['nsubj']
        yv = ROLE_TO_VAR['dobj']

        obj_rule = QUANTIFIER_RULE[obj_quant]
        subj_rule = QUANTIFIER_RULE[subj_quant]

        atom = f"{pred}({xv}, {yv})"

        object_formula = f"{obj_quant}{yv} ({obj_noun}({yv}) {obj_rule} {atom})"

        return f"{subj_quant}{xv} ({subj_noun}({xv}) {subj_rule} {object_formula})"

    def __str__(self):
        return "SVO"
