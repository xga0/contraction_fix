import unittest
from contraction_fix.core.fixer import ContractionFixer

class TestContractionFixer(unittest.TestCase):
    def setUp(self):
        self.fixer = ContractionFixer()

    def test_standard_contractions(self):
        test_cases = [
            ("I can't do it", "I cannot do it"),
            ("It's a test", "It is a test"),
            ("They're coming", "They are coming"),
            ("We'll see", "We will see"),
            ("You'd better", "You would better")
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
        self.assertEqual(matches[0]["match"], "can't")
        self.assertEqual(matches[1]["match"], "it's")

    def test_add_remove_contraction(self):
        # Test adding new contraction
        self.fixer.add_contraction("gonna", "going to")
        self.assertEqual(self.fixer.fix("I'm gonna do it"), "I am going to do it")
        
        # Test removing contraction
        self.fixer.remove_contraction("gonna")
        self.assertEqual(self.fixer.fix("I'm gonna do it"), "I am gonna do it")

if __name__ == '__main__':
    unittest.main() 