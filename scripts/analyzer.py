import os
import re

COMMON_FILE = os.path.join(os.path.dirname(__file__), "..", "database", "common_passwords.txt")

with open(COMMON_FILE, encoding="utf-8") as f:
    COMMON = {line.strip().lower() for line in f if line.strip()}

KEYBOARD_ROWS = ["qwertyuiop", "asdfghjkl", "zxcvbnm", "1234567890"]
LEET = str.maketrans({"@": "a", "4": "a", "3": "e", "1": "i", "!": "i",
                      "0": "o", "$": "s", "5": "s", "7": "t"})


def get_label(score):
    if score < 30:
        return "Very Weak"
    if score < 50:
        return "Weak"
    if score < 70:
        return "Medium"
    if score < 85:
        return "Strong"
    return "Very Strong"


def has_sequence(password):
    """True if there are 3 characters in a row like abc, 321 or qwe."""
    p = password.lower()
    for i in range(len(p) - 2):
        a, b, c = p[i:i + 3]
        if a.isalnum() and b.isalnum() and c.isalnum():
            step = ord(b) - ord(a)
            if step in (1, -1) and ord(c) - ord(b) == step:
                return True
        for row in KEYBOARD_ROWS:
            if p[i:i + 3] in row or p[i:i + 3] in row[::-1]:
                return True
    return False


def is_leetspeak_of_common(password):
    """True for things like 'dr@g0n' that become a common password once decoded."""
    decoded = password.lower().translate(LEET)
    stripped = decoded.rstrip("0123456789!@#$%^&*")
    return decoded in COMMON or (stripped != "" and stripped in COMMON)


def analyze(password):
    score = 0
    found = []  # (weakness, suggestion) pairs

    # --- points for good things ---
    if len(password) >= 12:
        score += 30
    elif len(password) >= 8:
        score += 20
    else:
        found.append(("Too short (under 8 characters)", "Use at least 12 characters"))

    types = {
        "lowercase letters": (any(c.islower() for c in password), 10, "Add lowercase letters"),
        "uppercase letters": (any(c.isupper() for c in password), 10, "Add uppercase letters"),
        "digits": (any(c.isdigit() for c in password), 10, "Add a digit"),
        "symbols": (any(not c.isalnum() for c in password), 15, "Add a symbol like ! or @"),
    }
    used = 0
    for name, (present, points, tip) in types.items():
        if present:
            score += points
            used += 1
        else:
            found.append((f"No {name}", tip))
    if used >= 3:
        score += 5

    # --- penalties for common weaknesses ---
    if password.lower() in COMMON:
        score -= 40
        found.append(("Is a very common password", "Pick something unique, not on common lists"))
    elif is_leetspeak_of_common(password):
        score -= 30
        found.append(("Predictable word with leetspeak swaps (like @ for a)",
                      "Swapping letters for symbols doesn't fool attackers; use a different word"))

    if re.search(r"(.)\1\1", password):
        score -= 10
        found.append(("Repeated characters (like aaa)", "Avoid the same character 3+ times in a row"))

    if has_sequence(password):
        score -= 10
        found.append(("Contains a sequence (like abc, 123 or qwe)", "Avoid sequences and keyboard patterns"))

    if used == 1:
        score -= 10
        found.append(("Uses only one type of character", "Mix letters, digits and symbols"))

    if re.search(r"(?<!\d)(19|20)\d{2}(?!\d)", password):
        score -= 5
        found.append(("Contains a year", "Avoid years and dates"))

    score = max(0, min(100, score))
    return {
        "score": score,
        "label": get_label(score),
        "weaknesses": [w for w, _ in found],
        "suggestions": [s for _, s in found],
    }
