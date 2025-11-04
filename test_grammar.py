"""
Test script to show what LanguageTool can and cannot detect.
Run: python test_grammar.py
"""

import language_tool_python
from textblob import TextBlob

def test_sentence(text):
    """Test a sentence and show results."""
    print(f"\n{'='*60}")
    print(f"ORIGINAL: {text}")
    print(f"{'='*60}")
    
    # Step 1: Spelling correction with TextBlob
    spelled = str(TextBlob(text).correct())
    if spelled != text:
        print(f"✓ SPELLING: {spelled}")
    else:
        print(f"✓ SPELLING: No changes")
    
    # Step 2: Grammar check with LanguageTool
    tool = language_tool_python.LanguageTool('en-US')
    matches = tool.check(spelled)
    
    if matches:
        print(f"\n📝 GRAMMAR ISSUES FOUND: {len(matches)}")
        for i, m in enumerate(matches, 1):
            print(f"\n  {i}. {m.message}")
            if m.replacements:
                print(f"     Suggestions: {', '.join(m.replacements[:3])}")
            print(f"     Error text: '{spelled[m.offset:m.offset+m.errorLength]}'")
        
        corrected = language_tool_python.utils.correct(spelled, matches)
        print(f"\n✅ FINAL: {corrected}")
    else:
        print(f"\n✅ GRAMMAR: No issues found")
        print(f"✅ FINAL: {spelled}")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("GRAMMAR CHECKER TEST - What it CAN and CANNOT detect")
    print("="*60)
    
    # Test cases
    test_cases = [
        # What it CAN detect
        "I has a pen",                          # Subject-verb agreement
        "She go to school yesterday",           # Verb tense
        "This are bad sentence",                # Subject-verb agreement
        "tommorrow was a holiday",              # Spelling
        "I has three appls",                    # Spelling + grammar
        "He dont like it",                      # Missing apostrophe
        "Their going to the store",             # Wrong word (their/they're)
        
        # What it CANNOT detect (grammatically correct but illogical)
        "She is a boy",                         # Logically wrong but grammatically correct
        "The cat barked loudly",                # Semantically wrong
        "I ate the building",                   # Impossible but grammatically correct
        "Tomorrow was a holiday",               # Tense confusion (but grammatically valid)
    ]
    
    for test in test_cases:
        test_sentence(test)
    
    print("\n" + "="*60)
    print("SUMMARY:")
    print("="*60)
    print("✅ CAN DETECT:")
    print("  - Spelling mistakes")
    print("  - Subject-verb agreement errors")
    print("  - Wrong verb tenses")
    print("  - Missing punctuation")
    print("  - Wrong word usage (their/they're, etc.)")
    print("  - Capitalization issues")
    print("\n❌ CANNOT DETECT:")
    print("  - Logical contradictions (she is a boy)")
    print("  - Semantic errors (cat barked)")
    print("  - Context-dependent errors")
    print("  - Factual incorrectness")
    print("\n💡 For better detection, you need AI models like GPT-4")
    print("="*60 + "\n")
