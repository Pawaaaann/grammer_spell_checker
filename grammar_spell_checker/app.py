"""
Project: grammar_spell_checker
Purpose: Simple grammar and spell checker using language_tool_python.

Installation (Windows/macOS/Linux):
1) Create and activate a virtual environment (recommended)
   - Windows (PowerShell):
       python -m venv .venv
       .venv\\Scripts\\Activate.ps1
   - macOS/Linux (bash):
       python3 -m venv .venv
       source .venv/bin/activate

2) Install dependency:
   pip install language-tool-python

Optional alternative (TextBlob):
   pip install textblob
   python -m textblob.download_corpora  # Only needed once

Usage examples:
   - Check inline text:
       python app.py --text "This are bad sentence with errrors."
   - Check a file:
       python app.py --file sample.txt
   - Interactive mode (no args):
       python app.py

Notes:
- language_tool_python uses LanguageTool rules for grammar/spelling/style.
- The script prints detected issues and a suggested fully corrected text.
"""

import argparse
import sys
from pathlib import Path
import tkinter as tk
from tkinter import messagebox
import re

try:
    import language_tool_python
except ImportError as e:
    print(
        "Missing dependency: language-tool-python.\n"
        "Install it with: pip install language-tool-python",
        file=sys.stderr,
    )
    raise

try:
    from textblob import TextBlob
except ImportError:
    TextBlob = None


def check_text(text: str, lang: str = "en-US") -> None:
    tool = language_tool_python.LanguageTool(lang)
    matches = tool.check(text)

    if not matches:
        print("No issues found.")
        return

    print(f"Found {len(matches)} issue(s):\n")
    for i, m in enumerate(matches, 1):
        context = m.context if m.context else ""
        replacements = ", ".join(m.replacements[:5]) if m.replacements else "(none)"
        print(
            f"{i}. {m.ruleId}: {m.message}\n"
            f"   Offset: {m.offset}-{m.offset + m.errorLength}\n"
            f"   Context: {context}\n"
            f"   Suggestion(s): {replacements}\n"
        )

    corrected = language_tool_python.utils.correct(text, matches)
    print("Corrected text:\n")
    print(corrected)


def correct_spelling(text: str) -> str:
    """Return a spelling-corrected version of the given text using TextBlob.

    Requires the 'textblob' package and its corpora. If missing, raises
    ImportError with installation guidance.
    """
    if TextBlob is None:
        raise ImportError(
            "Missing dependency: textblob. Install with: 'pip install textblob' "
            "and download corpora with: 'python -m textblob.download_corpora'"
        )
    return str(TextBlob(text).correct())


def _count_word_changes(original: str, new_text: str) -> int:
    a = re.findall(r"[A-Za-z']+", original)
    b = re.findall(r"[A-Za-z']+", new_text)
    n = min(len(a), len(b))
    diffs = sum(1 for i in range(n) if a[i] != b[i])
    diffs += abs(len(a) - len(b))
    return diffs


def check_grammar(text: str) -> str:
    """Detect and correct grammar/style issues using LanguageTool('en-US').

    Returns the corrected text after applying all suggestions.
    """
    tool = language_tool_python.LanguageTool('en-US')
    matches = tool.check(text)
    return language_tool_python.utils.correct(text, matches)


def check_grammar_with_count(text: str) -> tuple[str, int]:
    tool = language_tool_python.LanguageTool('en-US')
    matches = tool.check(text)
    corrected = language_tool_python.utils.correct(text, matches)
    return corrected, len(matches)


def fix_text(text: str) -> str:
    """Fix text by first correcting spelling (TextBlob) then grammar (LanguageTool).

    Prints both the original and the final corrected text. Returns the corrected text.
    """
    original = text
    spelled = correct_spelling(original)
    corrected, _ = check_grammar_with_count(spelled)
    print("Original:\n")
    print(original)
    print("\nCorrected:\n")
    print(corrected)
    return corrected


def read_text_from_file(path: Path) -> str:
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")
    return path.read_text(encoding="utf-8")


def interactive_loop() -> None:
    print("Enter/paste text. Press Enter on an empty line to finish.\n")
    lines = []
    try:
        while True:
            line = input()
            if line.strip() == "":
                break
            lines.append(line)
    except (EOFError, KeyboardInterrupt):
        pass

    text = "\n".join(lines).strip()
    if not text:
        print("No input provided.")
        return
    check_text(text)


def simple_cli() -> None:
    """Prompt for a single line of text, run fix_text, and show corrected output."""
    try:
        user_text = input("Enter your text: ")
    except (EOFError, KeyboardInterrupt):
        return
    if not user_text.strip():
        print("No input provided.")
        return
    fixed = fix_text(user_text)
    print(f"Corrected: {fixed}")


def run_gui() -> None:
    root = tk.Tk()
    root.title("Grammar & Spell Checker")

    frame = tk.Frame(root, padx=10, pady=10)
    frame.pack(fill=tk.BOTH, expand=True)

    input_label = tk.Label(frame, text="Input")
    input_label.pack(anchor="w")

    input_box = tk.Text(frame, height=10, wrap=tk.WORD)
    input_box.pack(fill=tk.BOTH, expand=True)

    output_label = tk.Label(frame, text="Corrected")
    output_label.pack(anchor="w", pady=(10, 0))

    output_box = tk.Text(frame, height=10, wrap=tk.WORD)
    output_box.pack(fill=tk.BOTH, expand=True)

    stats_label = tk.Label(frame, text="Spelling fixes: 0 | Grammar fixes: 0")
    stats_label.pack(anchor="w", pady=(6, 0))

    def on_check():
        text = input_box.get("1.0", "end-1c")
        if not text.strip():
            messagebox.showinfo("Info", "Please enter some text.")
            return
        try:
            spelled = correct_spelling(text)
            spelling_changes = _count_word_changes(text, spelled)
            corrected, grammar_changes = check_grammar_with_count(spelled)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return
        output_box.delete("1.0", tk.END)
        output_box.insert("1.0", corrected)
        stats_label.config(text=f"Spelling fixes: {spelling_changes} | Grammar fixes: {grammar_changes}")

    check_btn = tk.Button(frame, text="Check", command=on_check)
    check_btn.pack(pady=10)

    def on_copy():
        corrected_text = output_box.get("1.0", "end-1c")
        if not corrected_text:
            messagebox.showinfo("Info", "Nothing to copy.")
            return
        try:
            root.clipboard_clear()
            root.clipboard_append(corrected_text)
            root.update()  # keep on clipboard after window closes
            messagebox.showinfo("Copied", "Corrected text copied to clipboard.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    copy_btn = tk.Button(frame, text="Copy corrected text", command=on_copy)
    copy_btn.pack(pady=(0, 10))

    root.mainloop()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Grammar and spell checker using language_tool_python",
    )
    parser.add_argument("--text", type=str, help="Inline text to check")
    parser.add_argument("--file", type=str, help="Path to a text file to check")
    parser.add_argument("--lang", type=str, default="en-US", help="Language code, e.g., en-US, en-GB, de-DE")
    parser.add_argument("--gui", action="store_true", help="Launch Tkinter GUI")
    parser.add_argument("--fix", type=str, help="Run combined spelling+grammar fix on provided text")

    args = parser.parse_args()

    if args.text and args.file:
        print("Please provide either --text or --file, not both.", file=sys.stderr)
        sys.exit(2)

    if args.fix:
        print(fix_text(args.fix))
        return

    if args.text:
        check_text(args.text, args.lang)
        return

    if args.file:
        text = read_text_from_file(Path(args.file))
        check_text(text, args.lang)
        return

    if args.gui:
        run_gui()
        return

    simple_cli()


if __name__ == "__main__":
    main()
