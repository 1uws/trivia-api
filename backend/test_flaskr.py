import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
	"""This class represents the trivia test case"""

	def setUp(self):
		"""Define test variables and initialize app."""
		self.app = create_app()
		self.client = self.app.test_client
		self.database_name = "trivia_test"
		self.user = os.environ['USER']
		self.password = os.environ['PASSWORD']
		self.database_path = 'postgresql://{}:{}@{}/{}'.format(self.user, self.password, 'localhost:5432', self.database_name)
		setup_db(self.app, self.database_path)

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
	def test_root(self):
		res = self.client().get('/')

		self.assertEqual(res.status_code, 404)

	def test_questions(self):
		res = self.client().get('/questions')

		self.assertEqual(res.status_code, 200)

	def test_categories(self):
		res = self.client().get('/categories')

		self.assertEqual(res.status_code, 200)

	def test_new_question(self):
		res = self.client().post('/post_question', json={
			'question': 'question 1',
			'answer': 'answer 1',
			'category': 1,
			'difficulty': 1,
		})
		data = json.loads(res.data)

		self.assertEqual(res.status_code, 200)
		self.assertEqual(data['success'], True)

	def test_delete_question_200(self):
		res = self.client().delete('/questions/5')
		data = json.loads(res.data)

		self.assertEqual(res.status_code, 200)
		self.assertEqual(data['success'], True)

	def test_delete_question_404(self):
		res = self.client().delete('/questions/id')

		self.assertEqual(res.status_code, 404)

	def test_search_questions_no_result(self):
		res = self.client().post("/questions", json={
			'searchTerm': 'searchTerm',
		})
		data = json.loads(res.data)

		self.assertEqual(res.status_code, 200)
		self.assertEqual(data['success'], True)
		self.assertEqual(data['questions'], [])
		self.assertEqual(data['total_questions'], 19)

	def test_search_questions_found(self):
		res = self.client().post("/questions", json={
			'searchTerm': 'actor',
		})
		data = json.loads(res.data)

		self.assertEqual(res.status_code, 200)
		self.assertEqual(data['success'], True)
		self.assertTrue(data['questions'])
		self.assertEqual(data['total_questions'], 19)

	def test_questions_by_category_200(self):
		res = self.client().get('/categories/1/questions')
		data = json.loads(res.data)

		self.assertEqual(res.status_code, 200)
		self.assertEqual(data['success'], True)
		self.assertTrue(data['questions'])
		self.assertEqual(data['total_questions'], 19)

	def test_questions_by_category_404(self):
		res = self.client().get('/categories/id/questions')

		self.assertEqual(res.status_code, 404)

	def test_quizzes_200(self):
		res = self.client().post('/quizzes', json={
			'previous_questions': [20],
			'quiz_category': {
				'id': 1,
			},
		})
		data = json.loads(res.data)

		self.assertEqual(res.status_code, 200)
		self.assertTrue(data['question'])

	def test_quizzes_400(self):
		res = self.client().post('/quizzes', json={
			'quiz_category': 1,
		})

		self.assertEqual(res.status_code, 400)

	def test_error_400(self):
		res = self.client().post("/post_question", json={
			'question': '',
			'answer': '',
			'category': '',
			'difficulty': '',
		})
		data = json.loads(res.data)

		self.assertEqual(res.status_code, 400)
		self.assertEqual(data["success"], False)
		self.assertEqual(data["message"], "bad request")

	def test_error_404(self):
		res = self.client().delete("/questions/0")
		data = json.loads(res.data)

		self.assertEqual(res.status_code, 404)
		self.assertEqual(data["success"], False)
		self.assertEqual(data["message"], "resource not found")

	def test_error_405(self):
		res = self.client().put("/questions")
		data = json.loads(res.data)

		self.assertEqual(res.status_code, 405)
		self.assertEqual(data["success"], False)
		self.assertEqual(data["message"], "method not allowed")

	def test_error_422(self):
		res = self.client().post("/post_question", json={
			'question': 'question',
			'answer': 'answer',
			'category': 'category',
			'difficulty': 'difficulty',
		})
		data = json.loads(res.data)

		self.assertEqual(res.status_code, 422)
		self.assertEqual(data["success"], False)
		self.assertEqual(data["message"], "unprocessable")

# Make the tests conveniently executable
if __name__ == "__main__":
	unittest.main()