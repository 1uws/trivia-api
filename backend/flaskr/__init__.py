import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from functools import reduce

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_query(page, selection):
	begin = (page - 1) * QUESTIONS_PER_PAGE
	end = page * QUESTIONS_PER_PAGE

	return selection[begin:end]

def create_app(test_config=None):
	# create and configure the app
	app = Flask(__name__)
	setup_db(app)

	"""
	@TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
	"""

	"""
	@TODO: Use the after_request decorator to set Access-Control-Allow
	"""

	"""
	@TODO:
	Create an endpoint to handle GET requests
	for all available categories.
	"""
	@app.route('/categories', methods=['GET'])
	def get_categoris():
		categories = {}
		category_dicts = [{category.id: category.type} for category in Category.query.order_by(Category.id).all()]
		for category in category_dicts:
			categories.update(category)
		return jsonify(
			{
				"success": True,
				"categories": categories,
			}
		)

	"""
	@TODO:
	Create an endpoint to handle GET requests for questions,
	including pagination (every 10 questions).
	This endpoint should return a list of questions,
	number of total questions, current category, categories.

	TEST: At this point, when you start the application
	you should see questions and categories generated,
	ten questions per page and pagination at the bottom of the screen for three pages.
	Clicking on the page numbers should update the questions.
	"""
	@app.route("/questions", methods=["GET"])
	def get_questions():
		questions = Question.query.order_by(Question.id).all()
		page = request.args.get("page", 1, type=int)
		result_questions = [question.format() for question in paginate_query(page, questions)]
		categories = {}
		category_dicts = [{category.id: category.type} for category in Category.query.order_by(Category.id).all()]
		for category in category_dicts:
			categories.update(category)
		if 0 == len(result_questions):
			abort(404)
		return jsonify(
			{
				"success": True,
				"questions": result_questions,
				"total_questions": len(questions),
				"categories": categories,
				# "current_category": ,
			}
		)


	"""
	@TODO:
	Create an endpoint to DELETE question using a question ID.

	TEST: When you click the trash icon next to a question, the question will be removed.
	This removal will persist in the database and when you refresh the page.
	"""
	@app.route('/questions/<int:question_id>', methods=['DELETE'])
	def delete_question(question_id):
		try:
			question = Question.query.filter(Question.id == question_id).one_or_none()

			if question is None:
				abort(404)

			question.delete()

			return jsonify(
				{
					'success': True,
				}
			)
		except:
			abort(422)

	"""
	@TODO:
	Create an endpoint to POST a new question,
	which will require the question and answer text,
	category, and difficulty score.

	TEST: When you submit a question on the "Add" tab,
	the form will clear and the question will appear at the end of the last page
	of the questions list in the "List" tab.
	"""
	@app.route('/post_question', methods=['POST'])
	def new_question():
		json_request = request.get_json()
		json_request = {
			'question': json_request.get('question', ''),
			'answer': json_request.get('answer', ''),
			'category': json_request.get('category', ''),
			'difficulty': json_request.get('difficulty', ''),
		}
		if '' in json_request.values():
			abort(400)
		try:
			question = Question(
				question = json_request['question'],
				answer = json_request['answer'],
				category = json_request['category'],
				difficulty = json_request['difficulty'],
			)
			question.insert()
			return jsonify(
				{
					'success': True,
				}
			)
		except:
			abort(422)

	"""
	@TODO:
	Create a POST endpoint to get questions based on a search term.
	It should return any questions for whom the search term
	is a substring of the question.

	TEST: Search by any phrase. The questions list will update to include
	only question that include that string within their question.
	Try using the word "title" to start.
	"""
	@app.route('/questions', methods=['POST'])
	def search_questions():
		json_request = request.get_json()
		search_term = json_request.get('searchTerm', '').lower()
		questions = Question.query.order_by(Question.id).all()
		result_questions = [question.format() for question in questions if search_term in question.question.lower()]
		return jsonify(
			{
				'success': True,
				'questions': result_questions,
				'total_questions': len(questions),
			}
		)

	"""
	@TODO:
	Create a GET endpoint to get questions based on category.

	TEST: In the "List" tab / main screen, clicking on one of the
	categories in the left column will cause only questions of that
	category to be shown.
	"""
	@app.route('/categories/<int:category_id>/questions', methods=['GET'])
	def get_categorical_questions(category_id):
		questions = Question.query.filter(Question.category == category_id).all()
		questions = [question.format() for question in questions]
		# if 0 == len(questions):
		# 	abort(404)
		return jsonify(
			{
				'success': True,
				'questions': questions,
				'total_questions': len(Question.query.all()),
			}
		)

	"""
	@TODO:
	Create a POST endpoint to get questions to play the quiz.
	This endpoint should take category and previous question parameters
	and return a random questions within the given category,
	if provided, and that is not one of the previous questions.

	TEST: In the "Play" tab, after a user selects "All" or a category,
	one question at a time is displayed, the user is allowed to answer
	and shown whether they were correct or not.
	"""
	def generator_chek_id(list_id):
		return lambda x: x.id not in list_id
	@app.route('/quizzes', methods=['POST'])
	def quizzes():
		json_request = request.get_json()
		json_request = {
			'previous_questions': json_request.get('previous_questions', None),
			'quiz_category': json_request.get('quiz_category', None),
		}
		if None in json_request.values():
			abort(400)
		check_previous_id = generator_chek_id([question for question in json_request['previous_questions']])
		questions = Question.query.filter(Question.category == json_request['quiz_category']['id']).all()
		remain_questions = list(filter(check_previous_id, questions))

		if 0 < len(remain_questions):
			question = random.choice(remain_questions).format()
		else:
			question = None

		return jsonify(
			{
				'success': True,
				'question': question,
			}
		)
	"""
	@TODO:
	Create error handlers for all expected errors
	including 404 and 422.
	"""

	return app