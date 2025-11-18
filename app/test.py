from utilities.FolConvertion import FolConverterEn
TEST_CASES = [
    # ==========================================
    # ГРУППА 1: SV (Subject - Verb)
    # ==========================================
    {
        "text": "Every student sleeps.",
        "pattern": "SV",
        "desc": "Базовый случай: Явный универсальный квантор",
        "expected_logic": "∀x (Student(x) → Sleep(x))"
    },
    {
        "text": "A cat runs.",
        "pattern": "SV",
        "desc": "Базовый случай: Явный экзистенциальный квантор",
        "expected_logic": "∃x (Cat(x) ∧ Run(x))"
    },
    {
        "text": "Birds fly.",
        "pattern": "SV",
        "desc": "Неявный квантор: Множественное число (Plural -> ∀)",
        "expected_logic": "∀x (Bird(x) → Fly(x))"
    },
    {
        "text": "The sun shines.",
        "pattern": "SV",
        "desc": "Неявный квантор: Единственное число/Det (Singular -> ∃)",
        "expected_logic": "∃x (Sun(x) ∧ Shine(x))"
    },
    {
        "text": "A student does not sleep.",
        "pattern": "SV",
        "desc": "Отрицание глагола (Verb Negation)",
        "expected_logic": "∃x (Student(x) ∧ ¬Sleep(x))"
    },
    {
        "text": "No student sleeps.",
        "pattern": "SV",
        "desc": "Отрицательный квантор (Subject Negation -> 'No' is ∀ + ¬Pred)",
        "expected_logic": "∀x (Student(x) → ¬Sleep(x))"
    },
    {
        "text": "No bird does not fly.",
        "pattern": "SV",
        "desc": "Двойное отрицание (Subj Neg + Verb Neg -> Positive Pred)",
        "expected_logic": "∀x (Bird(x) → Fly(x))"
    },

    # ==========================================
    # ГРУППА 2: SVC (Subject - Copula - Complement)
    # ==========================================
    {
        "text": "Every human is mortal.",
        "pattern": "SVC",
        "desc": "SVC: Явный универсальный (∀)",
        "expected_logic": "∀x (Human(x) → Mortal(x))"
    },
    {
        "text": "Some apples are red.",
        "pattern": "SVC",
        "desc": "SVC: Явный экзистенциальный (∃)",
        "expected_logic": "∃x (Apple(x) ∧ Red(x))"
    },
    {
        "text": "The sky is not green.",
        "pattern": "SVC",
        "desc": "SVC: Отрицание связки (Verb Negation)",
        "expected_logic": "∃x (Sky(x) ∧ ¬Green(x))"
    },
    {
        "text": "No king is eternal.",
        "pattern": "SVC",
        "desc": "SVC: Отрицание субъекта (Subject Negation)",
        "expected_logic": "∀x (King(x) → ¬Eternal(x))"
    },
    {
        "text": "Sugar is sweet.",
        "pattern": "SVC",
        "desc": "SVC: Неявный квантор (Mass noun -> ∃/Singular)",
        "expected_logic": "∃x (Sugar(x) ∧ Sweet(x))"
    },

    # ==========================================
    # ГРУППА 3: SVO (Subject - Verb - Object)
    # ==========================================
    {
        "text": "Every student reads a book.",
        "pattern": "SVO",
        "desc": "SVO: ∀ субъект, ∃ объект (Классика)",
        "expected_logic": "∀x (Student(x) → ∃y (Book(y) ∧ Read(x, y)))"
    },
    {
        "text": "Some cats eat mice.",
        "pattern": "SVO",
        "desc": "SVO: ∃ субъект, ∀ объект (Mice is plural implicit)",
        "expected_logic": "∃x (Cat(x) ∧ ∀y (Mouse(y) → Eat(x, y)))"
    },
    {
        "text": "John does not like pizza.",
        "pattern": "SVO",
        "desc": "SVO: Отрицание глагола",
        "expected_logic": "∃x (John(x) ∧ ∃y (Pizza(y) ∧ ¬Like(x, y)))"
    },
    {
        "text": "No teacher helps a student.",
        "pattern": "SVO",
        "desc": "SVO: Отрицание субъекта",
        "expected_logic": "∀x (Teacher(x) → ∃y (Student(y) ∧ ¬Help(x, y)))"
    },
    {
        "text": "I see no evil.",
        "pattern": "SVO",
        "desc": "SVO: Отрицание объекта (Object Negation -> ∀ + ¬Pred)",
        "expected_logic": "∃x (I(x) ∧ ∀y (Evil(y) → ¬See(x, y)))"
    },
    {
        "text": "No one trusts no one.",
        "pattern": "SVO",
        "desc": "SVO: Двойное отрицание (Subj + Obj -> Positive Pred)",
        # Примечание: "No one" парсится как "No" (det) + "one" (noun)
        "expected_logic": "∀x (One(x) → ∀y (One(y) → Trust(x, y)))"
    }
]

if __name__ == "__main__":
    converter_en = FolConverterEn()
    for s in TEST_CASES:
        print("Sentence:", s['text'])
        print("Pattern:", converter_en.get_pattern(s["text"]))
        print("FOL:", converter_en.convert_to_fol(s["text"]))
        print("FOL (expected):", s["expected_logic"])
        print("-" * 40)