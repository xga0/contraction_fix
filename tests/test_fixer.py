import unittest
from contraction_fix.fixer import ContractionFixer, Match

class TestContractionFixer(unittest.TestCase):
    def setUp(self):
        self.fixer = ContractionFixer()

    def test_standard_contractions(self):
        test_cases = [
            ("I can't do it", "I cannot do it"),
            ("It's a test", "It is a test"),
            ("They're coming", "They are coming"),
            ("We'll see", "We will see"),
            ("You'd better", "You would better"),
            ("I'd like to see y'all", "I would like to see you all")  # Added test for I'd
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                self.assertEqual(self.fixer.fix(input_text), expected)

    def test_informal_contractions(self):
        test_cases = [
            ("goin' home", "going home"),
            ("doin' well", "doing well"),
            ("nothin' special", "nothing special")
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                self.assertEqual(self.fixer.fix(input_text), expected)

    def test_internet_slang(self):
        test_cases = [
            ("btw it's cool", "by the way it is cool"),
            ("idk what to do", "I do not know what to do"),
            ("tbh it's fine", "to be honest it is fine")
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                self.assertEqual(self.fixer.fix(input_text), expected)

    def test_preview(self):
        text = "I can't believe it's not butter!"
        matches = self.fixer.preview(text)
        
        self.assertEqual(len(matches), 2)
        self.assertIsInstance(matches[0], Match)
        self.assertEqual(matches[0].text, "can't")
        self.assertEqual(matches[0].replacement, "cannot")
        self.assertEqual(matches[1].text, "it's")
        self.assertEqual(matches[1].replacement, "it is")
        
        # Test context size
        matches = self.fixer.preview(text, context_size=3)
        self.assertTrue(len(matches[0].context) <= matches[0].text.length + 6)  # text length + 2*context_size

    def test_possessive_vs_contraction(self):
        test_cases = [
            # Contractions
            ("it's a nice day", "it is a nice day"),
            ("that's interesting", "that is interesting"),
            ("what's happening", "what is happening"),
            ("there's a problem", "there is a problem"),
            ("today's weather is nice", "today is weather is nice"),
            
            # Possessives (should remain unchanged)
            ("John's car", "John's car"),
            ("the dog's bone", "the dog's bone"),
            ("my mother's house", "my mother's house"),
            ("the company's policy", "the company's policy"),
            ("James's book", "James's book"),
            ("the boss's office", "the boss's office"),
            ("the class's schedule", "the class's schedule"),
            
            # Mixed cases
            ("It's John's car and that's final", "It is John's car and that is final"),
            ("The company's CEO says it's time", "The company's CEO says it is time"),
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                self.assertEqual(self.fixer.fix(input_text), expected)

    def test_case_preservation(self):
        test_cases = [
            ("I'M GOING HOME", "I AM GOING HOME"),
            ("They're RUNNING", "They are RUNNING"),
            ("IT'S time", "IT IS time"),
            ("DON'T STOP", "DO NOT STOP")
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                self.assertEqual(self.fixer.fix(input_text), expected)

    def test_alternate_apostrophes(self):
        test_cases = [
            ("I'd like to", "I would like to"),    # Standard apostrophe
            ("I'd like to", "I would like to"),    # Curly apostrophe
            ("don't do it", "do not do it"),       # Standard apostrophe
            ("don't do it", "do not do it")        # Curly apostrophe
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                # Replace standard with curly apostrophe in second test
                if "'" in input_text:
                    curly_input = input_text.replace("'", "'")
                    self.assertEqual(self.fixer.fix(curly_input), expected)
                self.assertEqual(self.fixer.fix(input_text), expected)

    def test_add_remove_contraction(self):
        # Test adding new contraction
        self.fixer.add_contraction("gonna", "going to")
        self.assertEqual(self.fixer.fix("I'm gonna do it"), "I am going to do it")
        
        # Test removing contraction
        self.fixer.remove_contraction("gonna")
        self.assertEqual(self.fixer.fix("I'm gonna do it"), "I am gonna do it")
        
        # Test thread safety by adding and removing in sequence
        self.fixer.add_contraction("wanna", "want to")
        self.fixer.remove_contraction("wanna")
        self.assertEqual(self.fixer.fix("I wanna go"), "I wanna go")

if __name__ == '__main__':
    unittest.main() 