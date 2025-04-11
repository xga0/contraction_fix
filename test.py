from contraction_fix import ContractionFixer

# Create a custom fixer instance
fixer = ContractionFixer(use_informal=True, use_slang=False)

# Fix text
text = "I'd like to see y'all tomorrow"
fixed_text = fixer.fix(text)
print("Original text:", text)
print("Fixed text:", fixed_text)

# Preview contractions
matches = fixer.preview(text, context_size=5)
for match in matches:
    print(f"Found '{match.text}' at position {match.start}")
    print(f"Context: '{match.context}'")
    print(f"Will be replaced with: '{match.replacement}'")