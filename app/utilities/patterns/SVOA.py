from typing import Any, Optional
from .base import Base
from .utils import ROLE_TO_VAR, QUANTIFIER_RULE


class SVOA(Base):
    """
    Класс для предложений структуры **Subject – Verb – Object – Adverbial (SVOA)**.
    
    Примеры:
    - "John ate an apple quickly." (advmod)
    - "A student reads a book in the library." (prep + pobj)
    - "Robots build cars efficiently."

    ### Структурные требования (match):
    1.  Наличие **nsubj** (субъекта).
    2.  Наличие **dobj** (прямого объекта).
    3.  Наличие обстоятельства (**advmod**, **obl**, **prep**, **npadvmod**).

    ### Логическое преобразование (convert):
    Формула с тройной вложенностью:
    `Q1x ( Subject(x) RULE1 Q2y ( Object(y) RULE2 Q3z ( Adverb(z) RULE3 Predicate(x, y, z) ) ) )`
    
    Где:
    - x: Субъект
    - y: Объект
    - z: Обстоятельство
    - Отрицание (¬) вычисляется как XOR(subj, verb, obj, adv).
    """

    def match(self, doc: Any) -> bool:
        """
        Проверяет наличие субъекта, объекта и обстоятельства.
        """
        root = self.find_root(doc)
        if not root:
            return False

        has_subj = False
        has_obj = False
        has_adv = False

        # Список зависимостей, считающихся обстоятельствами
        adv_deps = {"advmod", "obl", "npadvmod", "prep"}

        for child in root.children:
            if child.dep_ == "nsubj":
                has_subj = True
            if child.dep_ == "dobj":
                has_obj = True
            if child.dep_ in adv_deps:
                has_adv = True

        return has_subj and has_obj and has_adv

    def _get_semantic_head(self, token: Any) -> Any:
        """
        Вспомогательный метод для извлечения ядра обстоятельства.
        Если это предлог (prep), возвращаем pobj.
        """
        if token.dep_ == "prep":
            for child in token.children:
                if child.dep_ == "pobj":
                    return child
            return token
        return token

    def convert(self, doc: Any) -> str:
        """
        Преобразует SVOA-предложение в логическую формулу.
        """
        root = self.find_root(doc)
        
        # 1. Поиск токенов
        subj_token = [c for c in root.children if c.dep_ == "nsubj"][0]
        obj_token = [c for c in root.children if c.dep_ == "dobj"][0]
        
        # Ищем первое подходящее обстоятельство
        adv_deps = {"advmod", "obl", "npadvmod", "prep"}
        adv_raw = [c for c in root.children if c.dep_ in adv_deps][0]
        adv_token = self._get_semantic_head(adv_raw)

        # 2. Извлечение атрибутов (Noun, Quantifier, Negation)
        
        # Субъект
        subj_noun, subj_quant, subj_neg = self.extract_quantified_noun(subj_token)
        
        # Объект
        obj_noun, obj_quant, obj_neg = self.extract_quantified_noun(obj_token)
        
        # Обстоятельство
        adv_noun, adv_quant, adv_neg = self.extract_quantified_noun(adv_token)
        
        # Наследование квантора для обстоятельства (если нет своего детерминанта)
        # Обычно наследуем от Субъекта
        if not any(c.dep_ == "det" for c in adv_token.children):
            adv_quant = subj_quant

        # 3. Отрицание глагола
        verb_neg = self.is_negated(root)

        # 4. Итоговое отрицание (XOR четырех компонентов)
        final_neg = subj_neg ^ verb_neg ^ obj_neg ^ adv_neg
        neg_symbol = "¬" if final_neg else ""

        # 5. Переменные
        xv = ROLE_TO_VAR.get('nsubj', 'x')
        yv = ROLE_TO_VAR.get('dobj', 'y')
        zv = 'z' # Используем z для третьего аргумента

        # 6. Правила соединения
        subj_rule = QUANTIFIER_RULE[subj_quant]
        obj_rule = QUANTIFIER_RULE[obj_quant]
        adv_rule = QUANTIFIER_RULE[adv_quant]

        pred_name = root.lemma_.capitalize()

        # 7. Сборка формулы (изнутри наружу)

        # Атом: ¬Eat(x, y, z)
        atom = f"{neg_symbol}{pred_name}({xv}, {yv}, {zv})"

        # Уровень 3: Обстоятельство (z) -> Атом
        level3 = f"{adv_quant}{zv} ({adv_noun}({zv}) {adv_rule} {atom})"

        # Уровень 2: Объект (y) -> Уровень 3
        level2 = f"{obj_quant}{yv} ({obj_noun}({yv}) {obj_rule} {level3})"

        # Уровень 1: Субъект (x) -> Уровень 2
        final_formula = f"{subj_quant}{xv} ({subj_noun}({xv}) {subj_rule} {level2})"

        return final_formula

    def __str__(self) -> str:
        return "SVOA"