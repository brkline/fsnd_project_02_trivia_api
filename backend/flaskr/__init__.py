import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import re
from sqlalchemy.sql.functions import func

from werkzeug.exceptions import HTTPException

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
    CORS(app, resources={r'/*': {'origins': '*'}})
    '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
    @app.after_request
    def set_headers(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization, true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, PATCH, POST, DELETE, OPTIONS')

        return response

    '''
  @TODO:
  Create an endpoint to handle GET requests
  for all available categories.
  '''
    @app.route('/categories', methods=['GET'])
    def get_categories():
        categories = {}
        for category in Category.query.all():
            categories[category.id] = category.type

        return jsonify({
            'categories': categories
        })

    '''
  @TODO:
  Create an endpoint to handle GET requests for questions,
  including pagination (every 10 questions).
  This endpoint should return a list of questions,
  number of total questions, current category, categories.

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions.
  '''
    @app.route('/questions', methods=['GET'])
    def get_questions():
        categories = {}
        for category in Category.query.all():
            categories[category.id] = category.type
        questions = [question.format() for question in Question.query.all()]
        page = int(request.args.get('page', '0'))
        end = page * 10
        start = end - 10

        return jsonify({
            'questions': questions[
                start:end] if page else questions,
            'total_questions': len(questions),
            'categories': categories
        })
    '''
  @TODO:
  Create an endpoint to DELETE question using a question ID.

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page.
  '''
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        question = Question.query.get(question_id)
        if not question:
            return abort(404, f'Question with {question_id} not found')
        question.delete()

        return jsonify({
            'deleted': question_id
        })
    '''
  @TODO:
  Create an endpoint to POST a new question,
  which will require the question and answer text,
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab,
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.
  '''
    @app.route('/questions', methods=['POST'])
    def post_question():
        question = request.json.get('question')
        answer = request.json.get('answer')
        category = request.json.get('category')
        difficulty = request.json.get('difficulty')
        if not (question and answer and category and difficulty):
            return abort(400,
                         'You must include question, answer, category, '
                         'and difficulty when creating a new question')
        question_entry = Question(question, answer, category, difficulty)
        question_entry.insert()

        return jsonify({
            'question': question_entry.format()
        })
    '''
  @TODO:
  Create a POST endpoint to get questions based on a search term.
  It should return any questions for whom the search term
  is a substring of the question.

  TEST: Search by any phrase. The questions list will update to include
  only question that include that string within their question.
  Try using the word "title" to start.
  '''
    @app.route('/search', methods=['POST'])
    def search():
        search_term = request.json.get('searchTerm', '')
        questions = [question.format() for question in Question.query.all() if
                     re.search(search_term, question.question, re.IGNORECASE)]

        return jsonify({
            'questions': questions,
            'total_questions': len(questions)
        })
    '''
  @TODO:
  Create a GET endpoint to get questions based on category.

  TEST: In the "List" tab / main screen, clicking on one of the
  categories in the left column will cause only questions of that
  category to be shown.
  '''
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_questions_by_category(category_id):
        if not category_id:
            return abort(400, 'Invalid category id')
        questions = [question.format() for question in
                     Question.query.filter(Question.category == category_id)]

        return jsonify({
            'questions': questions,
            'total_questions': len(questions),
            'current_category': category_id
        })

    '''
  @TODO:
  Create a POST endpoint to get questions to play the quiz.
  This endpoint should take category and previous question parameters
  and return a random questions within the given category,
  if provided, and that is not one of the previous questions.

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not.
  '''
    @app.route('/quizzes', methods=['POST'])
    def get_quiz_questions():
        previous_questions = request.json.get('previous_questions')
        quiz_category = request.json.get('quiz_category')
        if not quiz_category:
            return abort(400, 'Quiz Category missing in request payload')
        category_id = int(quiz_category.get('id'))
        questions = Question.query.filter(
            Question.category == category_id,
            ~Question.id.in_(previous_questions)) if category_id else \
            Question.query.filter(~Question.id.in_(previous_questions))
        question = questions.order_by(func.random()).first()
        if not question:
            return jsonify({})
        return jsonify({
            'question': question.format()
        })
    '''
  @TODO:
  Create error handlers for all expected errors
  including 404 and 422.
  '''
    @app.errorhandler(HTTPException)
    def http_exception_handler(error):
        return jsonify({
            'success': False,
            'error': error.code,
            'message': error.description
        }), error.code

    @app.errorhandler(Exception)
    def exception_handler(error):
        return jsonify({
            'success': False,
            'error': 500,
            'message': f'An unexpected error occurred: {error}'
        }), 500

    return app
