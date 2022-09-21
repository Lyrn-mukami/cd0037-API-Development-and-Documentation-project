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
        self.database_path ='postgresql://{}:{}@{}/{}'.format('postgres','God loves us all','localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {
            "question": "Who painted the potrait Mona Lisa",
            "answer": "Leonardo da Vinci",
            "difficulty": 2,
            "category": 2}
    
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
    # Category GET request tests
    def test_valid_get_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["categories"])
        
    def test_invalid_get_categories(self):
        res = self.client().get("/categories/1")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    #Test pagination
    def test_get_paginated_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]))
        self.assertTrue(data["categories"])

    def test_requesting_questions_beyond_valid_page(self):
        res = self.client().get("/questions?page=1000")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    
    def test_delete_book(self):
        res = self.client().delete("/questions/2")
        data = json.loads(res.data)

        book = Question.query.filter(Question.id == 2).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_delete_non_existing_question(self):
        res = self.client().delete("/questions/1000")
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")

    def test_valid_question_creation(self):
        res=self.client().post("/questions", json=self.new_question)
        data=json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        
    def test_invalid_question_creation(self):
        res = self.client().post("/questions")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "bad request")


    def test_question_search_with_results(self):
        res = self.client().post("/questions", json={"searchTerm": "medicine"})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["current_category"])
        self.assertTrue(len(data["questions"]), 1)

    def test_get_search_question_without_results(self):
        res = self.client().post("/questions",
                                 json={"searchTerm": "blah blah blah"})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["current_category"])
        self.assertEqual(len(data["questions"]), 0)


    def test_questions_by_category(self):
        res = self.client().get('/categories/4/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

    def test_get_questions_by_invalid_category(self):
        res = self.client().get('/categories/400/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')


    def test_get_next_question_in_quiz(self):
        json_request = {
            'previous_questions': [13], 
            'quiz_category': {'id': '0'}
        }
        res = self.client().post('/quizzes', json=json_request)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_failed_get_next_question(self):
        res = self.client().post('/quizzes')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()