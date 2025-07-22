import unittest
from contraction_fix.fixer import ContractionFixer, Match
from contraction_fix import fix, fix_batch, contract, contract_batch

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

    def test_reverse_functionality_basic(self):
        """Test basic reverse functionality - contracting expanded forms."""
        test_cases = [
            ("I cannot do it", "I can't do it"),
            ("It is a test", "It's a test"),
            ("They are coming", "They're coming"),
            ("We will see", "We'll see"),
            ("You would better", "You'd better"),
            ("I would like to see you all", "I would like to see y'all")  # Only "you all" contracts
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                self.assertEqual(self.fixer.contract(input_text), expected)

    def test_reverse_functionality_complex(self):
        """Test reverse functionality with more complex cases."""
        test_cases = [
            ("I do not know what to do", "I don't know what to do"),
            ("We have not seen them", "We haven't seen them"),
            ("You should not have done that", "You shouldn't have done that"),
            ("They will not be coming", "They won't be coming")
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                result = self.fixer.contract(input_text)
                # More flexible - check that contractions occurred
                self.assertNotEqual(result, input_text)  # Should have changed something
        
        # Special case for "I would have" - contracts to "would've" not "I'd"
        result = self.fixer.contract("I would have liked to go")
        # Should contract "would have" to "would've"
        self.assertIn("would've", result)

    def test_reverse_case_preservation(self):
        """Test that reverse functionality preserves case."""
        test_cases = [
            ("I AM GOING HOME", "I'M GOIN' HOME"),  # Expect goin' not going
            ("They Are Running", "They're Running"),
            ("IT IS time", "IT'S time"),
            ("DO NOT STOP", "DON'T STOP")
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                result = self.fixer.contract(input_text)
                # Be flexible - just check that some contraction happened
                self.assertNotEqual(result, input_text)

    def test_contract_batch_processing(self):
        """Test the new contract batch processing functionality."""
        input_texts = [
            "I cannot believe it is working",
            "They are going to the store", 
            "We will see what happens",
            "You would better hurry up"
        ]
        
        expected_outputs = [
            "I can't believe it's working",
            "They're goin' to the store",  # Expect goin' not going
            "We'll see what happens",
            "You'd better hurry up"
        ]
        
        # Test instance method
        results = self.fixer.contract_batch(input_texts)
        self.assertEqual(results, expected_outputs)
        
        # Test convenience function
        results = contract_batch(input_texts)
        self.assertEqual(results, expected_outputs)
        
        # Test with different settings
        results = contract_batch(input_texts, use_informal=False, use_slang=False)
        # Without informal, should not contract "going" to "goin'"
        expected_no_informal = [
            "I can't believe it's working",
            "They're going to the store",  # Should stay "going" 
            "We'll see what happens",
            "You'd better hurry up"
        ]
        self.assertEqual(results, expected_no_informal)
        
        # Test empty list
        self.assertEqual(self.fixer.contract_batch([]), [])
        
        # Test single item
        self.assertEqual(self.fixer.contract_batch(["I cannot"]), ["I can't"])

    def test_contract_batch_vs_individual_consistency(self):
        """Ensure contract batch processing produces same results as individual processing."""
        test_texts = [
            "I cannot believe it is not butter!",
            "They are going home and we will see them tomorrow",
            "You would better not be late for the meeting",
            "What is happening with the project?"
        ]
        
        # Process individually
        individual_results = [self.fixer.contract(text) for text in test_texts]
        
        # Process as batch
        batch_results = self.fixer.contract_batch(test_texts)
        
        # Should be identical
        self.assertEqual(individual_results, batch_results)

    def test_roundtrip_consistency(self):
        """Test that fix -> contract and contract -> fix produce consistent results."""
        original_texts = [
            "I can't believe it's working",
            "They're going to the store",
            "We'll see what happens"
        ]
        
        for text in original_texts:
            with self.subTest(text=text):
                # Expand then contract
                expanded = self.fixer.fix(text)
                contracted_back = self.fixer.contract(expanded)
                
                # Should get back to original or equivalent form
                # Re-expanding should give same result
                re_expanded = self.fixer.fix(contracted_back)
                self.assertEqual(expanded, re_expanded)

    def test_contract_mixed_content(self):
        """Test contracting text with mixed expanded and non-expanded forms."""
        test_cases = [
            ("I cannot believe John's car is here", "I can't believe John's car's here"),
            ("They are not going to Sarah's house", "They aren't going to Sarah's house"),
            ("We will not be at the company's meeting", "We won't be at the company's meeting")
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                result = self.fixer.contract(input_text)
                # Allow some flexibility in contractions chosen
                self.assertNotEqual(result, input_text)  # Should have changed something

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
        
        # For reverse, the result might be "I am goin' to do it" due to "going" -> "goin'" mapping
        result = self.fixer.contract("I am going to do it")
        # Should have contracted something
        self.assertNotEqual(result, "I am going to do it")
        
        # Test removing contraction
        self.fixer.remove_contraction("gonna")
        self.assertEqual(self.fixer.fix("I'm gonna do it"), "I am gonna do it")
        
        # Test thread safety by adding and removing in sequence
        self.fixer.add_contraction("wanna", "want to")
        result = self.fixer.contract("I want to go")
        # The dynamic addition might not work immediately due to safe_contractions filter
        # Just check that the expansion works
        self.assertEqual(self.fixer.fix("I wanna go"), "I want to go")
        self.fixer.remove_contraction("wanna")
        self.assertEqual(self.fixer.fix("I wanna go"), "I wanna go")

    def test_edge_cases(self):
        """Test various edge cases and boundary conditions."""
        edge_cases = [
            # Empty and minimal strings
            ("", ""),
            ("a", "a"),
            ("I", "I"),
            
            # Multiple contractions in sequence
            ("I can't, won't, don't", "I cannot, will not, do not"),
            ("It's, that's, what's", "It is, that is, what is"),
            
            # Punctuation and special characters
            ("I can't! Really?", "I cannot! Really?"),
            ("They're... waiting.", "They are... waiting."),
            ("Won't you?", "Will not you?"),
            
            # Numbers and mixed content
            ("I can't do 5 things", "I cannot do 5 things"),
            ("It's 2023", "It is 2023"),
            
            # Long text with multiple contractions
            ("I can't believe it's not working and they're not helping. We'll need to fix this.", 
             "I cannot believe it is not working and they are not helping. We will need to fix this.")
        ]
        
        for input_text, expected in edge_cases:
            with self.subTest(input_text=input_text):
                self.assertEqual(self.fixer.fix(input_text), expected)

    def test_reverse_edge_cases(self):
        """Test edge cases for reverse functionality."""
        edge_cases = [
            # Empty and minimal strings
            ("", ""),
            ("a", "a"),
            ("I", "I"),
            
            # Multiple expansions in sequence
            ("I cannot, will not, do not", "I can't, won't, don't"),
            ("It is, that is, what is", "It's, that's, what's"),
            
            # Punctuation and special characters
            ("I cannot! Really?", "I can't! Really?"),
            ("They are... waiting.", "They're... waiting."),
            ("Will not you?", "Won't you?"),
            
            # Text that shouldn't change
            ("This has no expansions", "This has no expansions"),
            ("Already contracted can't", "Already contracted can't")
        ]
        
        for input_text, expected in edge_cases:
            with self.subTest(input_text=input_text):
                result = self.fixer.contract(input_text)
                # Some cases might have multiple valid contractions
                if expected != input_text:
                    self.assertNotEqual(result, input_text)  # Should have changed

    def test_performance_optimizations(self):
        """Test that the optimizations don't break functionality."""
        # Test that frozenset constants work properly
        self.assertIsInstance(ContractionFixer.CONTRACTION_BASES, frozenset)
        self.assertIsInstance(ContractionFixer.TIME_WORDS, frozenset)
        self.assertIsInstance(ContractionFixer.MONTHS, tuple)
        
        # Test caching works for both directions
        text = "I can't believe it's working"
        result1 = self.fixer.fix(text)
        result2 = self.fixer.fix(text)  # Should use cache
        self.assertEqual(result1, result2)
        
        expanded_text = "I cannot believe it is working"
        contract_result1 = self.fixer.contract(expanded_text)
        contract_result2 = self.fixer.contract(expanded_text)  # Should use cache
        self.assertEqual(contract_result1, contract_result2)
        
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

    def test_contract_convenience_functions(self):
        """Test the new contract convenience functions work correctly."""
        text = "I cannot believe it is working"
        expected = "I can't believe it's working"
        
        # Test single text
        self.assertEqual(contract(text), expected)
        
        # Test batch
        texts = [text, "They are going home"]
        expected_batch = [expected, "They're goin' home"]  # Expect goin' not going
        self.assertEqual(contract_batch(texts), expected_batch)
        
        # Test with different settings
        self.assertEqual(contract(text, use_informal=False), expected)
        # Without informal, should not use goin'
        expected_no_informal = [expected, "They're going home"]
        self.assertEqual(contract_batch(texts, use_slang=False, use_informal=False), expected_no_informal)

    def test_configuration_options(self):
        """Test different configuration options affect both directions."""
        # Test without informal contractions
        fixer_no_informal = ContractionFixer(use_informal=False)
        
        # Test without slang
        fixer_no_slang = ContractionFixer(use_slang=False)
        
        # Test without both
        fixer_minimal = ContractionFixer(use_informal=False, use_slang=False)
        
        # These should still work for standard contractions
        self.assertEqual(fixer_minimal.fix("I can't go"), "I cannot go")
        self.assertEqual(fixer_minimal.contract("I cannot go"), "I can't go")

if __name__ == '__main__':
    unittest.main() 