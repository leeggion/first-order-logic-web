import spacy
from spacy import displacy

QUANTIFIER_MAP = {
    'every': '∀',
    'each': '∀',
    'a': '∃',
    'an': '∃',
    'some': '∃',
    'exists': '∃'
}

ROLE_TO_VAR = {
    'nsubj': 'x', 
    'dobj': 'y'   
}

# 3. Правила сборки для кванторов
QUANTIFIER_RULE = {
    '∀': '→',
    '∃': '∧' 
}


class FolConverterEn:
    """
    Класс для преобразования простых английских утвердительных предложений
    в формулы логики предикатов (FOL).
    
    ОГРАНИЧЕНИЯ (те же, что и раньше):
    - Работает только с простыми предложениями SVO.
    - Требует явных кванторов (определителей).
    - Не обрабатывает отрицания, модальность и т.д.
    - Не решает проблему неоднозначности области действия.
    """

    def __init__(self, model_name="en_core_web_sm"):
        """Загружает NLP-модель spaCy."""
        try:
            self.nlp = spacy.load(model_name)
        except IOError:
            print(f"[Ошибка] Модель '{model_name}' не найдена.")
            print(f"Пожалуйста, установите ее: python -m spacy download {model_name}")
            exit()

    def _extract_phrase_components(self, token):
        noun_lemma = token.lemma_.capitalize()
        quantifier_symbol = None
        
        for child in token.children:
            if child.dep_ == 'det':
                quantifier_symbol = QUANTIFIER_MAP.get(child.lemma_)
                break
        
        return {'noun': noun_lemma, 'quantifier': quantifier_symbol}

    def convert_to_fol(self, text: str) -> str:
        doc = self.nlp(text)
        svg_code = displacy.render(doc, style="dep")
        predicate_token = None
        subject_token = None
        object_token = None
        with open("dependency_tree.svg", "w", encoding="utf-8") as f:
          f.write(svg_code)
        for token in doc:
            if token.dep_ == 'ROOT':
                predicate_token = token
                break
        
        if not predicate_token:
            return "[Ошибка] Не найден главный предикат (ROOT) в предложении."

        for child in predicate_token.children:
            if child.dep_ in ROLE_TO_VAR:
                if child.dep_ == 'nsubj':
                    subject_token = child
                elif child.dep_ == 'dobj':
                    object_token = child

        if not (subject_token and object_token):
            return (f"[Ошибка] Предложение не является SVO. "
                    f"(Субъект={subject_token}, Объект={object_token})")

        
        predicate = {
            'lemma': predicate_token.lemma_.capitalize(),
            'var_x': ROLE_TO_VAR['nsubj'],
            'var_y': ROLE_TO_VAR['dobj']
        }
        
        subject = self._extract_phrase_components(subject_token)
        subject['var'] = ROLE_TO_VAR['nsubj']
        
        object = self._extract_phrase_components(object_token)
        object['var'] = ROLE_TO_VAR['dobj']

        if not subject['quantifier'] or not object['quantifier']:
            return (f"[Ошибка] Не найдены явные кванторы (a, every, some) "
                    f"для субъекта или объекта.")
        
        atom_str = f"{predicate['lemma']}({predicate['var_x']}, {predicate['var_y']})"

        obj_quant = object['quantifier']
        obj_rule = QUANTIFIER_RULE[obj_quant]
        obj_formula = (
            f"{obj_quant}{object['var']} "
            f"({object['noun']}({object['var']}) {obj_rule} {atom_str})"
        )

        subj_quant = subject['quantifier']
        subj_rule = QUANTIFIER_RULE[subj_quant]
        final_formula = (
            f"{subj_quant}{subject['var']} "
            f"({subject['noun']}({subject['var']}) {subj_rule} {obj_formula})"
        )
        return final_formula


if __name__ == "__main__":
    
    converter_en = FolConverterEn()

    sentence4 = "Some professor teaches a course"
    fol4 = converter_en.convert_to_fol(sentence4)
    print(f"Sentence: {sentence4}")
    print(f"FOL Formula: {fol4}")
    print("-" * 30)