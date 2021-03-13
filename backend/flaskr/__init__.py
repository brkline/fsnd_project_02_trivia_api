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

    CORS(app, resources={r'/*': {'origins': '*'}})

    @app.after_request
    def set_headers(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization, true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, PATCH, POST, DELETE, OPTIONS')

        return response

    @app.route('/categories', methods=['GET'])
    def get_categories():
        categories = {}
        for category in Category.query.all():
            categories[category.id] = category.type

        return jsonify({
            'categories': categories
        })

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

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        question = Question.query.get(question_id)
        if not question:
            return abort(404, f'Question with {question_id} not found')
        question.delete()

        return jsonify({
            'deleted': question_id
        })

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

    @app.route('/search', methods=['POST'])
    def search():
        search_term = request.json.get('searchTerm', '')
        results = Question.query.filter(
            Question.question.ilike('%{}%'.format(search_term))).all()        
        questions = [question.format() for question in results]
        return jsonify({
            'questions': questions,
            'total_questions': len(questions)
        })

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
