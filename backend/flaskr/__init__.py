import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from sqlalchemy.sql import func
from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

# pagination function
def pagination(request, selection):
     page = request.args.get('page', 1, type=int)
     start = (page - 1) * QUESTIONS_PER_PAGE
     end = start + QUESTIONS_PER_PAGE
     questions = [question.format() for question in selection]
     current_questions = questions[start:end]
     return current_questions
# end of pagination function

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    CORS(app) Add once done with the project
    """

    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
    """
    @DONE: Use the after_request decorator to set Access-Control-Allow
    """
    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response
    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    json should return categories and success
    """
    @app.route('/categories', methods=['GET'])
    def get_categories():
        try:
            categories = Category.query.order_by(Category.id).all()
            if len(categories) == 0:
                abort(404)

            return jsonify(
                {
                    "success":True,
                    "categories": {
                        category.id: category.type for category in categories
                    }
                }
                )
        except:
            abort(400)

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
    @app.route('/questions', methods=['GET'])
    def paginated_questions():
        try:
            selection = Question.query.order_by(Question.id).all()
            current_questions=pagination(request, selection)
            categories = Category.query.order_by(Category.id).all()
            if len(current_questions) == 0:
                abort(404)
            return jsonify({
                "success": True,
                "questions": current_questions,
                "total_questions": len(selection),
                "categories": {
                        category.id: category.type for category in categories
                    },
                "current_category": "Varying"
            })
        except:
            abort(404)
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
            return jsonify({
                "success": True
            })
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
    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json()
        search = body.get("searchTerm", None)


        new_question = body.get("question", None)
        answer = body.get("answer", None)
        category = body.get("category", None)
        difficulty = body.get("difficulty", None)
        try:

            if search:
                selection = Question.query.order_by(Question.id).filter(
                    Question.question.ilike("%{}%".format(search))
                )
                current_questions = pagination(request, selection)
                return jsonify({
                    "success":True,
                    "questions":current_questions,
                    "total_questions":len(selection.all()),
                    "current_category": "Varying"
                })
            else:
                question = Question(question=new_question,answer=answer,difficulty=difficulty,category=category)

                question.insert()

                return jsonify({
                    "success":True,
                })
            
        except:
            abort(400)
        
    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_by_category(category_id):
        try:
            questions = Question.query.filter(Question.category == category_id).all()
            category_questions = pagination(request, questions)
            if (len(category_questions) == 0):
                abort(404)
            return jsonify({
                "success":True,
                "questions": category_questions,
                "total_questions": len(questions),
                "current_category": category_id
            })
        except:
            abort(404)
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
    @app.route('/quizzes', methods=['POST'])
    def next_question():
        try:
            body = request.get_json()
            previous_questions = body.get('previous_questions')
            quiz_category = body.get('quiz_category')
            if quiz_category is None or quiz_category['id'] == 0:
                questions =[question for question in Question.query.all()]
            else:
                questions =[question for question in Question.query.filter(Question.category== quiz_category['id'])]
            available_questions=[]
            for question in questions:
                    if question['id'] not in previous_questions:
                        available_questions.append(question)
            if (len(available_questions) > 0):
                        chosen = random.choice(available_questions) 
                        return jsonify({
                            "success":True,
                            "question" : chosen
                        }) 
            else:
                    return jsonify({
                        "success":True,
                        "question" : None
                    })  
        except:
         abort(400)
            
    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "resource not found"}),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "unprocessable"}),
            422,
        )

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"success": False, "error": 400, "message": "bad request"}), 400
    return app

