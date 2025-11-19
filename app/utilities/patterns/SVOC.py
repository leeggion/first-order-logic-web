from typing import Any, Tuple, Optional
from .base import Base
from .utils import ROLE_TO_VAR, QUANTIFIER_RULE


class SVOC(Base):
    """
    Класс для SVOC с "Эвристикой Детерминанта" для исправления ошибок sm-модели.
    """

    def _analyze_structure(self, root: Any) -> Tuple[Optional[Any], Optional[Any]]:
        dobj = None
        for child in root.children:
            if child.dep_ == "dobj":
                dobj = child
                break
        
        comp_deps = {"oprd", "xcomp", "ccomp", "acomp"}
        root_comps = [c for c in root.children if c.dep_ in comp_deps]

        # 1. Small Clause (нет dobj)
        if not dobj:
            for comp in root_comps:
                inner_subjs = [c for c in comp.children if c.dep_ == "nsubj"]
                if inner_subjs:
                    return inner_subjs[0], comp
            return None, None

        # 2. Анализ dobj на ошибки парсера
        # Кандидаты на роль "настоящего объекта" среди детей текущего dobj
        # Ищем существительные (frog), которые ошибочно подчинены слову green
        potential_real_objs = [c for c in dobj.children if c.pos_ in ("NOUN", "PROPN", "PRON")]

        # --- ЭВРИСТИКА 1: ADJ as Object ---
        # Если dobj - прилагательное, это точно ошибка.
        if dobj.pos_ == "ADJ":
            if potential_real_objs:
                return potential_real_objs[0], dobj # (Obj=Frog, Comp=Green)

        # --- ЭВРИСТИКА 2: Determiner Gap (для случаев, когда Green = NOUN) ---
        # Проверяем: у dobj НЕТ артикля, а у его ребенка ЕСТЬ артикль.
        # "turned [green]" (нет det) -> "frog" -> "the" (есть det)
        dobj_has_det = any(c.dep_ == "det" for c in dobj.children)
        
        if not dobj_has_det:
            for child in potential_real_objs:
                child_has_det = any(gc.dep_ == "det" for gc in child.children)
                if child_has_det:
                    # Нашли инверсию! Настоящий объект - child (frog)
                    return child, dobj

        # 3. Если dobj настоящий, ищем комплемент
        if root_comps:
            return dobj, root_comps[0]

        # 4. Post-nominal adjective (turned frog green)
        for child in dobj.children:
            if child.dep_ in ("amod", "acl") and child.i > dobj.i:
                return dobj, child

        return None, None

    def match(self, doc: Any) -> bool:
        root = self.find_root(doc)
        if not root: return False
        if not any(c.dep_ == "nsubj" for c in root.children): return False
        
        obj_t, comp_t = self._analyze_structure(root)
        return (obj_t is not None) and (comp_t is not None)

    def convert(self, doc: Any) -> str:
        root = self.find_root(doc)
        obj_token, comp_token = self._analyze_structure(root)
        subj_token = [c for c in root.children if c.dep_ == "nsubj"][0]

        if not obj_token or not comp_token:
            return "Error: SVOC mismatch"

        # Данные
        subj_noun, subj_quant, subj_neg = self.extract_quantified_noun(subj_token)
        obj_noun, obj_quant, obj_neg = self.extract_quantified_noun(obj_token)
        comp_noun, comp_quant, comp_neg = self.extract_quantified_noun(comp_token)

        # Наследование квантора
        if not any(c.dep_ == "det" for c in comp_token.children):
            comp_quant = obj_quant

        # Отрицание
        verb_neg = self.is_negated(root)
        final_neg = subj_neg ^ verb_neg ^ obj_neg ^ comp_neg
        neg_symbol = "¬" if final_neg else ""

        # Переменные
        xv, yv, zv = "x", "y", "z"
        pred_name = root.lemma_.capitalize()

        # Сборка
        subj_rule = QUANTIFIER_RULE[subj_quant]
        obj_rule = QUANTIFIER_RULE[obj_quant]
        comp_rule = QUANTIFIER_RULE[comp_quant]

        atom = f"{neg_symbol}{pred_name}({xv}, {yv}, {zv})"
        level3 = f"{comp_quant}{zv} ({comp_noun}({zv}) {comp_rule} {atom})"
        level2 = f"{obj_quant}{yv} ({obj_noun}({yv}) {obj_rule} {level3})"
        final_formula = f"{subj_quant}{xv} ({subj_noun}({xv}) {subj_rule} {level2})"

        return final_formula

    def __str__(self) -> str:
        return "SVOC"