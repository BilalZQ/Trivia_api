import os
from flask import Flask, json, request, abort, jsonify
from sqlalchemy.orm import query
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category
from utils import (
  paginated_data, get_formatted_categories, error_response
)
from constants import QUESTIONS_PER_PAGE, HTTP_STATUS


def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)

  CORS(app, resources={r'*': { 'origins': '*' }})

  # CORS headers
  @app.after_request
  def after_request(response):
        response.headers.add(
          'Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add(
          'Access-Control-Allow-Methods', 'GET, POST, PUT, PATCH, DELETE')
        return response


  @app.route('/categories')
  def get_categories():
        return jsonify({
          'success': True,
          'categories': get_formatted_categories(),
        })


  '''
  @TODO:

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions.
  '''
  @app.route('/questions')
  def get_questions():
        questions = Question.query.order_by(Question.id).all()

        if not questions:
              abort(HTTP_STATUS.NOT_FOUND)

        paginated_response = paginated_data(request, questions, QUESTIONS_PER_PAGE)

        return jsonify({
          'success': True,
          'questions': paginated_response,
          'total_questions': len(questions),
          'categories': get_formatted_categories(),
          'current_category': None
        })

  '''
  @TODO:

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
        question = Question.query.get(question_id)
        if not question:
            abort(HTTP_STATUS.NOT_FOUND)

        question.delete()

        return jsonify({
          'success': True
        }), HTTP_STATUS.NO_CONTENT


  '''
  @TODO:

  TEST: When you submit a question on the "Add" tab,
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.
  '''
  @app.route('/questions', methods=['POST'])
  def create_question():
        question = request.get_json()

        if not question:
            abort(HTTP_STATUS.BAD_REQUEST)

        question = Question(**question)
        question.insert()

        return jsonify({
          'success': True,
          'id': question.id
        }), HTTP_STATUS.CREATED

  '''
  @TODO:

  TEST: Search by any phrase. The questions list will update to include
  only question that include that string within their question.
  Try using the word "title" to start.
  '''
  @app.route('/questions/search', methods=['POST'])
  def search_questions():
        search_term = request.get_json().get('searchTerm')
        questions = [question.format() for question in Question.query.filter(
          Question.question.ilike(f'%{search_term}%'))]
        return jsonify({
          'success': True,
          'questions': questions,
        })

  '''
  @TODO:

  TEST: In the "List" tab / main screen, clicking on one of the
  categories in the left column will cause only questions of that
  category to be shown.
  '''
  @app.route('/categories/<int:category_id>/questions')
  def get_questions_by_category(category_id):
        category = Category.query.get(category_id)
        if not category:
              abort(HTTP_STATUS.NOT_FOUND)

        questions = [
          question.format()
          for question in Question.query.filter_by(category=category_id)]

        return jsonify({
          'success': True,
          'questions': questions,
          'total_questions': len(questions),
          'current_category': category.format()
        })

  '''
  @TODO:

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not.
  '''
  @app.route('/quizzes', methods=['POST'])
  def play_quiz():
        request_data = request.get_json()
        category = request_data.get('quiz_category')
        previous_questions = request_data.get('previous_questions', [])

        if not category:
              abort(HTTP_STATUS.BAD_REQUEST)

        category_id = category.get('id')
        filters = [Question.id.notin_(previous_questions)]
        if category_id:
              filters.append(Question.category == category_id)
        questions = Question.query.filter(*filters)

        questions = [question.format() for question in questions]
        random_question = random.choice(questions) if questions else None
        return jsonify({
          'success': True,
          'question': random_question,
        })

  '''
  @TODO:
  Create error handlers for all expected errors
  including 404 and 422.
  '''

  @app.errorhandler(HTTP_STATUS.NOT_FOUND)
  def not_found(error):
      return error_response(HTTP_STATUS.NOT_FOUND)


  @app.errorhandler(HTTP_STATUS.BAD_REQUEST)
  def not_found(error):
      return error_response(HTTP_STATUS.BAD_REQUEST)


  @app.errorhandler(HTTP_STATUS.UNPROCESSABLE_ENTITY)
  def unprocessable_entity(error):
      return error_response(HTTP_STATUS.UNPROCESSABLE_ENTITY)


  @app.errorhandler(HTTP_STATUS.INTERNAL_SERVER_ERROR)
  def unprocessable_entity(error):
      return error_response(HTTP_STATUS.INTERNAL_SERVER_ERROR)


  @app.errorhandler(HTTP_STATUS.METHOD_NOT_ALLOWED)
  def unprocessable_entity(error):
      return error_response(HTTP_STATUS.METHOD_NOT_ALLOWED)

  return app
