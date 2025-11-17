import spacy
from PatternFactory import PatternFactory


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

    def __init__(self, model="en_core_web_sm"):
        self.nlp = spacy.load(model)
        self.factory = PatternFactory()

    def get_pattern(self, text):
        doc = self.nlp(text)

        pattern = self.factory.get_pattern(doc)
        if not pattern:
            return "[Ошибка] Не удалось определить тип предложения."

        return pattern

    def convert_to_fol(self, text):
        doc = self.nlp(text)

        pattern = self.factory.get_pattern(doc)
        if not pattern:
            return "[Ошибка] Не удалось определить тип предложения."

        return pattern.convert(doc)


if __name__ == "__main__":
    converter_en = FolConverterEn()
    sentences = [
        "A student sleeps",  # SV
        "Every dog barks.",  # SV
        "Every student is smart",  # SVC
        "Some cats are cute.",  # SVC
        "Every cat is animal.",  # SVC
        "A sky is blue.",  # SVC
        "Some professor teaches a course",  # SVO
        "All teachers help each student.",  # SVO
        "Every student reads a book."  # SVO
    ]
    for i in sentences:
        print(f"Sentence: {i}")
        print(f"Pattern: {converter_en.get_pattern(i)}")
        print(f"FOL Formula: {converter_en.convert_to_fol(i)}")
        print("-" * 30)
