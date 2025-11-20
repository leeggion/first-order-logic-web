from typing import Optional, Tuple, Any
from .utils import QUANTIFIER_MAP

class Base:
    """
    Базовый абстрактный класс для паттернов преобразования предложений в FOL.

    Обеспечивает общий интерфейс и вспомогательные методы для анализа
    синтаксического дерева, извлечения кванторов и определения отрицаний.
    
    Все конкретные классы паттернов (SVO, SVC, SV и т.д.) должны наследовать
    данный класс и реализовывать его абстрактные методы.
    """

    def match(self, doc: Any) -> bool:
        """
        Определяет, соответствует ли предложение данному синтаксическому паттерну.

        Это абстрактный метод, который должен быть переопределен в дочерних классах.

        Args:
            doc: Обработанный документ или спан (обычно spacy.tokens.Doc).

        Returns:
            bool: True, если предложение соответствует структуре паттерна, иначе False.

        Raises:
            NotImplementedError: Если метод не переопределен в дочернем классе.
        """
        raise NotImplementedError

    def convert(self, doc: Any) -> str:
        """
        Преобразует предложение в строку формата First-Order Logic (FOL).

        Это абстрактный метод, который должен быть переопределен в дочерних классах.

        Args:
            doc: Обработанный документ или спан (обычно spacy.tokens.Doc).

        Returns:
            str: Строка с формулой FOL.

        Raises:
            NotImplementedError: Если метод не переопределен в дочернем классе.
        """
        raise NotImplementedError

    def find_root(self, doc: Any) -> Optional[Any]:
        """
        Находит корневой токен (ROOT) в синтаксическом дереве документа.

        Корень обычно является основным глаголом предложения.

        Args:
            doc: Обработанный документ или спан (обычно spacy.tokens.Doc).

        Returns:
            Optional[Any]: Корневой токен (spacy.tokens.Token) или None, если не найден.
        """
        for token in doc:
            if token.dep_ == 'ROOT':
                return token
        return None

    def is_negated(self, token: Any) -> bool:
        """
        Проверяет наличие грамматического отрицания у токена (обычно глагола).

        Анализирует дочерние элементы токена на наличие зависимости 'neg'
        (например, частицы 'not', 'n\'t').

        Args:
            token: Токен для проверки (spacy.tokens.Token).

        Returns:
            bool: True, если найдено отрицание, иначе False.
        """
        for child in token.children:
            if child.dep_ == "neg":
                return True
        return False

    def extract_quantified_noun(self, token: Any) -> Tuple[str, str, bool]:
        """
        Извлекает информацию о существительном, его кванторе и логическом отрицании.

        Выполняет три задачи:
        1. Извлекает **лемму** существительного.
        2. Определяет **квантор** (явный `det` или неявный по POS-тегу).
        3. Определяет **отрицание**, встроенное в квантор (например, 'no', 'none').

        Если явный квантор (`det`) отсутствует, применяется **эвристика**:
        - Множественное число (`NNS`) -> '∀' (универсальный квантор).
        - Остальные случаи (`NN`, `NNP`) -> '∃' (квантор существования).

        Args:
            token: Токен существительного (обычно nsubj или dobj).

        Returns:
            Tuple[str, str, bool]: Кортеж из трех элементов:
                - **noun (str)**: Лемма существительного с заглавной буквы.
                - **quantifier (str)**: Символ квантора ('∀' или '∃').
                - **is_quant_neg (bool)**: Флаг отрицательного квантора (True для 'no'/'none').
        """
        noun = token.lemma_.capitalize()
        quantifier = None
        is_quant_neg = False

        # 1. Ищем явный квантор (det)
        for child in token.children:
            # print(child, child.dep_)
            if child.dep_ == "det":
                lemma = child.lemma_.lower()
                if lemma in QUANTIFIER_MAP:
                    quantifier = QUANTIFIER_MAP[lemma]
                    # Если квантор 'no' или 'none', это логическое отрицание
                    if lemma in ['no', 'none', 'not']:
                        is_quant_neg = True
                    break
            elif child.dep_ == "neg":
                is_quant_neg = True
        
        # 2. Если квантор не найден, применяем эвристику (Implicit Quantifiers)
        if quantifier is None:
            # NNS = Noun, plural (Множественное число) -> Обычно "Все" (Dogs bark -> All dogs bark)
            # NN = Noun, singular (Единственное число) -> Обычно "Существует" (Student reads -> A student reads)
            # NNP = Proper noun (Имя собственное) -> Пока трактуем как ∃ (John sleeps -> Exists x (John(x) AND Sleep(x)))
            
            if token.tag_ == "NNS":
                quantifier = '∀'
            else:
                quantifier = '∃'

        return noun, quantifier, is_quant_neg