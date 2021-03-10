import os
import unittest
import json
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category

load_dotenv()


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client

        self.db_user_name = os.environ.get("DB_USER_NAME")
        self.db_password = os.environ.get("DB_PASSWORD")
        self.database_name = "trivia"
        self.database_path = "postgres://{}:{}@{}/{}".format(
            self.db_user_name, self.db_password, 'localhost:5432', self.database_name)
        # self.database_name = "trivia_test"
        # self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)
        self.test_question = {
            'question': 
            """
            What was the title of the 1990 fantasy directed by Tim Burton
            about a young man with multi-bladed appendages?
            """,
            'answer': 'Edward Scissorhands',
            'category': 5,
            'difficulty': 3
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_all_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(data['categories'], dict)

    def test_get_questions(self):
        res = self.client().get('/questions?page=1')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(data['questions'], list)
        self.assertLessEqual(len(data['questions']), 10)
        self.assertIsInstance(data['total_questions'], int)
        self.assertIsInstance(data['categories'], dict)

    def test_delete_question(self):
        question_id = 1
        res = self.client().delete(f'/questions/{question_id}')
        data = json.loads(res.data)
        if res.status_code == 404:
            self.assertEqual(data['success'], False)
        else:
            self.assertEqual(data['deleted'], 1)

    def test_delete_question_fail(self):
        res = self.client().delete('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)

    def test_post_question(self):
        res = self.client().post('/questions',
                                 data=json.dumps(self.test_question),
                                 content_type='application/json')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertIsNotNone(data['question'])

    def test_post_question_fail(self):
        res = self.client().post('/questions',
                                 data=json.dumps({}),
                                 content_type='application/json')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)

    def test_search(self):
        request_data = {'searchTerm': 'what'}
        res = self.client().post('/search', data=json.dumps(request_data),
                                 content_type='application/json')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(data['questions'], list)
        self.assertIsInstance(data['total_questions'], int)

    def test_get_questions_by_category(self):
        category_id = 1
        res = self.client().get(f'/categories/{category_id}/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(data['questions'], list)
        self.assertIsInstance(data['total_questions'], int)
        self.assertEqual(data['current_category'], category_id)
        for question in data['questions']:
            self.assertEqual(question['category'], category_id)

    def test_get_questions_by_category_fail(self):
        category_id = 0
        res = self.client().get(f'/categories/{category_id}/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)

    def test_get_quiz_questions(self):
        request_data = {
            'previous_questions': [1, 2, 3, 4],
            'quiz_category': {'id': 1, 'type': 'Science'}
        }
        res = self.client().post('/quizzes', data=json.dumps(request_data),
                                 content_type='application/json')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        if data.get('question', None):
            self.assertNotIn(data['question']['id'],
                             request_data['previous_questions'])

    def test_get_quiz_questions_fail(self):
        res = self.client().post('/quizzes', data=json.dumps({}),
                                 content_type='application/json')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
