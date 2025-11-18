from typing import Any
from spacy import displacy

class DependencyVisualizer:
    """
    Класс для генерации HTML-визуализации синтаксического дерева зависимостей.

    Использует библиотеку `spacy.displacy` для создания интерактивного
    дерева, пригодного для встраивания в веб-приложения (например, на Flask).
    """

    def __init__(self, style: str = "dep"):
        """
        Инициализирует визуализатор.

        Args:
            style (str): Стиль визуализации displacy. По умолчанию: "dep" (зависимости).
        """
        self.style = style

    def render(self, doc: Any) -> str:
        """
        Преобразует объект spaCy Doc в HTML-строку с визуализацией зависимостей.

        Args:
            doc: Обработанный документ или спан spaCy (spacy.tokens.Doc | Span).

        Returns:
            str: HTML-строка с визуализацией displacy.
        """

        html = displacy.render(
            doc,
            style=self.style,
            page=True,         # Генерирует полноценную web-страницу (можно выключить)
            minify=True        # Убирает пробелы, чтобы HTML был компактным
        )
        return html
