from typing import Dict, Optional
import spacy
from utilities.patterns import PATTERNS
from utilities.DependencyVisualizer import DependencyVisualizer

class FolAnalyzerEn:
    """
    Главный фасадный класс для анализа предложений и преобразования их в FOL.

    Класс объединяет:
    1.  Загрузку модели spaCy.
    2.  Выбор подходящего синтаксического паттерна (SVO, SVC, SV).
    3.  Преобразование предложения в формулу логики первого порядка (FOL).
    4.  Визуализацию синтаксического дерева зависимостей.
    """
    
    def __init__(self, model: str = "en_core_web_sm"):
        """
        Инициализирует анализатор, загружая модель spaCy и необходимые инструменты.

        Args:
            model (str): Название модели spaCy для загрузки. По умолчанию: "en_core_web_sm".
        """
        self.nlp = spacy.load(model)
        self.visualizer = DependencyVisualizer()
        self.patterns = PATTERNS

    def analyze(self, text: str) -> Dict[str, Optional[str]]:
        """
        Принимает текст, анализирует его и возвращает структурированный результат.

        

        Выполняет последовательный перебор зарегистрированных паттернов,
        пока не будет найден первый подходящий (`pattern.match(doc)`).

        Args:
            text (str): Входное предложение на английском языке.

        Returns:
            Dict[str, Optional[str]]: Словарь с результатами:
                - **fol (str)**: Строка с формулой FOL или сообщение об ошибке.
                - **tree_html (str)**: HTML-код для визуализации дерева зависимостей.
                - **pattern (str | None)**: Имя примененного паттерна (например, "SVO") или None в случае ошибки.
        """
        doc = self.nlp(text)

        # Поиск подходящего паттерна
        for pattern in self.patterns:
            if pattern.match(doc):
                fol = pattern.convert(doc)
                break
        else:
            fol = "[Ошибка] Не найден подходящий паттерн."

        # HTML дерево зависимостей
        tree_html = self.visualizer.render(doc)

        return {
            "fol": fol,
            "tree_html": tree_html,
            "pattern": str(pattern) if fol[0] != "[" else None
        }
