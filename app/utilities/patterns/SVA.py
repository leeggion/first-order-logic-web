from typing import Any, Optional
from .base import Base
from .utils import ROLE_TO_VAR, QUANTIFIER_RULE


class SVA(Base):
    """
    Класс для предложений структуры **Subject – Verb – Adverbial (SVA)**.
    Обрабатывает предложения, где действие описывается обстоятельством места, 
    времени или образа действия (включая предложные группы).

    Примеры:
    - "Dogs run quickly." (advmod)
    - "John walks to school." (prep + pobj)
    - "Every student sits in the classroom."

    ### Структурные требования (match):
    1.  Наличие **nsubj** (субъекта).
    2.  Наличие обстоятельства, выраженного через:
        - **advmod** (наречие: *quickly*),
        - **obl** (косвенное дополнение/обстоятельство),
        - **npadvmod** (именная группа как обстоятельство),
        - **prep** (предлог, ведущий к **pobj**).

    ### Логическое преобразование (convert):
    Формула вложенная, так как обстоятельство рассматривается как второй предикат:
    `Q1x ( Subject(x) RULE1 Q2y ( Adverb(y) RULE2 Predicate(x, y) ) )`
    
    Особенности:
    - Если у обстоятельства нет своего квантора (детерминанта), оно **наследует** квантор субъекта.
    - Отрицание (`¬`) вычисляется как XOR трех компонентов: субъекта, глагола и обстоятельства.
    """

    def match(self, doc: Any) -> bool:
        """
        Проверяет наличие субъекта и хотя бы одного типа обстоятельства (advmod, obl, npadvmod, prep).
        """
        root = self.find_root(doc)
        if not root:
            return False

        has_subj = False
        has_adv = False

        for child in root.children:
            if child.dep_ == "nsubj":
                has_subj = True
            # расширяем список зависимостей — учитываем prepositional phrases
            if child.dep_ in ("advmod", "obl", "npadvmod", "prep"):
                has_adv = True

        return has_subj and has_adv

    def _get_adv_token(self, root_token: Any) -> Optional[Any]:
        """
        Вспомогательный метод: возвращает токен, несущий основной смысл обстоятельства.
        
        Логика поиска:
        1. Ищем прямые `advmod`, `obl`, `npadvmod`.
        2. Если найден `prep`, пытаемся найти его `pobj` (объект предлога).
           Например, в "to school": root->to(prep)->school(pobj). Вернем "school".
        """
        adv = None
        for child in root_token.children:
            if child.dep_ in ("advmod", "obl", "npadvmod"):
                return child
            if child.dep_ == "prep" and adv is None:
                # запомним prep на случай, если нет advmod/obl
                adv = child

        if adv is not None:
            # попробуем получить pobj
            for c in adv.children:
                if c.dep_ == "pobj":
                    return c
            # если pobj не найден, вернём сам prep (на всякий случай)
            return adv

        return None

    def convert(self, doc: Any) -> str:
        """
        Преобразует SVA-предложение в формулу с вложенной квантификацией.
        """
        root = self.find_root(doc)
        if not root:
            return ""

        # subj token
        subj_tokens = [c for c in root.children if c.dep_ == "nsubj"]
        if not subj_tokens:
            return ""
        subj_token = subj_tokens[0]

        # adv token (учитываем prep->pobj)
        adv_token = self._get_adv_token(root)
        if adv_token is None:
            return ""

        # 1. Извлечение данных для субъекта
        subj_noun, subj_quant, subj_is_neg = self.extract_quantified_noun(subj_token)

        # 2. Извлечение данных для обстоятельства
        # если обстоятельство — предлог (prep), _get_adv_token уже вернул pobj или prep.
        adv_noun, adv_quant, adv_is_neg = self.extract_quantified_noun(adv_token)

        # print(adv_noun, adv_quant, adv_is_neg)
        # 3. Если у обстоятельства нет явного квантора (det), мы хотим по умолчанию
        # наследовать квантор субъекта (чтобы "Dogs run quickly" -> adv_quant = ∀)
        # Мы считаем, что extract_quantified_noun возвращает is_quant_neg = False если det не найден.
        # Поэтому проверим adv_token на наличие детерминанта (дети с dep_ == 'det').
        has_adv_det = any(c.dep_ == "det" for c in adv_token.children)
        if not has_adv_det:
            # наследуем квантор субъекта (так соответствует ожидаемым тестам)
            adv_quant = subj_quant

        # 4. Отрицание глагола
        verb_is_neg = self.is_negated(root)

        # 5. Общая логика отрицаний (xor)
        final_neg = subj_is_neg ^ verb_is_neg ^ adv_is_neg
        neg_symbol = "¬" if final_neg else ""

        # 6. Переменные
        xv = ROLE_TO_VAR.get('nsubj', 'x')
        yv = ROLE_TO_VAR.get('advmod', ROLE_TO_VAR.get('dobj', 'y'))

        # 7. Правила соединения (используем QUANTIFIER_RULE для adv,
        #   и правило между Subject и вложенной формулой — как в других частях)
        subj_rule = "→" if subj_quant == "∀" else "∧"
        adv_rule = QUANTIFIER_RULE.get(adv_quant, "→")

        # 8. Предикат (лемма глагола, с заглавной буквы)
        pred_name = root.lemma_.capitalize()

        # 9. Формирование атома: например "¬Run(x, y)"
        atom = f"{neg_symbol}{pred_name}({xv}, {yv})"

        # 10. Вложенная формула для обстоятельства
        object_formula = f"{adv_quant}{yv} ({adv_noun}({yv}) {adv_rule} {atom})"

        # 11. Финальная формула
        return f"{subj_quant}{xv} ({subj_noun}({xv}) {subj_rule} {object_formula})"

    def __str__(self) -> str:
        """
        Возвращает строковое имя паттерна.
        """
        return "SVA"
