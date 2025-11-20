from typing import Optional, Tuple, Any
from .base import Base
from .utils import ROLE_TO_VAR, QUANTIFIER_RULE

# Предполагается, что doc - это объект spacy.tokens.Doc или Span
# Для типизации используем Any или импортируем spacy.tokens
class SVO(Base):
    """
    Обработчик предложений со структурой «Субъект — Глагол — Объект» (SVO).

    Этот класс наследуется от Base и реализует логику выявления (match)
    и преобразования (convert) простых предложений, содержащих подлежащее (nsubj),
    сказуемое (ROOT) и прямое дополнение (dobj), в формулы логики первого порядка.
    """
    
    def match(self, doc: Any) -> bool:
        """
        Проверяет, соответствует ли переданный документ паттерну SVO.

        Метод ищет корневой токен (глагол) и проверяет наличие у него
        двух обязательных зависимых элементов:
        1. nsubj (номинальный субъект).
        2. dobj (прямое дополнение).
        
        Args:
            doc: Обрабатываемый документ или спан (обычно spacy.tokens.Doc).

        Returns:
            bool: True, если структура соответствует SVO, иначе False.
        """
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

    def convert(self, doc: Any) -> str:
        """
        Преобразует документ SVO в строковое представление логической формулы.

        Алгоритм преобразования:
        1.  **Извлечение компонентов**: Находит подлежащее, сказуемое и дополнение.
        2.  **Анализ кванторов и свойств**: Для субъекта и объекта извлекаются
            существительное, квантор и признак отрицания.
        3.  **Обработка отрицания**: Вычисляется итоговое отрицание предиката
            с использованием операции XOR между отрицаниями субъекта, глагола и объекта.
            Это позволяет корректно обрабатывать двойные и тройные отрицания.
        4.  **Сборка формулы**: Формирует вложенную строку вида:
            `Q1 x ( Subject(x) RULE1 ( Q2 y ( Object(y) RULE2 Atom ) ) )`,
            где Atom — это предикат действия, например `¬Eat(x, y)`.

        Args:
            doc: Обрабатываемый документ (spacy.tokens.Doc).

        Returns:
            str: Строка, содержащая итоговую логическую формулу.
        """
        root = self.find_root(doc)

        subj_token = [c for c in root.children if c.dep_ == "nsubj"][0]
        obj_token = [c for c in root.children if c.dep_ == "dobj"][0]

        # 1. Извлекаем параметры Субъекта и Объекта
        # Метод extract_quantified_noun теперь возвращает 3 значения (включая флаг 'no')
        subj_noun, subj_quant, subj_is_neg = self.extract_quantified_noun(subj_token)
        obj_noun,  obj_quant,  obj_is_neg  = self.extract_quantified_noun(obj_token)

        # 2. Проверяем отрицание глагола
        verb_is_neg = self.is_negated(root)

        # 3. Вычисляем итоговое отрицание предиката (XOR трех значений)
        # True, если нечетное количество отрицаний
        final_negation = subj_is_neg ^ verb_is_neg ^ obj_is_neg
        neg_symbol = "¬" if final_negation else ""

        # 4. Собираем переменные и правило
        pred_name = root.lemma_.capitalize()
        
        xv = ROLE_TO_VAR['nsubj']
        yv = ROLE_TO_VAR['dobj']

        subj_rule = QUANTIFIER_RULE[subj_quant]
        obj_rule = QUANTIFIER_RULE[obj_quant]

        # 5. Формируем атом действия
        # Например: ¬Eat(x, y)
        atom = f"{neg_symbol}{pred_name}({xv}, {yv})"

        # 6. Вложенная формула объекта
        # Q2 y ( Object(y) RULE2 Atom )
        object_formula = f"{obj_quant}{yv} ({obj_noun}({yv}) {obj_rule} {atom})"

        # 7. Финальная формула
        # Q1 x ( Subject(x) RULE1 Object_Formula )
        return f"{subj_quant}{xv} ({subj_noun}({xv}) {subj_rule} {object_formula})"

    def __str__(self) -> str:
        """
        Возвращает строковое представление имени паттерна.

        Returns:
            str: Имя паттерна ("SVO").
        """
        return "SVO"