from typing import Any
from .base import Base
from .utils import ROLE_TO_VAR, QUANTIFIER_RULE


class SVIODO(Base):
    """
    Класс для предложений структуры **Subject – Verb – Indirect Object – Direct Object (SVIODO)**.
    Описывает дитранзитивные (двупереходные) глаголы, требующие двух дополнений: 
    кому? (Recipient) и что? (Theme).

    Примеры:
    - "The teacher gave the student a book."
    - "She sends him a letter."

    ### Структурные требования (match):
    1.  Наличие **nsubj** (субъекта).
    2.  Наличие **dobj** (прямого дополнения — "что").
    3.  Наличие **iobj** или **dative** (косвенного дополнения — "кому").
        *Примечание: SpaCy может использовать `dative` для косвенного дополнения.*

    ### Логическое преобразование (convert):
    Формула с тройной вложенностью:
    `Q1x ( Subject(x) R1 Q2y ( IObj(y) R2 Q3z ( DObj(z) R3 Predicate(x, y, z) ) ) )`
    
    Особенности:
    - Отрицание (`¬`) вычисляется как XOR четырех компонентов: субъекта, глагола, IO и DO.
    - Переменные: Subj -> x, IO -> y, DO -> z.
    """

    def match(self, doc: Any) -> bool:
        """
        Проверяет наличие субъекта, прямого дополнения и косвенного дополнения.
        """
        root = self.find_root(doc)
        if not root:
            return False

        has_subj = False
        has_dobj = False
        has_iobj = False

        for child in root.children:
            if child.dep_ == "nsubj":
                has_subj = True
            if child.dep_ == "dobj":
                has_dobj = True
            # Проверяем оба варианта тегов для косвенного дополнения
            if child.dep_ in ("iobj", "dative"):
                has_iobj = True
            # Вариант 2: Предлог to/for (gave a book to her)
            elif child.dep_ == "prep" and child.lemma_ in ("to", "for"):
                has_iobj = True

        return has_subj and has_dobj and has_iobj

    def convert(self, doc: Any) -> str:
        """
        Преобразует SVIODO-предложение в формулу логики предикатов.
        """
        root = self.find_root(doc)
        if not root:
            return ""

        # Поиск токенов
        subj_token = None
        dobj_token = None
        iobj_token = None

        for child in root.children:
            if child.dep_ == "nsubj":
                subj_token = child
            elif child.dep_ == "dobj":
                dobj_token = child
            elif child.dep_ in ("iobj", "dative"):
                iobj_token = child
            elif child.dep_ == "prep" and child.lemma_ in ("to", "for"):
                iobj_token = child

        if not (subj_token and dobj_token and iobj_token):
            return ""

        # 1. Извлечение данных (существительное, квантор, отрицание) для всех частей
        subj_noun, subj_quant, s_neg = self.extract_quantified_noun(subj_token)
        iobj_noun, iobj_quant, io_neg = self.extract_quantified_noun(iobj_token)
        dobj_noun, dobj_quant, do_neg = self.extract_quantified_noun(dobj_token)

        # 2. Отрицание глагола
        v_neg = self.is_negated(root)

        # 3. Итоговое отрицание (4-way XOR)
        # ¬(S ^ V ^ IO ^ DO)
        final_neg = s_neg ^ v_neg ^ io_neg ^ do_neg
        neg_symbol = "¬" if final_neg else ""

        # 4. Переменные
        # Используем get с fallback, чтобы гарантировать уникальность, если ROLE_TO_VAR не настроен
        xv = ROLE_TO_VAR.get('nsubj', 'x')
        yv = ROLE_TO_VAR.get('iobj', 'y') 
        zv = ROLE_TO_VAR.get('dobj', 'z')

        # 5. Правила соединения (импликация для ∀, конъюнкция для ∃)
        subj_rule = QUANTIFIER_RULE.get(subj_quant, "∧")
        iobj_rule = QUANTIFIER_RULE.get(iobj_quant, "∧")
        dobj_rule = QUANTIFIER_RULE.get(dobj_quant, "∧")

        # 6. Предикат
        pred_name = root.lemma_.capitalize()
        
        # 7. Сборка формулы (от внутреннего к внешнему)
        
        # Атом: ¬Give(x, y, z)
        # Обратите внимание на порядок аргументов: (Agent, Recipient, Theme) -> (x, y, z)
        atom = f"{neg_symbol}{pred_name}({xv}, {yv}, {zv})"

        # Уровень 1: Прямое дополнение (Theme)
        # Qz z ( Book(z) rule Atom )
        dobj_formula = f"{dobj_quant}{zv} ({dobj_noun}({zv}) {dobj_rule} {atom})"

        # Уровень 2: Косвенное дополнение (Recipient)
        # Qy y ( Student(y) rule dobj_formula )
        iobj_formula = f"{iobj_quant}{yv} ({iobj_noun}({yv}) {iobj_rule} {dobj_formula})"

        # Уровень 3: Субъект (Agent)
        # Qx x ( Teacher(x) rule iobj_formula )
        final_formula = f"{subj_quant}{xv} ({subj_noun}({xv}) {subj_rule} {iobj_formula})"

        return final_formula

    def __str__(self) -> str:
        """
        Возвращает строковое имя паттерна.
        """
        return "SVIODO"