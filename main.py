import getpass
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "scripts"))

from analyzer import analyze


def print_report(result):
    print(f"\nScore: {result['score']}/100  ->  {result['label']}")
    if result["weaknesses"]:
        print("Weaknesses:")
        for w in result["weaknesses"]:
            print(f"  - {w}")
        print("Suggestions:")
        for s in result["suggestions"]:
            print(f"  - {s}")
    else:
        print("No weaknesses found. Nice password!")
    print()


def main():
    print("Password Strength Analyzer (press Enter on an empty line to quit)")
    while True:
        # getpass hides what you type; nothing is saved or logged
        password = getpass.getpass("Enter a password: ")
        if not password:
            break
        print_report(analyze(password))


if __name__ == "__main__":
    main()
