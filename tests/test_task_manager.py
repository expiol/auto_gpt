import unittest
from task_manager import TaskManager

class TestTaskManager(unittest.TestCase):
    def test_task_execution(self):
        task_description = "echo 'Testing TaskManager'"
        manager = TaskManager()
        manager.initialize_task(task_description)

        while not manager.is_task_complete():
            success, output = manager.execute_next_command()
            self.assertTrue(success)

        self.assertTrue(manager.is_task_complete())
        self.assertIn("Testing TaskManager", manager.get_task_result())

    def test_task_with_error(self):
        task_description = "non_existent_command"
        manager = TaskManager()
        manager.initialize_task(task_description)

        success, output = manager.execute_next_command()
        self.assertFalse(success)

        suggestion = manager.analyze_error_with_gpt(output)
        self.assertIsInstance(suggestion, str)

if __name__ == '__main__':
        unittest.main()
