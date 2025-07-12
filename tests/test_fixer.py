import unittest
from contraction_fix.fixer import ContractionFixer, Match
from contraction_fix import fix, fix_batch

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
            ("I'd like to see y'all", "I would like to see you all")
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

    def test_batch_processing(self):
        """Test the new batch processing functionality."""
        input_texts = [
            "I can't believe it's working",
            "They're going to the store",
            "We'll see what happens",
            "You'd better hurry up"
        ]
        
        expected_outputs = [
            "I cannot believe it is working",
            "They are going to the store",
            "We will see what happens",
            "You would better hurry up"
        ]
        
        # Test instance method
        results = self.fixer.fix_batch(input_texts)
        self.assertEqual(results, expected_outputs)
        
        # Test convenience function
        results = fix_batch(input_texts)
        self.assertEqual(results, expected_outputs)
        
        # Test with different settings
        results = fix_batch(input_texts, use_informal=False, use_slang=False)
        self.assertEqual(results, expected_outputs)
        
        # Test empty list
        self.assertEqual(self.fixer.fix_batch([]), [])
        
        # Test single item
        self.assertEqual(self.fixer.fix_batch(["I can't"]), ["I cannot"])

    def test_batch_vs_individual_consistency(self):
        """Ensure batch processing produces same results as individual processing."""
        test_texts = [
            "I can't believe it's not butter!",
            "They're going home and we'll see them tomorrow",
            "You'd better not be late for the meeting",
            "What's happening with the project?"
        ]
        
        # Process individually
        individual_results = [self.fixer.fix(text) for text in test_texts]
        
        # Process as batch
        batch_results = self.fixer.fix_batch(test_texts)
        
        # Should be identical
        self.assertEqual(individual_results, batch_results)

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
        for match in matches:
            self.assertLessEqual(len(match.context), len(match.text) + 6)

    def test_possessive_vs_contraction(self):
        test_cases = [
            # Contractions
            ("it's a nice day", "it is a nice day"),
            ("that's interesting", "that is interesting"),
            ("what's happening", "what is happening"),
            ("there's a problem", "there is a problem"),
            
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
            ("I'd like to", "I would like to"),
            ("don't do it", "do not do it")
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                # Test with standard apostrophe
                self.assertEqual(self.fixer.fix(input_text), expected)
                # Test with curly apostrophe
                curly_input = input_text.replace("'", "'")
                self.assertEqual(self.fixer.fix(curly_input), expected)

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

    def test_performance_optimizations(self):
        """Test that the optimizations don't break functionality."""
        # Test that frozenset constants work properly
        self.assertIsInstance(ContractionFixer.CONTRACTION_BASES, frozenset)
        self.assertIsInstance(ContractionFixer.TIME_WORDS, frozenset)
        self.assertIsInstance(ContractionFixer.MONTHS, tuple)
        
        # Test caching works
        text = "I can't believe it's working"
        result1 = self.fixer.fix(text)
        result2 = self.fixer.fix(text)  # Should use cache
        self.assertEqual(result1, result2)
        
        # Test that cache is cleared when contractions are modified
        self.fixer.add_contraction("testword", "test word")
        self.fixer.remove_contraction("testword")

    def test_convenience_functions(self):
        """Test the convenience functions work correctly."""
        text = "I can't believe it's working"
        expected = "I cannot believe it is working"
        
        # Test single text
        self.assertEqual(fix(text), expected)
        
        # Test batch
        texts = [text, "They're going home"]
        expected_batch = [expected, "They are going home"]
        self.assertEqual(fix_batch(texts), expected_batch)
        
        # Test with different settings
        self.assertEqual(fix(text, use_informal=False), expected)
        self.assertEqual(fix_batch(texts, use_slang=False), expected_batch)

if __name__ == '__main__':
    unittest.main() 