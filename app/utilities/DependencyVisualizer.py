from spacy import displacy

class DependencyVisualizer:
    """
    Визуализатор синтаксического дерева зависимостей предложения.
    Используется внутри веб-приложения Flask.

    Основные возможности:
    ---------------------
    - принимает документ spaCy
    - генерирует HTML-код с деревом зависимостей
    - возвращает HTML, готовый для вставки в шаблон Jinja2
    """

    def __init__(self, style="dep"):
        self.style = style

    def render(self, doc):
        """
        Преобразует spaCy Doc в HTML-дерево зависимостей.
        Параметры:
            doc : spaCy Doc

        Возвращает:
            HTML-строка с визуализацией displacy
        """

        html = displacy.render(
            doc,
            style=self.style,
            page=True,         # Генерирует полноценную web-страницу (можно выключить)
            minify=True        # Убирает пробелы, чтобы HTML был компактным
        )
        return html
