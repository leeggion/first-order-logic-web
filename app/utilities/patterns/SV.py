from typing import Any
from .base import Base
from .utils import ROLE_TO_VAR, QUANTIFIER_RULE


class SV(Base):
    """
    Класс для предложений структуры **Subject – Verb (SV)**.
    Относится к простым непереходным предложениям (не имеющим объектов/комплементов).

    Примеры:
    - "Every dog barks."
    - "A student sleeps."

    ### Структурные требования (match):
    1.  Наличие **nsubj** (субъекта).
    2.  **Отсутствие** любых видов объектов (**dobj**, **iobj**, **pobj**).
    3.  **Отсутствие** любых видов комплементов (**attr**, **acomp**, **xcomp**, **ccomp**).

    ### Логическое преобразование (convert):
    Формула вида: `Qx ( Subject(x) RULE ¬Predicate(x) )`,
    где **Predicate** — лемма глагола (`ROOT`), а отрицание (`¬`) вычисляется
    через XOR отрицаний квантора субъекта и глагола.
    """

    def match(self, doc: Any) -> bool:
        """
        Проверяет наличие субъекта и отсутствие всех видов объектов и комплементов.
        """
        root = self.find_root(doc)
        if not root:
            return False

        subj = None
        has_object = False
        has_complement = False

        for child in root.children:
            if child.dep_ == "nsubj":
                subj = child
            
            # Важно: "neg" не ломает структуру SV, поэтому мы его игнорируем в проверках "has_..."
            if child.dep_ in ("dobj", "iobj", "pobj"):
                has_object = True
            if child.dep_ in ("attr", "acomp", "xcomp", "ccomp"):
                has_complement = True

        return subj is not None and not has_object and not has_complement

    def convert(self, doc: Any) -> str:
        """
        Преобразует SV-предложение в формулу логики первого порядка.
        """
        root = self.find_root(doc)
        subj_token = [c for c in root.children if c.dep_ == "nsubj"][0]

        # 1. Извлекаем данные субъекта с учетом "No"
        subj_noun, subj_quant, is_quant_neg = self.extract_quantified_noun(subj_token)
        
        # 2. Проверяем отрицание глагола (does NOT run)
        is_verb_neg = self.is_negated(root)

        # 3. Определяем итоговое отрицание предиката
        # Если "No student" (True) ... "sleeps" (False) -> Negate predicate
        # Если "A student" (False) ... "does not sleep" (True) -> Negate predicate
        # Если "No student" (True) ... "does not sleep" (True) -> Positive predicate (Double neg)
        final_negation = is_quant_neg ^ is_verb_neg  # XOR
        
        neg_symbol = "¬" if final_negation else ""

        # 4. Формируем переменные
        var = ROLE_TO_VAR['nsubj']
        predicate = root.lemma_.capitalize()
        rule = QUANTIFIER_RULE[subj_quant]

        # 5. Сборка формулы
        # Пример: ∀x (Student(x) → ¬Sleep(x))
        return f"{subj_quant}{var} ({subj_noun}({var}) {rule} {neg_symbol}{predicate}({var}))"

    def __str__(self) -> str:
        """
        Возвращает строковое имя паттерна.
        """
        return "SV"