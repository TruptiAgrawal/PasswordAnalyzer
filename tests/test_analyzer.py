import os
import sys
import unittest

# make scripts/analyzer.py importable when running from the project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from analyzer import analyze, get_label

STRONG = "Xk9#mP2$vLq7!"  # 13 chars, all 4 types, nothing predictable


def has_weakness(result, keyword):
    """True if any weakness message mentions the keyword (case-insensitive)."""
    return any(keyword in w.lower() for w in result["weaknesses"])


class TestResultShape(unittest.TestCase):
    def test_returns_expected_keys(self):
        result = analyze("hello")
        self.assertEqual(set(result), {"score", "label", "weaknesses", "suggestions"})

    def test_score_is_int_in_range(self):
        for pw in ["", "a", "password", STRONG, "A" * 200]:
            score = analyze(pw)["score"]
            self.assertIsInstance(score, int)
            self.assertTrue(0 <= score <= 100, f"{pw!r} gave {score}")

    def test_every_weakness_has_a_suggestion(self):
        result = analyze("aaa111")
        self.assertGreater(len(result["weaknesses"]), 0)
        self.assertEqual(len(result["weaknesses"]), len(result["suggestions"]))


class TestLabels(unittest.TestCase):
    def test_label_boundaries(self):
        cases = {
            0: "Very Weak", 29: "Very Weak",
            30: "Weak", 49: "Weak",
            50: "Medium", 69: "Medium",
            70: "Strong", 84: "Strong",
            85: "Very Strong", 100: "Very Strong",
        }
        for score, label in cases.items():
            self.assertEqual(get_label(score), label, f"score {score}")

    def test_analyze_label_matches_score(self):
        for pw in ["abc", "Summer2020", STRONG]:
            result = analyze(pw)
            self.assertEqual(result["label"], get_label(result["score"]))


class TestScoring(unittest.TestCase):
    def test_empty_password_is_very_weak(self):
        result = analyze("")
        self.assertEqual(result["score"], 0)
        self.assertEqual(result["label"], "Very Weak")

    def test_strong_password_exact_score(self):
        # length 12+ (30) + lower + upper + digit (30) + symbol (15) + variety (5)
        result = analyze(STRONG)
        self.assertEqual(result["score"], 80)
        self.assertEqual(result["label"], "Strong")
        self.assertEqual(result["weaknesses"], [])

    def test_longer_scores_higher(self):
        self.assertGreater(analyze(STRONG)["score"], analyze("Xk9#mP2$")["score"])

    def test_more_character_types_score_higher(self):
        self.assertGreater(analyze("Kq7vLmXz")["score"], analyze("kqvlmxzw")["score"])
        self.assertGreater(analyze("Kq7!vLmX")["score"], analyze("Kq7vLmXz")["score"])

    def test_short_password_gets_no_length_points(self):
        self.assertLess(analyze("Kq7!")["score"], analyze("Kq7!vLmX")["score"])


class TestWeaknesses(unittest.TestCase):
    def test_short_password_flagged(self):
        self.assertTrue(has_weakness(analyze("Kq7!"), "short"))

    def test_common_password_flagged(self):
        result = analyze("password")
        self.assertTrue(has_weakness(result, "common"))
        self.assertLess(result["score"], 30)

    def test_common_check_ignores_case(self):
        self.assertTrue(has_weakness(analyze("PASSWORD"), "common"))

    def test_common_password_with_special_chars(self):
        # these come from the special-character section of common_passwords.txt
        for pw in ["Admin@123", "Krishna@123!@#", "!@#$%^&*"]:
            self.assertTrue(has_weakness(analyze(pw), "common"), pw)

    def test_leetspeak_flagged(self):
        # "dr@g0n" is "dragon" with substitutions
        self.assertTrue(has_weakness(analyze("Dr@g0n"), "leet"))

    def test_repeated_characters_flagged(self):
        self.assertTrue(has_weakness(analyze("Kq7!aaaXvLm"), "repeat"))
        self.assertFalse(has_weakness(analyze("Kq7!aaXvLm"), "repeat"))  # only 2 in a row

    def test_sequences_flagged(self):
        for pw in ["Kq7!abcXvLm", "Kq7!XvLm123", "Kq7!qwertyXv"]:
            self.assertTrue(has_weakness(analyze(pw), "sequence"), pw)

    def test_only_letters_flagged(self):
        self.assertTrue(has_weakness(analyze("kqvlmxzwpt"), "only"))

    def test_only_digits_flagged(self):
        self.assertTrue(has_weakness(analyze("739204851"), "only"))

    def test_year_flagged(self):
        for pw in ["Kq7!vLm1999", "Kq7!vLm2024"]:
            self.assertTrue(has_weakness(analyze(pw), "year"), pw)

    def test_missing_types_flagged(self):
        result = analyze("kqvlmxzwpt")
        self.assertTrue(has_weakness(result, "uppercase"))
        self.assertTrue(has_weakness(result, "digit"))
        self.assertTrue(has_weakness(result, "symbol"))

    def test_strong_password_has_no_weaknesses(self):
        self.assertEqual(analyze(STRONG)["weaknesses"], [])


class TestWeakVsStrong(unittest.TestCase):
    def test_ranking(self):
        passwords = ["123456", "password", "Summer2020", "Kq7!vLmX", STRONG]
        scores = [analyze(p)["score"] for p in passwords]
        self.assertEqual(scores, sorted(scores), dict(zip(passwords, scores)))

    def test_common_passwords_are_never_strong(self):
        for pw in ["Password@123", "Welcome@123", "Qwerty@123"]:
            self.assertLess(analyze(pw)["score"], 70, pw)


if __name__ == "__main__":
    unittest.main()
