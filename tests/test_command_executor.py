import unittest
from command_executor import execute_command

class TestCommandExecutor(unittest.TestCase):
    def test_execute_command_success(self):
        success, output = execute_command("echo 'Hello, World!'")
        self.assertTrue(success)
        self.assertEqual(output.strip(), "Hello, World!")

    def test_execute_command_failure(self):
        success, output = execute_command("non_existent_command")
        self.assertFalse(success)
        self.assertIn("command not found", output)

if __name__ == '__main__':
    unittest.main()
