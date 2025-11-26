# Полный код: преобразование в ПНФ (как было) + сколемизация префиксной (ПНФ) формулы.
# Добавлена поддержка подстановок и сколемизации по алгоритму:
# читаем префикс слева-направо, для ∃: если перед ним нет ∀ -> константа, иначе -> функция от предшествующих ∀.
from dataclasses import dataclass
from typing import List, Tuple, Set, Dict, Optional, Union
import itertools
from typing import Any


class Formula:
    def eliminate_implications(self) -> "Formula":
        raise NotImplementedError()
    def to_nnf(self) -> "Formula":
        raise NotImplementedError()
    def free_vars(self) -> Set[str]:
        raise NotImplementedError()
    def rename_bound_vars(self, mapping: Dict[str, str]) -> "Formula":
        raise NotImplementedError()
    def fresh_rename(self, used: Set[str], counter: itertools.count) -> "Formula":
        raise NotImplementedError()
    def pull_out_quantifiers(self) -> Tuple[List[Tuple[str, str]], "Formula"]:
        raise NotImplementedError()
    def build_prefix(self, qlist: List[Tuple[str, str]]) -> "Formula":
        res: Formula = self
        for q, v in reversed(qlist):
            if q == "forall":
                res = ForAll(v, res)
            else:
                res = Exists(v, res)
        return res
    # подстановка: mapping: имя переменной -> Term (новый терм)
    def substitute(self, mapping: Dict[str, "Term"]) -> "Formula":
        raise NotImplementedError()
    def __str__(self) -> str:
        raise NotImplementedError()

# Term теперь поддерживает функции: name(args...)
@dataclass(frozen=True)
class Term:
    name: str
    args: Tuple["Term", ...] = ()
    def __str__(self):
        if self.args:
            return f"{self.name}({', '.join(map(str,self.args))})"
        return self.name

def substitute_in_term(t: Term, mapping: Dict[str, Term]) -> Term:
    # Если это переменная (без аргументов) и есть замена -> заменить полностью
    if not t.args and t.name in mapping:
        return mapping[t.name]
    # иначе рекурсивно подставить в аргументы (если есть)
    if t.args:
        return Term(t.name, tuple(substitute_in_term(a, mapping) for a in t.args))
    return t

# ------------------------------
# Атомы и связки
# ------------------------------

@dataclass
class Atom(Formula):
    name: str
    args: Tuple[Term, ...]
    def eliminate_implications(self):
        return self
    def to_nnf(self):
        return self
    def free_vars(self) -> Set[str]:
        # считаем свободными те термы, которые представляют переменные (без args)
        return {t.name for t in self.args if not t.args}
    def rename_bound_vars(self, mapping: Dict[str, str]):
        return self
    def fresh_rename(self, used: Set[str], counter: itertools.count):
        return self
    def pull_out_quantifiers(self):
        return ([], self)
    def substitute(self, mapping: Dict[str, Term]) -> "Atom":
        return Atom(self.name, tuple(substitute_in_term(a, mapping) for a in self.args))
    def __str__(self):
        if self.args:
            return f"{self.name}({', '.join(map(str,self.args))})"
        return self.name

@dataclass
class Not(Formula):
    f: Formula
    def eliminate_implications(self):
        return Not(self.f.eliminate_implications())
    def to_nnf(self):
        inner = self.f
        if isinstance(inner, Not):
            return inner.f.to_nnf()
        if isinstance(inner, And):
            return Or(Not(inner.left).to_nnf(), Not(inner.right).to_nnf())
        if isinstance(inner, Or):
            return And(Not(inner.left).to_nnf(), Not(inner.right).to_nnf())
        if isinstance(inner, ForAll):
            return Exists(inner.var, Not(inner.body).to_nnf())
        if isinstance(inner, Exists):
            return ForAll(inner.var, Not(inner.body).to_nnf())
        return Not(inner.to_nnf())
    def free_vars(self) -> Set[str]:
        return self.f.free_vars()
    def rename_bound_vars(self, mapping: Dict[str, str]):
        return Not(self.f.rename_bound_vars(mapping))
    def fresh_rename(self, used: Set[str], counter: itertools.count):
        return Not(self.f.fresh_rename(used, counter))
    def pull_out_quantifiers(self):
        # После to_nnf под Not не будут кванторы — значит Not над матрицей (атомами)
        return ([], self)
    def substitute(self, mapping: Dict[str, Term]) -> "Not":
        return Not(self.f.substitute(mapping))
    def __str__(self):
        return f"¬{wrap(self.f)}"

@dataclass
class And(Formula):
    left: Formula
    right: Formula
    def eliminate_implications(self):
        return And(self.left.eliminate_implications(), self.right.eliminate_implications())
    def to_nnf(self):
        return And(self.left.to_nnf(), self.right.to_nnf())
    def free_vars(self) -> Set[str]:
        return self.left.free_vars() | self.right.free_vars()
    def rename_bound_vars(self, mapping: Dict[str, str]):
        return And(self.left.rename_bound_vars(mapping), self.right.rename_bound_vars(mapping))
    def fresh_rename(self, used: Set[str], counter: itertools.count):
        return And(self.left.fresh_rename(used, counter), self.right.fresh_rename(used, counter))
    def pull_out_quantifiers(self):
        left_qs, left_mat = self.left.pull_out_quantifiers()
        right_qs, right_mat = self.right.pull_out_quantifiers()
        qs = left_qs + right_qs
        mat = And(left_mat, right_mat)
        return (qs, mat)
    def substitute(self, mapping: Dict[str, Term]) -> "And":
        return And(self.left.substitute(mapping), self.right.substitute(mapping))
    def __str__(self):
        return f"({self.left} ∧ {self.right})"

@dataclass
class Or(Formula):
    left: Formula
    right: Formula
    def eliminate_implications(self):
        return Or(self.left.eliminate_implications(), self.right.eliminate_implications())
    def to_nnf(self):
        return Or(self.left.to_nnf(), self.right.to_nnf())
    def free_vars(self) -> Set[str]:
        return self.left.free_vars() | self.right.free_vars()
    def rename_bound_vars(self, mapping: Dict[str, str]):
        return Or(self.left.rename_bound_vars(mapping), self.right.rename_bound_vars(mapping))
    def fresh_rename(self, used: Set[str], counter: itertools.count):
        return Or(self.left.fresh_rename(used, counter), self.right.fresh_rename(used, counter))
    def pull_out_quantifiers(self):
        left_qs, left_mat = self.left.pull_out_quantifiers()
        right_qs, right_mat = self.right.pull_out_quantifiers()
        qs = left_qs + right_qs
        mat = Or(left_mat, right_mat)
        return (qs, mat)
    def substitute(self, mapping: Dict[str, Term]) -> "Or":
        return Or(self.left.substitute(mapping), self.right.substitute(mapping))
    def __str__(self):
        return f"({self.left} ∨ {self.right})"

@dataclass
class Implies(Formula):
    left: Formula
    right: Formula
    def eliminate_implications(self):
        return Or(Not(self.left).eliminate_implications(), self.right.eliminate_implications())
    def to_nnf(self):
        return self.eliminate_implications().to_nnf()
    def free_vars(self) -> Set[str]:
        return self.left.free_vars() | self.right.free_vars()
    def rename_bound_vars(self, mapping: Dict[str, str]):
        return Implies(self.left.rename_bound_vars(mapping), self.right.rename_bound_vars(mapping))
    def fresh_rename(self, used: Set[str], counter: itertools.count):
        return Implies(self.left.fresh_rename(used, counter), self.right.fresh_rename(used, counter))
    def pull_out_quantifiers(self):
        return self.eliminate_implications().pull_out_quantifiers()
    def substitute(self, mapping: Dict[str, Term]) -> "Formula":
        return Implies(self.left.substitute(mapping), self.right.substitute(mapping))
    def __str__(self):
        return f"({self.left} → {self.right})"

@dataclass
class Iff(Formula):
    left: Formula
    right: Formula
    def eliminate_implications(self):
        return And(Implies(self.left, self.right).eliminate_implications(),
                   Implies(self.right, self.left).eliminate_implications())
    def to_nnf(self):
        return self.eliminate_implications().to_nnf()
    def free_vars(self) -> Set[str]:
        return self.left.free_vars() | self.right.free_vars()
    def rename_bound_vars(self, mapping: Dict[str, str]):
        return Iff(self.left.rename_bound_vars(mapping), self.right.rename_bound_vars(mapping))
    def fresh_rename(self, used: Set[str], counter: itertools.count):
        return Iff(self.left.fresh_rename(used, counter), self.right.fresh_rename(used, counter))
    def pull_out_quantifiers(self):
        return self.eliminate_implications().pull_out_quantifiers()
    def substitute(self, mapping: Dict[str, Term]) -> "Iff":
        return Iff(self.left.substitute(mapping), self.right.substitute(mapping))
    def __str__(self):
        return f"({self.left} ↔ {self.right})"

@dataclass
class ForAll(Formula):
    var: str
    body: Formula
    def eliminate_implications(self):
        return ForAll(self.var, self.body.eliminate_implications())
    def to_nnf(self):
        return ForAll(self.var, self.body.to_nnf())
    def free_vars(self) -> Set[str]:
        return self.body.free_vars() - {self.var}
    def rename_bound_vars(self, mapping: Dict[str, str]):
        if self.var in mapping:
            newvar = mapping[self.var]
            return ForAll(newvar, self.body.rename_bound_vars({**mapping, self.var: newvar}))
        else:
            return ForAll(self.var, self.body.rename_bound_vars(mapping))
    def fresh_rename(self, used: Set[str], counter: itertools.count):
        base = self.var
        new = base
        while new in used:
            new = f"{base}_{next(counter)}"
        used2 = set(used)
        used2.add(new)
        return ForAll(new, self.body.rename_bound_vars({self.var: new}).fresh_rename(used2, counter))
    def pull_out_quantifiers(self):
        inner_qs, inner_mat = self.body.pull_out_quantifiers()
        return ( [("forall", self.var)] + inner_qs, inner_mat )
    def substitute(self, mapping: Dict[str, Term]) -> "ForAll":
        # защита переменной связанного квантора: если есть замена для var, не применять её внутри
        mapping2 = {k:v for k,v in mapping.items() if k != self.var}
        return ForAll(self.var, self.body.substitute(mapping2))
    def __str__(self):
        return f"∀{self.var}.({self.body})"

@dataclass
class Exists(Formula):
    var: str
    body: Formula
    def eliminate_implications(self):
        return Exists(self.var, self.body.eliminate_implications())
    def to_nnf(self):
        return Exists(self.var, self.body.to_nnf())
    def free_vars(self) -> Set[str]:
        return self.body.free_vars() - {self.var}
    def rename_bound_vars(self, mapping: Dict[str, str]):
        if self.var in mapping:
            newvar = mapping[self.var]
            return Exists(newvar, self.body.rename_bound_vars({**mapping, self.var: newvar}))
        else:
            return Exists(self.var, self.body.rename_bound_vars(mapping))
    def fresh_rename(self, used: Set[str], counter: itertools.count):
        base = self.var
        new = base
        while new in used:
            new = f"{base}_{next(counter)}"
        used2 = set(used)
        used2.add(new)
        return Exists(new, self.body.rename_bound_vars({self.var: new}).fresh_rename(used2, counter))
    def pull_out_quantifiers(self):
        inner_qs, inner_mat = self.body.pull_out_quantifiers()
        return ( [("exists", self.var)] + inner_qs, inner_mat )
    def substitute(self, mapping: Dict[str, Term]) -> "Exists":
        mapping2 = {k:v for k,v in mapping.items() if k != self.var}
        return Exists(self.var, self.body.substitute(mapping2))
    def __str__(self):
        return f"∃{self.var}.({self.body})"

# ------------------------------
# Вспомогательные функции
# ------------------------------

def wrap(f: Formula) -> str:
    if isinstance(f, Atom) or (isinstance(f, Not) and isinstance(f.f, Atom)):
        return str(f)
    return f"({f})"

_unique_counter = itertools.count(1)

# to_prenex — оставляем как раньше (без изменений по смыслу)
def to_prenex(formula: Formula) -> Formula:
    step1 = formula.eliminate_implications()
    print("После устранения импликаций:\n ", step1)
    step2 = step1.to_nnf()
    print("В форме ННФ (negation normal form):\n ", step2)
    used = set(step2.free_vars())
    step3 = step2.fresh_rename(used, itertools.count(1))
    print("После переименования связанных переменных (уникальные):\n ", step3)
    qs, mat = step3.pull_out_quantifiers()
    print("Список кванторов (слева направо):", qs)
    print("Матрица (без кванторов):\n ", mat)
    res = mat.build_prefix(qs)
    return res

# ------------------------------
# Сколемизация (на входе: формула в ПНФ)
# ------------------------------

def skolemize_prenex(formula: Formula) -> Formula:
    """
    Ожидает: формула в ПНФ (всё в виде префикса кванторов + матрица).
    Алгоритм:
      1) Получаем список кванторов и матрицу через pull_out_quantifiers()
      2) Идём слева-направо по списку кванторов:
         - если 'forall' -> добавляем имя в список универсальных (не заменяем)
         - если 'exists' -> если ранее нет универсальных -> вводим новую сколем-константу
                             иначе -> вводим сколем-функцию от текущного списка универсальных
           Далее выполняем подстановку для ВСЕХ последующих кванторов и для матрицы:
             заменяем имя связной переменной на соответствующий Term
      3) После прохода удаляем все кванторы ∀ (оставляем чистую формулу без кванторов)
    """
    qs, mat = formula.pull_out_quantifiers()
    # список универсальных переменных, которые встретились к этому моменту
    universals: List[str] = []
    # mapping: имя переменной -> Term (сколем-терм)
    mapping: Dict[str, Term] = {}
    # уникализатор для имён сколем-функций и констант
    counter = itertools.count(1)

    # Обрабатываем префикс слева-направо
    for i, (qtype, var) in enumerate(qs):
        if qtype == "forall":
            # просто добавляем в список универсальных (никаких замен)
            universals.append(var)
        elif qtype == "exists":
            # создаём сколем-терм
            if len(universals) == 0:
                # сколемовская константа
                sk_name = f"c_{var}_{next(counter)}"
                sk_term = Term(sk_name, ())
            else:
                # сколем-функция от текущих универсальных
                sk_name = f"f_{var}_{next(counter)}"
                args = tuple(Term(u, ()) for u in universals)
                sk_term = Term(sk_name, args)
            # пометим замену
            mapping[var] = sk_term
            # После того, как мы заменили эту существующую переменную, мы должны
            # применить эту подстановку ко всем оставшимся кванторам и матрице.
            # Это делаем, чтобы последующие кванторы/тела не ссылались на старое имя.
            # Для этого мы заменяем все в списке qs (в оставшейся части) и в mat.
            # — заменяем имена связных переменных в qs (чтобы, если позже встретится тот же var — его защита)
            new_qs = []
            for j in range(i+1, len(qs)):
                qj, varj = qs[j]
                # если varj совпадает с тем, что мы заменили — заменяем его имя в префиксе
                # (хотя это маловероятно, т.к. мы предварительно делали fresh_rename, но на всякий случай)
                if varj == var:
                    varj = f"{varj}_repl"
                new_qs.append((qj, varj))
            # обновляем оставшуюся часть префикса
            qs = qs[:i+1] + new_qs
            # Применим подстановку к матрице (и к уже существующим подстановкам — необходимости нет,
            # т.к. mapping маппит только оригинальные имена, не термы)
            mat = mat.substitute(mapping)
        else:
            raise ValueError("Неизвестный тип квантора в префиксе: " + str(qtype))

    # На всякий случай применим финальную подстановку ко всей матрице
    mat = mat.substitute(mapping)

    # Удаляем все ∀, возвращаем матрицу без кванторов
    def remove_forall(f: Formula) -> Formula:
        if isinstance(f, ForAll):
            return remove_forall(f.body)
        if isinstance(f, And):
            return And(remove_forall(f.left), remove_forall(f.right))
        if isinstance(f, Or):
            return Or(remove_forall(f.left), remove_forall(f.right))
        if isinstance(f, Not):
            return Not(remove_forall(f.f))
        # атомы/прочее
        return f

    return remove_forall(mat)

# ------------------------------
# Примеры / демонстрация
# ------------------------------

import re
from typing import List, Optional


# ------------------------------
# Парсер формул
# ------------------------------

class Parser:
    def __init__(self, text: str):
        self.tokens = self.tokenize(text)
        self.pos = 0

    def tokenize(self, text: str) -> List[str]:
        """Разбивает строку на токены"""
        # Специальные символы и операторы (добавили точку)
        special = r'[∀∃∧∨¬→↔(),.]'
        # Идентификаторы (переменные, предикаты, функции)
        identifier = r'[a-zA-Z_][a-zA-Z0-9_]*'

        pattern = f'{special}|{identifier}'
        tokens = re.findall(pattern, text)
        return [t for t in tokens if t.strip()]

    def current_token(self) -> Optional[str]:
        """Возвращает текущий токен"""
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def eat(self, expected: Optional[str] = None) -> str:
        """Считывает текущий токен и перемещается к следующему"""
        if self.pos >= len(self.tokens):
            raise SyntaxError(f"Неожиданный конец строки, ожидалось: {expected}")

        token = self.tokens[self.pos]
        if expected and token != expected:
            raise SyntaxError(f"Ожидался '{expected}', но получен '{token}'")

        self.pos += 1
        return token

    def try_eat(self, expected: str) -> bool:
        """Пытается съесть токен, если он соответствует ожидаемому"""
        if self.current_token() == expected:
            self.pos += 1
            return True
        return False

    def match(self, expected: str) -> bool:
        """Проверяет, совпадает ли текущий токен с ожидаемым"""
        return self.current_token() == expected

    def parse(self) -> Formula:
        """Парсит полную формулу"""
        result = self.parse_impl()
        if self.current_token() is not None:
            raise SyntaxError(f"Лишние токены в конце: {self.tokens[self.pos:]}")
        return result

    def parse_impl(self) -> Formula:
        """Парсит импликацию (самый низкий приоритет)"""
        left = self.parse_or()

        while self.match('→') or self.match('->'):
            op = self.eat()
            right = self.parse_or()
            left = Implies(left, right)

        return left

    def parse_or(self) -> Formula:
        """Парсит дизъюнкцию"""
        left = self.parse_and()

        while self.match('∨') or self.match('|'):
            op = self.eat()
            right = self.parse_and()
            left = Or(left, right)

        return left

    def parse_and(self) -> Formula:
        """Парсит конъюнкцию"""
        left = self.parse_not()

        while self.match('∧') or self.match('&'):
            op = self.eat()
            right = self.parse_not()
            left = And(left, right)

        return left

    def parse_not(self) -> Formula:
        """Парсит отрицание"""
        if self.match('¬') or self.match('~') or self.match('!'):
            self.eat()
            return Not(self.parse_not())

        return self.parse_quantifier_or_atom()

    def parse_quantifier_or_atom(self) -> Formula:
        """Парсит кванторы или атомарные формулы"""
        # Кванторы
        if self.match('∀') or self.match('forall'):
            op = self.eat()
            var = self.parse_variable()
            # Точка теперь не обязательна
            self.try_eat('.')
            body = self.parse_impl()
            return ForAll(var, body)

        elif self.match('∃') or self.match('exists'):
            op = self.eat()
            var = self.parse_variable()
            # Точка теперь не обязательна
            self.try_eat('.')
            body = self.parse_impl()
            return Exists(var, body)

        # Атомарные формулы и скобки
        return self.parse_atom()

    def parse_variable(self) -> str:
        """Парсит переменную"""
        token = self.eat()
        if not re.match(r'[a-zA-Z_][a-zA-Z0-9_]*', token):
            raise SyntaxError(f"Ожидалась переменная, но получено: {token}")
        return token

    def parse_atom(self) -> Formula:
        """Парсит атомарные формулы"""
        if self.match('('):
            self.eat('(')
            expr = self.parse_impl()
            self.eat(')')
            return expr

        # Предикат или пропозициональная переменная
        ident = self.eat()
        if not re.match(r'[a-zA-Z_][a-zA-Z0-9_]*', ident):
            raise SyntaxError(f"Ожидался идентификатор, но получено: {ident}")

        # Проверяем, есть ли аргументы
        if self.match('('):
            self.eat('(')
            args = self.parse_terms()
            self.eat(')')
            return Atom(ident, tuple(args))
        else:
            # Пропозициональная переменная (предикат без аргументов)
            return Atom(ident, ())

    def parse_terms(self) -> List[Term]:
        """Парсит список термов, разделенных запятыми"""
        terms = []

        # Первый терм
        terms.append(self.parse_term())

        # Остальные термы (если есть)
        while self.match(','):
            self.eat(',')
            terms.append(self.parse_term())

        return terms

    def parse_term(self) -> Term:
        """Парсит терм (переменная, константа или функция)"""
        ident = self.eat()
        if not re.match(r'[a-zA-Z_][a-zA-Z0-9_]*', ident):
            raise SyntaxError(f"Ожидался идентификатор терма, но получено: {ident}")

        # Проверяем, есть ли аргументы у функции
        if self.match('('):
            self.eat('(')
            args = self.parse_terms()
            self.eat(')')
            return Term(ident, tuple(args))
        else:
            # Переменная или константа
            return Term(ident, ())


def parse_formula(text: str) -> Formula:
    """Парсит строку в формулу"""
    return Parser(text).parse()

# ------------------------------
# Алгоритм унификации
# ------------------------------

@dataclass
class UnificationResult:
    success: bool
    substitution: Dict[str, Term]
    message: str = ""

class Unifier:
    """Класс для унификации формул и термов (Исправленный)"""
    
    @staticmethod
    def is_variable(term: Term) -> bool:
        """
        Проверяет, является ли терм переменной.
        Переменная должна начинаться с маленькой буквы и не иметь аргументов.
        ВАЖНО: Убрано ограничение len == 1, чтобы работали x_1, var_2 и т.д.
        """
        # Проверяем, что нет аргументов, имя не пустое и первая буква строчная
        return (not term.args) and term.name and term.name[0].islower()
    
    @staticmethod
    def apply_substitution(term: Term, substitution: Dict[str, Term]) -> Term:
        # Если это переменная и она есть в подстановке -> заменяем
        if Unifier.is_variable(term) and term.name in substitution:
            # Рекурсивно применяем подстановку к результату, если нужно
            return Unifier.apply_substitution(substitution[term.name], substitution)
        
        # Если есть аргументы -> рекурсивно обрабатываем их
        if term.args:
            new_args = tuple(Unifier.apply_substitution(arg, substitution) for arg in term.args)
            return Term(term.name, new_args)
        
        return term
    
    @staticmethod
    def occurs_check(var: str, term: Term, substitution: Dict[str, Term]) -> bool:
        term_sub = Unifier.apply_substitution(term, substitution)
        if Unifier.is_variable(term_sub) and term_sub.name == var:
            return True
        if term_sub.args:
            return any(Unifier.occurs_check(var, arg, substitution) for arg in term_sub.args)
        return False
    
    @staticmethod
    def unify_terms(term1: Term, term2: Term, substitution: Dict[str, Term]) -> UnificationResult:
        t1 = Unifier.apply_substitution(term1, substitution)
        t2 = Unifier.apply_substitution(term2, substitution)
        
        if t1 == t2:
            return UnificationResult(True, substitution)
        
        if Unifier.is_variable(t1):
            if Unifier.occurs_check(t1.name, t2, substitution):
                return UnificationResult(False, {}, f"Occurs check: {t1.name} in {t2}")
            substitution[t1.name] = t2
            return UnificationResult(True, substitution)
            
        if Unifier.is_variable(t2):
            if Unifier.occurs_check(t2.name, t1, substitution):
                return UnificationResult(False, {}, f"Occurs check: {t2.name} in {t1}")
            substitution[t2.name] = t1
            return UnificationResult(True, substitution)
            
        if t1.name != t2.name or len(t1.args) != len(t2.args):
            return UnificationResult(False, {}, f"Mismatch: {t1} vs {t2}")
            
        current_sub = substitution
        for arg1, arg2 in zip(t1.args, t2.args):
            res = Unifier.unify_terms(arg1, arg2, current_sub)
            if not res.success:
                return res
            current_sub = res.substitution
            
        return UnificationResult(True, current_sub)

    @staticmethod
    def unify_atoms(atom1: Atom, atom2: Atom) -> UnificationResult:
        if atom1.name != atom2.name or len(atom1.args) != len(atom2.args):
            return UnificationResult(False, {}, "Different predicates or arity")
        
        substitution = {}
        for arg1, arg2 in zip(atom1.args, atom2.args):
            res = Unifier.unify_terms(arg1, arg2, substitution)
            if not res.success:
                return res
            substitution = res.substitution
        return UnificationResult(True, substitution)

def create_test_formulas():
    """Создает тестовые формулы для унификации"""
    
    # Первая формула: R(p(x), p(p(s(a))), g(g(f(f(f(φ(b)))))), g(f(g(p(y)))), h(q(y), x))
    term1_1 = Term("p", (Term("x"),))
    term1_2 = Term("p", (Term("p", (Term("s", (Term("a"),)),)),))
    term1_3 = Term("g", (Term("g", (Term("f", (Term("f", (Term("f", (Term("φ", (Term("b"),)),)),)),)),)),))
    term1_4 = Term("g", (Term("f", (Term("g", (Term("p", (Term("y"),)),)),)),))
    term1_5 = Term("h", (Term("q", (Term("y"),)), Term("x")))
    
    formula1 = Atom("R", (term1_1, term1_2, term1_3, term1_4, term1_5))
    
    # Вторая формула: R(p(r(u)), p(p(u)), g(g(f(f(f(t))))), g(f(g(p(c)))), h(z, r(u)))
    term2_1 = Term("p", (Term("r", (Term("u"),)),))
    term2_2 = Term("p", (Term("p", (Term("u"),)),))
    term2_3 = Term("g", (Term("g", (Term("f", (Term("f", (Term("f", (Term("t"),)),)),)),)),))
    term2_4 = Term("g", (Term("f", (Term("g", (Term("p", (Term("c"),)),)),)),))
    term2_5 = Term("h", (Term("z"), Term("r", (Term("u"),))))
    
    formula2 = Atom("R", (term2_1, term2_2, term2_3, term2_4, term2_5))
    
    return [formula1, formula2]

def test_complex_unification():
    """Тестирование унификации сложных формул"""
    print("=== ТЕСТИРОВАНИЕ УНИФИКАЦИИ СЛОЖНЫХ ФОРМУЛ ===")
    
    formulas = create_test_formulas()
    
    print("\nИСХОДНЫЕ ФОРМУЛЫ:")
    print("Формула 1:", formulas[0])
    print("Формула 2:", formulas[1])
    
    print("\nПРОЦЕСС УНИФИКАЦИИ:")
    
    # Тестируем унификацию атомов напрямую
    print("\n1. Прямая унификация атомов:")
    result = Unifier.unify_atoms(formulas[0], formulas[1])
    print(f"Успех: {result.success}")
    if result.success:
        print("Подстановка:")
        for var, term in result.substitution.items():
            print(f"  {var} -> {term}")
        
        # Применяем подстановку
        formula1_sub = formulas[0].substitute(result.substitution)
        formula2_sub = formulas[1].substitute(result.substitution)
        
        print("\nПосле подстановки:")
        print("Формула 1:", formula1_sub)
        print("Формула 2:", formula2_sub)
        print(f"Формулы идентичны: {formula1_sub == formula2_sub}")
    else:
        print(f"Причина неудачи: {result.message}")
    
    # Тестируем унификацию списка формул
    print("\n2. Унификация списка формул:")
    unified_formulas = Unifier.unify_formula_list(formulas)
    
    print("\nРЕЗУЛЬТАТ УНИФИКАЦИИ:")
    for i, formula in enumerate(unified_formulas):
        print(f"Формула {i+1}: {formula}")
    
    # Детальный анализ результата
    print("\nДЕТАЛЬНЫЙ АНАЛИЗ:")
    if len(unified_formulas) >= 2:
        are_identical = str(unified_formulas[0]) == str(unified_formulas[1])
        print(f"Унифицированные формулы идентичны: {are_identical}")
        
        if not are_identical:
            print("\nРазличия по позициям:")
            atom1 = unified_formulas[0]
            atom2 = unified_formulas[1]
            if isinstance(atom1, Atom) and isinstance(atom2, Atom):
                for pos, (arg1, arg2) in enumerate(zip(atom1.args, atom2.args)):
                    if str(arg1) != str(arg2):
                        print(f"  Позиция {pos+1}:")
                        print(f"    Формула 1: {arg1}")
                        print(f"    Формула 2: {arg2}")


# =========================================================
# Вспомогательные классы и функции для Резолюции
# =========================================================

@dataclass(frozen=True)
class Literal:
    """Представление литеры: Атом или ¬Атом."""
    name: str
    args: Tuple[Term, ...]
    negated: bool

    def __str__(self):
        s = f"{self.name}"
        if self.args:
            s += f"({', '.join(map(str, self.args))})"
        return f"¬{s}" if self.negated else s

    def substitute(self, mapping: Dict[str, Term]) -> 'Literal':
        """Применяет подстановку к аргументам литеры."""
        new_args = tuple(substitute_in_term(a, mapping) for a in self.args)
        return Literal(self.name, new_args, self.negated)

    def to_atom(self) -> Atom:
        """Возвращает объект Atom для унификации (игнорируя отрицание)."""
        return Atom(self.name, self.args)

def formula_to_clauses(formula: Formula) -> List[List[Literal]]:
    """
    Преобразует формулу (после сколемизации) в список клозов (КНФ).
    Формула должна быть в NNF.
    """
    f = formula.to_nnf()

    def distribute(f_node: Formula) -> List[List[Literal]]:
        # Базовый случай: Литера (Атом или Not(Atom))
        if isinstance(f_node, Atom):
            return [[Literal(f_node.name, f_node.args, False)]]
        if isinstance(f_node, Not):
            if isinstance(f_node.f, Atom):
                return [[Literal(f_node.f.name, f_node.f.args, True)]]
            # Если Not над сложной формулой, рекурсивно спускаем (хотя to_nnf должен был убрать)
            return distribute(f_node.to_nnf())
        
        # Конъюнкция: объединяем списки клозов (C1 & C2 -> [C1, C2])
        if isinstance(f_node, And):
            return distribute(f_node.left) + distribute(f_node.right)
        
        # Дизъюнкция: распределительный закон (A & B) v C -> (A v C) & (B v C)
        if isinstance(f_node, Or):
            left_clauses = distribute(f_node.left)
            right_clauses = distribute(f_node.right)
            result = []
            for c1 in left_clauses:
                for c2 in right_clauses:
                    # Объединяем литеры двух клозов
                    new_clause = c1 + c2
                    # Убираем дубликаты литер внутри одного клоза
                    unique_clause = sorted(list(set(new_clause)), key=str)
                    result.append(unique_clause)
            return result
        
        return []

    return distribute(f)

# =========================================================
# Основная логика: run_resolution
# =========================================================

def run_resolution(premises: List[str], goal: str) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Главная функция для интерфейса.
    Принимает список посылок и цель (строки).
    Возвращает ("ENTAILS" / "NOT ENTAILS", список_шагов).
    """
    steps_data = []
    
    def add_step(cid: int, clause_str: str, info: str, parents: List[int] = None, subst: str = ""):
        steps_data.append({
            "id": cid,
            "clause": clause_str,
            "info": info,
            "parents": parents or [],
            "substitution": subst
        })

    try:
        # 1. Парсинг
        prem_formulas = [parse_formula(p) for p in premises]
        goal_formula = parse_formula(goal)
        
        # 2. Построение отрицания цели: (P1 & P2 & ...) & ¬Goal
        full_formula = Not(goal_formula)
        for p in reversed(prem_formulas):
            full_formula = And(p, full_formula)
        
        # 3. Преобразование в ПНФ и Сколемизация
        prenex = to_prenex(full_formula)
        skolemized = skolemize_prenex(prenex)

        # 4. Получение КНФ (Клозов)
        clauses = formula_to_clauses(skolemized)
        
        # Хранилище клозов: список кортежей (id, [Literals], parent_info)
        clause_db = []
        seen_clauses = set()

        def add_clause_to_db(lits: List[Literal], info: str, parents: List[int] = None, subst: str = "") -> int:
            lits_sorted = sorted(lits, key=str)
            s_rep = ", ".join(str(l) for l in lits_sorted)
            
            if s_rep in seen_clauses:
                return -1 # Дубликат
            
            cid = len(clause_db) + 1
            clause_db.append({'id': cid, 'lits': lits_sorted, 'info': info, 'str': s_rep})
            seen_clauses.add(s_rep)
            
            add_step(cid, s_rep, info, parents, subst)
            return cid

        for c in clauses:
            add_clause_to_db(c, "Initial")

        # 5. Цикл резолюции (Saturation)
        max_steps = 1000
        step_count = 0
        new_clauses_indices = list(range(len(clause_db)))
        
        while new_clauses_indices and step_count < max_steps:
            current_batch_indices = new_clauses_indices
            new_clauses_indices = []
            total_clauses_count = len(clause_db)
            
            for i in current_batch_indices:
                clause_1_obj = clause_db[i]
                
                for j in range(total_clauses_count):
                    step_count += 1
                    clause_2_obj = clause_db[j]
                    
                    resolvents = resolve_clauses(clause_1_obj['lits'], clause_2_obj['lits'])
                    
                    for res_lits, subst_str in resolvents:
                        if not res_lits:
                            # Пустой клоз
                            add_step(len(clause_db)+1, "⊥ (Empty Clause)", "Contradiction", 
                                     [clause_1_obj['id'], clause_2_obj['id']], subst_str)
                            return "ВЫВОДИТСЯ", steps_data
                        
                        new_id = add_clause_to_db(res_lits, "Resolve", 
                                                  [clause_1_obj['id'], clause_2_obj['id']], subst_str)
                        
                        if new_id != -1:
                            new_clauses_indices.append(new_id - 1)

            if not new_clauses_indices:
                break

        return "НЕ ВЫВОДИТСЯ", steps_data

    except Exception as e:
        import traceback
        return "ERROR", [{"id": 0, "clause": "Error", "info": str(e), "parents": [], "substitution": ""}]


def resolve_clauses(c1: List[Literal], c2: List[Literal]) -> List[Tuple[List[Literal], str]]:
    """
    Пытается резольвировать два клоза.
    Возвращает список пар (список_литер_резольвенты, описание_подстановки).
    """
    results = []
    
    # 1. Переименование переменных во втором клозе (Standardizing Apart)
    # Используем случайный суффикс или счетчик, чтобы избежать коллизий
    # Для простоты добавим суффикс '_r' (в реальной системе нужен уникальный ID)
    # Здесь мы используем простую эвристику: надеемся, что Unifier справится,
    # но правильно — переименовать ВСЕ переменные в c2.
    
    # Сделаем "свежее" переименование для c2
    import random
    suffix = f"_{random.randint(1000, 9999)}"
    
    def rename_vars(lits, suf):
        mapping = {}
        # Собираем переменные (очень упрощенно: термы без аргументов)
        # В идеале нужен полный обход дерева термов
        vars_found = set()
        def visit(t: Term):
            if not t.args and t.name[0].islower():
                vars_found.add(t.name)
            for a in t.args: visit(a)
            
        for l in lits:
            for a in l.args: visit(a)
            
        for v in vars_found:
            mapping[v] = Term(f"{v}{suf}")
        
        return [l.substitute(mapping) for l in lits]

    c2_renamed = rename_vars(c2, suffix)

    # 2. Поиск контрарных пар
    for i, l1 in enumerate(c1):
        for j, l2 in enumerate(c2_renamed):
            # Проверяем: имена совпадают, знаки разные
            if l1.name == l2.name and l1.negated != l2.negated:
                # Пытаемся унифицировать атомы (без знака)
                res = Unifier.unify_atoms(l1.to_atom(), l2.to_atom())
                
                if res.success:
                    # Формируем подстановку для вывода
                    subst_desc = "{" + ", ".join(f"{k}/{v}" for k,v in res.substitution.items()) + "}"
                    
                    # Собираем новый клоз: (C1 \ l1) U (C2 \ l2)
                    new_lits = []
                    # Из первого клоза (кроме i)
                    for k, lit in enumerate(c1):
                        if k != i:
                            new_lits.append(lit.substitute(res.substitution))
                    # Из второго клоза (кроме j)
                    for k, lit in enumerate(c2_renamed):
                        if k != j:
                            new_lits.append(lit.substitute(res.substitution))
                    
                    # Факторизация (удаление дублей внутри клоза)
                    unique_lits = []
                    seen_strs = set()
                    for l in new_lits:
                        s = str(l)
                        if s not in seen_strs:
                            seen_strs.add(s)
                            unique_lits.append(l)
                            
                    results.append((unique_lits, subst_desc))
                    
    return results

# =========================================================
# ПРИМЕР ЗАПУСКА
# =========================================================
if __name__ == "__main__":
    p = [
        "∀x (Human(x) → Mortal(x))", 
        "Human(Socrates)"
    ]
    g = "Mortal(Socrates)"
    
    res, txt = run_resolution(p, g)
    print(f"RESULT: {res}")
    print("STEPS:")
    print(txt)