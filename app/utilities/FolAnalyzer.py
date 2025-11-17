import spacy
from utilities.patterns import PATTERNS
from utilities.DependencyVisualizer import DependencyVisualizer

class FolAnalyzerEn:
    """
    Главный фасадный класс: принимает предложение, анализирует, выбирает паттерн,
    преобразует в FOL и формирует визуализацию зависимостей.
    """
    
    def __init__(self, model="en_core_web_sm"):
        self.nlp = spacy.load(model)
        self.visualizer = DependencyVisualizer()
        self.patterns = PATTERNS

    def analyze(self, text):
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
