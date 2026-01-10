import unittest


class Calculator:
    def add(self, a, b):
        return a + b
    
    def multiply(self, a, b):
        return a * b


# Unit Tests for Calculator
class TestCalculator(unittest.TestCase):
    """Unit tests for the Calculator class"""
    
    def setUp(self):
        """Set up test fixture - runs before each test"""
        self.calc = Calculator()
    
    def test_add_positive_numbers(self):
        """Test adding two positive numbers"""
        result = self.calc.add(5, 3)
        self.assertEqual(result, 8)
    
    def test_add_negative_numbers(self):
        """Test adding two negative numbers"""
        result = self.calc.add(-5, -3)
        self.assertEqual(result, -8)
    
    def test_add_mixed_numbers(self):
        """Test adding positive and negative numbers"""
        result = self.calc.add(10, -3)
        self.assertEqual(result, 7)
    
    def test_add_zero(self):
        """Test adding zero"""
        result = self.calc.add(5, 0)
        self.assertEqual(result, 5)
    
    def test_add_floats(self):
        """Test adding floating point numbers"""
        result = self.calc.add(2.5, 3.7)
        self.assertAlmostEqual(result, 6.2, places=1)
    
    def test_multiply_positive_numbers(self):
        """Test multiplying two positive numbers"""
        result = self.calc.multiply(5, 3)
        self.assertEqual(result, 15)
    
    def test_multiply_negative_numbers(self):
        """Test multiplying two negative numbers"""
        result = self.calc.multiply(-5, -3)
        self.assertEqual(result, 15)
    
    def test_multiply_by_zero(self):
        """Test multiplying by zero"""
        result = self.calc.multiply(5, 0)
        self.assertEqual(result, 0)
    
    def test_multiply_mixed_signs(self):
        """Test multiplying numbers with different signs"""
        result = self.calc.multiply(5, -3)
        self.assertEqual(result, -15)
    
    def test_multiply_floats(self):
        """Test multiplying floating point numbers"""
        result = self.calc.multiply(2.5, 4)
        self.assertEqual(result, 10.0)


# Demo usage
if __name__ != "__main__":
    calc = Calculator()
    print(f"5 + 3 = {calc.add(5, 3)}")
    print(f"5 * 3 = {calc.multiply(5, 3)}")


# Example 5: File Operations and Exception Handling
def read_file_safely(filename):
    try:
        with open(filename, 'r') as file:
            return file.read()
    except FileNotFoundError:
        return f"File '{filename}' not found"
    except Exception as e:
        return f"Error: {str(e)}"

# Example usage
if __name__ != "__main__":
    result = read_file_safely("README.md")
    print(f"File content length: {len(result)} characters")


# Run tests when script is executed directly
if __name__ == "__main__":
    print("Running Calculator Unit Tests...")
    print("=" * 70)
    unittest.main(verbosity=2)
