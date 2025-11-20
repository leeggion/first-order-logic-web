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
    },
    
    # ==========================================
    # ГРУППА 4: SVA (Subject - Verb - Adverbial)
    # ==========================================
    {
        "text": "Dogs run quickly.",
        "pattern": "SVA",
        "desc": "Базовый случай: advmod как обстоятельство",
        "expected_logic": "∀x (Dog(x) → ∀y (Quickly(y) → Run(x, y)))"
    },
    {
        "text": "A student reads silently.",
        "pattern": "SVA",
        "desc": "Экзистенциальный субъект + advmod",
        "expected_logic": "∃x (Student(x) ∧ ∃y (Silently(y) → Read(x, y)))"
    },
    {
        "text": "The boy runs in the park.",
        "pattern": "SVA",
        "desc": "Обстоятельство через obl (prep phrase → noun)",
        "expected_logic": "∃x (Boy(x) ∧ ∃y (Park(y) → Run(x, y)))"
    },
    {
        "text": "Cats sleep this morning.",
        "pattern": "SVA",
        "desc": "npadvmod: именная группа как обстоятельство",
        "expected_logic": "∀x (Cat(x) → ∃y (Morning(y) → Sleep(x, y)))"
    },
    {
        "text": "dogs do not run quickly.",
        "pattern": "SVA",
        "desc": "Отрицание глагола",
        "expected_logic": "∀x (Dog(x) → ∀y (Quickly(y) → ¬Run(x, y)))"
    },
    {
        "text": "No dogs run quickly.",
        "pattern": "SVA",
        "desc": "Отрицательный субъект ('No' = ∀ + ¬Pred)",
        "expected_logic": "∀x (Dog(x) → ∀y (Quickly(y) → ¬Run(x, y)))"
    },
    {
        "text": "dogs run not quickly.",
        "pattern": "SVA",
        "desc": "Отрицание обстоятельства (neg на advmod)",
        "expected_logic": "∀x (Dog(x) → ∀y (Quickly(y) → ¬Run(x, y)))"
    },
    {
        "text": "No dogs do not run quickly.",
        "pattern": "SVA",
        "desc": "Двойное отрицание (SubjNeg XOR VerbNeg → Positive)",
        "expected_logic": "∀x (Dog(x) → ∀y (Quickly(y) → Run(x, y)))"
    },
    {
        "text": "A woman walks outside.",
        "pattern": "SVA",
        "desc": "Простое obl обстоятельство",
        "expected_logic": "∃x (Woman(x) ∧ ∃y (Outside(y) → Walk(x, y)))"
    },
    {
        "text": "Every child plays here.",
        "pattern": "SVA",
        "desc": "advmod 'here' как обстоятельство",
        "expected_logic": "∀x (Child(x) → ∃y (Here(y) → Play(x, y)))"
    },
    
    # ==========================================
    # ГРУППА 5: SVIODO (Subject - Verb - Indirect Object - Direct Object)
    # ==========================================

    {
        "text": "John gave Mary a book.",
        "pattern": "SVIODO",
        "desc": "Базовый случай: явный iobj + dobj",
        "expected_logic": "∃x (John(x) → ∃y (Mary(y) → ∃z (Book(z) → Give(x, y, z))))"
    },

    {
        "text": "John gave a book to Mary.",
        "pattern": "SVIODO",
        "desc": "iobj через prep→pobj (to Mary)",
        "expected_logic": "∃x (John(x) → ∃y (Mary(y) → ∃z (Book(z) → Give(x, y, z))))"
    },

    {
        "text": "Every teacher sent the students a message.",
        "pattern": "SVIODO",
        "desc": "∀ субъект, ∀ косвенный объект (plural), ∃ прямой объект",
        "expected_logic": "∀x (Teacher(x) → ∀y (Student(y) → ∃z (Message(z) → Send(x, y, z))))"
    },

    {
        "text": "The manager gave employees instructions.",
        "pattern": "SVIODO",
        "desc": "Implicit ∃ subject, ∀ iobj (plural), ∀ dobj (plural)",
        "expected_logic": "∃x (Manager(x) ∧ ∀y (Employee(y) → ∀z (Instruction(z) → Give(x, y, z))))"
    },

    {
        "text": "A woman showed the boy a picture.",
        "pattern": "SVIODO",
        "desc": "Смешанные кванторы: ∃ subj, ∃ iobj (the boy → ∃), ∃ dobj",
        "expected_logic": "∃x (Woman(x) ∧ ∃y (Boy(y) → ∃z (Picture(z) → Show(x, y, z))))"
    },

    {
        "text": "Some men told a child a story.",
        "pattern": "SVIODO",
        "desc": "∃ subject, ∃ iobj, ∃ dobj",
        "expected_logic": "∃x (Man(x) ∧ ∃y (Child(y) → ∃z (Story(z) → Tell(x, y, z))))"
    },

    {
        "text": "No student gave a teacher a book.",
        "pattern": "SVIODO",
        "desc": "Отрицательный субъект → ∀ + ¬Pred",
        "expected_logic": "∀x (Student(x) → ∃y (Teacher(y) → ∃z (Book(z) → ¬Give(x, y, z))))"
    },

    {
        "text": "A student did not give a boy a pen.",
        "pattern": "SVIODO",
        "desc": "Отрицание глагола",
        "expected_logic": "∃x (Student(x) ∧ ∃y (Boy(y) → ∃z (Pen(z) → ¬Give(x, y, z))))"
    },

    {
        "text": "No student did not give a boy a pen.",
        "pattern": "SVIODO",
        "desc": "Двойное отрицание (SubjNeg XOR VerbNeg → Positive)",
        "expected_logic": "∀x (Student(x) → ∃y (Boy(y) → ∃z (Pen(z) → Give(x, y, z))))"
    },

    {
        "text": "Parents give children gifts.",
        "pattern": "SVIODO",
        "desc": "Plural subject → ∀, plural iobj → ∀, plural dobj → ∀",
        "expected_logic": "∀x (Parent(x) → ∀y (Child(y) → ∀z (Gift(z) → Give(x, y, z))))"
    },

    {
        "text": "The teacher handed the girl the paper.",
        "pattern": "SVIODO",
        "desc": "Классический порядок iobj → dobj",
        "expected_logic": "∃x (Teacher(x) ∧ ∃y (Girl(y) → ∃z (Paper(z) → Hand(x, y, z))))"
    },

    {
        "text": "The teacher handed the paper to the girl.",
        "pattern": "SVIODO",
        "desc": "Форма c prep→pobj",
        "expected_logic": "∃x (Teacher(x) ∧ ∃y (Girl(y) → ∃z (Paper(z) → Hand(x, y, z))))"
    },

    {
        "text": "Every man taught the child a lesson.",
        "pattern": "SVIODO",
        "desc": "∀ subj, ∃ iobj, ∃ dobj",
        "expected_logic": "∀x (Man(x) → ∃y (Child(y) → ∃z (Lesson(z) → Teach(x, y, z))))"
    },

    {
        "text": "A scientist wrote students a long letter.",
        "pattern": "SVIODO",
        "desc": "Прилагательное у объекта не мешает",
        "expected_logic": "∃x (Scientist(x) ∧ ∀y (Student(y) → ∃z (Letter(z) → Write(x, y, z))))"
    },

    {
        "text": "No doctors gave patients medicine.",
        "pattern": "SVIODO",
        "desc": "Plural subject with negation → ∀ + ¬",
        "expected_logic": "∀x (Doctor(x) → ∀y (Patient(y) → ∀z (Medicine(z) → ¬Give(x, y, z))))"
    }
]

if __name__ == "__main__":
    converter_en = FolConverterEn()
    # print(converter_en.convert_to_fol("Dogs run not quickly."))
    for s in TEST_CASES:
        print("Sentence:", s['text'])
        print("Pattern:", converter_en.get_pattern(s["text"]))
        print("FOL:", converter_en.convert_to_fol(s["text"]))
        print("FOL (expected):", s["expected_logic"])
        print("-" * 40)