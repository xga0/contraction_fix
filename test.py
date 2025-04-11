# from contraction_fix import fix

# text = "I can't find Sarah's keys, and she won't be at her brother's house until it's dark."
# fixed_text = fix(text)
# print(fixed_text)  # "I cannot believe it is not butter!"

from contraction_fix import ContractionFixer

# Create a custom fixer instance
fixer = ContractionFixer(use_informal=True, use_slang=False)

# Fix text
text = "I'd like to see y'all tomorrow"
fixed_text = fixer.fix(text)
print(fixed_text)  # "I would like to see you all tomorrow"

# Preview contractions
matches = fixer.preview(text, context_size=5)
for match in matches:
    print(f"Found '{match['match']}' at position {match['start']}")
    print(f"Context: '{match['context']}'")
    print(f"Will be replaced with: '{match['replacement']}'")