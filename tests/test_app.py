import unittest
from app import app

class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_execute_task(self):
        response = self.app.post('/execute-task', json={
            "task_description": "echo 'Hello World'",
            "model_name": "gpt-3.5-turbo"
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("Hello World", response.get_json()['output'])

    def test_execute_task_with_model_selection(self):
        response = self.app.post('/execute-task', json={
            "task_description": "echo 'Hello GPT-4'",
            "model_name": "gpt-4"
        })
        # Depending on your access to GPT-4, this test may fail if not authorized
        if response.status_code == 200:
            self.assertIn("Hello GPT-4", response.get_json()['output'])
        else:
            self.assertEqual(response.status_code, 500)

    def test_missing_task_description(self):
        response = self.app.post('/execute-task', json={})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Task description is required", response.get_json()['message'])

if __name__ == '__main__':
    unittest.main()
