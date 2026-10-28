# Password Strength Analysis System

**Objective:** Evaluate password strength and identify common weaknesses to improve password security.

## 1. What it does
You type a password. The program gives back:
- A **score** (0–100) and a **label**: Very Weak / Weak / Medium / Strong / Very Strong
- A **list of weaknesses found** (e.g. "too short", "is a common password")
- **Suggestions** to fix each weakness

## 2. Language and tools
- **Python 3** only, with no external libraries.
- Runs in the terminal. A tiny web page (Flask) or Tkinter GUI can be added later.

## 3. Project structure
```
passwordStrengthAnalysis/
├── main.py                    # asks for a password, prints the report
├── scripts/
│   └── analyzer.py            # all the checking logic
├── database/
│   └── common_passwords.txt   # 1500 common passwords (500 with special chars)
├── tests/
│   └── test_analyzer.py       # unit tests (unittest)
└── docs/
    └── design_plan.md
```

## 4. How the analysis works
Each check adds or removes points from a score that starts at 0.

| # | Check | Rule | Points |
|---|-------|------|--------|
| 1 | Length | 8+ chars: +20, 12+ chars: +30, under 8: +0 | up to 30 |
| 2 | Lowercase letters | present | +10 |
| 3 | Uppercase letters | present | +10 |
| 4 | Digits | present | +10 |
| 5 | Symbols (!@#$…) | present | +15 |
| 6 | Variety bonus | 3+ character types used | +5 |

**Penalties (common weaknesses):**

| Weakness | How to detect | Penalty |
|----------|---------------|---------|
| Common password | found in `database/common_passwords.txt` (case-insensitive) | −40 |
| Repeated characters | `aaa`, `1111` (3+ in a row) | −10 |
| Sequences | `abc`, `123`, `qwerty` | −10 |
| Only one character type | e.g. only letters, only digits or only symbols | −10 |
| Contains year or date | `19xx`, `20xx` | −5 |
| Leetspeak of common word | `dr@g0n` → `dragon` (only if not already listed as common) | −30 |

Score is clamped between 0 and 100.

## 5. Score → label
| Score | Label |
|-------|-------|
| 0–29 | Very Weak |
| 30–49 | Weak |
| 50–69 | Medium |
| 70–84 | Strong |
| 85–100 | Very Strong |

## 6. Core design (easy to read)
`scripts/analyzer.py` has one main function that does everything and returns a dictionary, plus `get_label(score)`:
```python
def analyze(password):
    # returns {"score": 72, "label": "Strong",
    #          "weaknesses": [...], "suggestions": [...]}
```
Inside, `analyze()` goes through the checks one after another, adding points and collecting weaknesses. Two small helpers keep it readable: `has_sequence()` and `is_leetspeak_of_common()`.

## 7. Example output
```
Password: Summer2020
Score: 50/100  → Medium
Weaknesses:
  - No symbols
  - Contains a year
Suggestions:
  - Add a symbol like ! or @
  - Avoid years and dates
```

## 8. Build steps
1. ✅ Create `database/common_passwords.txt`.
2. ✅ Write the tests in `tests/test_analyzer.py`.
3. ✅ Write `scripts/analyzer.py`: `analyze()` and `get_label()` with all checks, scoring and labels.
4. ✅ Write `main.py` using `getpass` so the password isn't shown on screen.
5. Optional: add a web or GUI front end, or a feature to analyze a file of passwords.

**Run:** `python3 main.py`  
**Test:** `python3 -m unittest tests.test_analyzer -v`

## 9. Safety notes
- Never save or log the passwords entered.
- Everything runs locally, with no network calls.

## 10. Optional upgrades later
- Entropy calculation (bits)
- Estimated time to crack
- Password generator for strong suggestions
- Check against the HaveIBeenPwned k-anonymity API
