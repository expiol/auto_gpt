import unittest
from gpt_handler import generate_commands, analyze_error

class TestGPTHandler(unittest.TestCase):
    def test_generate_commands(self):
        task_description = "echo 'Test Command'"
        commands = generate_commands(task_description)
        self.assertIn("echo 'Test Command'", commands)

    def test_analyze_error(self):
        error_message = "bash: foobar: command not found"
        previous_command = "foobar"
        suggestion = analyze_error(error_message, previous_command)
        self.assertIsInstance(suggestion, str)
        self.assertTrue(len(suggestion) > 0)

if __name__ == '__main__':
    unittest.main()
