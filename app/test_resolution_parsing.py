from utilities.Resolution import parse_formula

formulas = [
    "∀x (Man(x) → Mortal(x))",
    "Man(Socrates)",
    "∃y (Person(y) ∧ Happy(y))",
    "∀x (Student(x) → ∃y (Book(y) ∧ Reads(x, y)))"
]

print("Testing parsing...")
for f in formulas:
    try:
        parsed = parse_formula(f)
        print(f"SUCCESS: {ascii(f)} -> {ascii(str(parsed))}")
    except Exception as e:
        print(f"FAILED: {ascii(f)} -> {ascii(str(e))}")
