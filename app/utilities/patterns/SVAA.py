from typing import Any, List, Optional
from .base import Base
from .utils import ROLE_TO_VAR, QUANTIFIER_RULE


class SVAA(Base):
    """
    Класс для предложений структуры **Subject – Verb – Adverbial – Adverbial (SVAA)**.
    Обрабатывает предложения, где действие описывается ДВУМЯ обстоятельствами.

    Примеры:
    - "Dogs run quickly in the park." (advmod + prep)
    - "John walks to school at 5pm." (prep + prep)
    - "Every student sits quietly in the classroom."

    ### Структурные требования (match):
    1.  Наличие **nsubj** (субъекта).
    2.  Наличие **минимум двух** обстоятельств среди детей корня.
        Типы обстоятельств: **advmod**, **obl**, **npadvmod**, **prep**.

    ### Логическое преобразование (convert):
    Формула с двойным вложением:
    `Q1x ( Subject(x) RULE1 Q2y ( Adv1(y) RULE2 Q3z ( Adv2(z) RULE3 Predicate(x, y, z) ) ) )`

    Особенности:
    - Переменные: x (Subj), y (Adv1), z (Adv2).
    - Если у обстоятельства нет квантора, оно наследует квантор субъекта.
    - Отрицание вычисляется как XOR(subj, verb, adv1, adv2).
    """

    def _is_adv(self, token: Any) -> bool:
        """Проверяет, является ли токен обстоятельством."""
        # acomp и xcomp добавлены, так как иногда adjective complement выступает в роли "как?"
        return token.dep_ in {"advmod", "obl", "npadvmod", "prep", "acomp", "xcomp"}

    def _collect_adverbs(self, root: Any) -> List[Any]:
        """
        Собирает список всех обстоятельств, связанных с глаголом,
        включая вложенные (works -> together -> well).
        """
        advs = []
        # 1. Проходим по прямым детям
        for child in root.children:
            if self._is_adv(child):
                advs.append(child)
                
                # 2. Если ребенок - обстоятельство, проверяем его детей (внуков корня)
                # Это решает проблему "well -> together"
                for grandchild in child.children:
                    if self._is_adv(grandchild):
                        advs.append(grandchild)
        return advs

    def match(self, doc: Any) -> bool:
        root = self.find_root(doc)
        if not root:
            return False

        subj = None
        for child in root.children:
            if child.dep_ == "nsubj":
                subj = child
        
        # Собираем все обстоятельства (прямые и вложенные)
        all_advs = self._collect_adverbs(root)

        # Нужно минимум 2 обстоятельства
        return subj is not None and len(all_advs) >= 2

    def _get_semantic_head(self, token: Any) -> Any:
        """
        Если токен - предлог (in), возвращаем сущ (park).
        """
        if token.dep_ == "prep":
            for child in token.children:
                if child.dep_ == "pobj":
                    return child
            return token
        return token

    def convert(self, doc: Any) -> str:
        root = self.find_root(doc)
        
        # 1. Субъект
        subj_token = [c for c in root.children if c.dep_ == "nsubj"][0]

        # 2. Обстоятельства
        # Используем ту же логику сбора, что и в match
        all_advs_raw = self._collect_adverbs(root)
        
        # Берем первые два найденных (если их больше, остальные игнорируем для SVAA)
        adv1_raw = all_advs_raw[0]
        adv2_raw = all_advs_raw[1]

        adv1_token = self._get_semantic_head(adv1_raw)
        adv2_token = self._get_semantic_head(adv2_raw)

        # 3. Извлечение параметров
        subj_noun, subj_quant, subj_neg = self.extract_quantified_noun(subj_token)
        
        adv1_noun, adv1_quant, adv1_neg = self.extract_quantified_noun(adv1_token)
        if not any(c.dep_ == "det" for c in adv1_token.children):
            adv1_quant = subj_quant

        adv2_noun, adv2_quant, adv2_neg = self.extract_quantified_noun(adv2_token)
        if not any(c.dep_ == "det" for c in adv2_token.children):
            adv2_quant = subj_quant

        # 4. Логика отрицания
        verb_neg = self.is_negated(root)
        final_neg = subj_neg ^ verb_neg ^ adv1_neg ^ adv2_neg
        neg_symbol = "¬" if final_neg else ""

        # 5. Переменные
        xv = "x"
        yv = "y"
        zv = "z"

        subj_rule = QUANTIFIER_RULE[subj_quant]
        adv1_rule = QUANTIFIER_RULE[adv1_quant]
        adv2_rule = QUANTIFIER_RULE[adv2_quant]

        pred_name = root.lemma_.capitalize()

        # 6. Сборка формулы
        atom = f"{neg_symbol}{pred_name}({xv}, {yv}, {zv})"
        
        # Порядок вложенности: Adv2 -> Adv1 -> Subj
        # (Порядок y и z не критичен для логики, но мы сохраняем структуру)
        level3 = f"{adv2_quant}{zv} ({adv2_noun}({zv}) {adv2_rule} {atom})"
        level2 = f"{adv1_quant}{yv} ({adv1_noun}({yv}) {adv1_rule} {level3})"
        final_formula = f"{subj_quant}{xv} ({subj_noun}({xv}) {subj_rule} {level2})"

        return final_formula

    def __str__(self) -> str:
        return "SVAA"