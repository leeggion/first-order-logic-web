from typing import Any, Optional
import spacy
from utilities.PatternFactory import PatternFactory


class FolConverterEn:
    """
    Класс для преобразования английских предложений в формулы логики предикатов (FOL).
    
    В отличие от FolAnalyzerEn, этот класс отвечает только за преобразование логики
    и не включает визуализацию

    ОГРАНИЧЕНИЯ:
    - Работает только с простыми предложениями.
    - Не обрабатывает модальность, сложные структуры и т.д.
    """

    def __init__(self, model: str = "en_core_web_sm"):
        """
        Инициализирует конвертер и загружает модель spaCy.

        Args:
            model (str): Название модели spaCy для загрузки. По умолчанию: "en_core_web_sm".
        """
        self.nlp = spacy.load(model)
        self.factory = PatternFactory()

    def get_pattern(self, text: str) -> Optional[Any]:
        """
        Анализирует текст и возвращает объект подходящего паттерна.

        Args:
            text (str): Входное предложение.

        Returns:
            Optional[Any]: Объект паттерна (например, SVO, SVC) или строка с ошибкой, если паттерн не найден.
        """
        doc = self.nlp(text)

        pattern = self.factory.get_pattern(doc)
        if not pattern:
            return "[Ошибка] Не удалось определить тип предложения."

        return pattern

    def convert_to_fol(self, text: str) -> str:
        """
        Анализирует текст, выбирает паттерн и преобразует его в формулу FOL.

        Args:
            text (str): Входное предложение.

        Returns:
            str: Строка с формулой FOL или сообщение об ошибке.
        """
        doc = self.nlp(text)

        pattern = self.factory.get_pattern(doc)
        if not pattern:
            return "[Ошибка] Не удалось определить тип предложения."

        return pattern.convert(doc)