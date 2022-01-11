import os
from flask import Flask, jsonify
import unittest
from app import app
from models import db, User, AuditLog
import requests
import json

app.testing = True

class TestApi(unittest.TestCase):
    def test_index(self):
        client = app.test_client(self)
        response = client.get('/', content_type='html/text')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, bytes(f"Hello, {os.environ['NAME']}!", 'utf-8'))

class TestFunctionalTestCaseBase(unittest.TestCase):
    def __init__(self, methodName) -> None:
        super().__init__(methodName=methodName)
        self.app = Flask(__name__)
        self.app.config.from_object("config.Config")
        db.init_app(self.app)


    def setUp(self):
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        """
        Ensures that the database is emptied for next unittest
        """
        with self.app.app_context():
            pass
            db.drop_all()
class TestDatabase(TestFunctionalTestCaseBase):

    def test_user_create(self):

        with self.app.app_context():
            user = User(first_name="Isabella", last_name="Angulo")
            db.session.add(user)
            db.session.commit()

            self.assertEqual(User.query.get(1).first_name, "Isabella")
            self.assertEqual(User.query.get(1).last_name, "Angulo")
            
            audit_log = AuditLog.query.all()
            self.assertEqual(len(audit_log), 1)
            
            data = { x.name: str(getattr(user, x.name)) for x in user.__table__.columns }
            
            self.assertEqual(str(audit_log[0].payload), str(data))
            
    def test_user_update(self):
	
        with self.app.app_context():
            user = User(first_name="Isabella", last_name="Angulo")
            db.session.add(user)
            db.session.commit()
            
            self.assertEqual(User.query.get(1).first_name, "Isabella")
            self.assertEqual(User.query.get(1).last_name, "Angulo")
            
            user.last_name = "Angulo Nova"
            db.session.commit()
            
            self.assertEqual(User.query.get(1).last_name, "Angulo Nova")
            
            audit_log = AuditLog.query.all()
            self.assertEqual(len(audit_log), 2)
            self.assertEqual(audit_log[1].payload, json.dumps({"last_name": "Angulo Nova"}))
            

            
    def test_user_delete(self):
		
        with self.app.app_context():
            user = User(first_name="Isabella", last_name="Angulo")
            db.session.add(user)
            db.session.commit()

            self.assertEqual(User.query.get(1).first_name, "Isabella")
            self.assertEqual(User.query.get(1).last_name, "Angulo")
            
            db.session.delete(user)
            db.session.commit()
            
            self.assertEqual(User.query.all(), [])
            
# class TestApiGraphQl(TestFunctionalTestCaseBase):
#     def setUp(self):
#         """Set up function called when class is consructed."""
#         self.client = app.test_client(self)
#         self.headers = {'content-type': 'application/json'}
#         return super().setUp()
#     
#     def test_user_create(self):
#         
#         payload = {"query":'mutation{userCreate(firstName:"Isabella",lastName:"Angulo"){ok user{id firstName lastName}}}'}
#     
#         response = self.client.post("/graphql", data=payload)
#         
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.get_json(), {'data': {'userCreate': {'ok': True, 'user': {'id': '1', 'firstName': 'Isabella', 'lastName': 'Angulo'}}}})
# 
#     def test_user_update(self):
#         with self.app.app_context():
#             user = User(first_name="Isabella", last_name="Angulo")
#             db.session.add(user)
#             db.session.commit()
#         
#             payload = {"query":'mutation{userUpdate(id: %s, firstName:"Isabella",lastName:"Angulo Nova"){ok user{id firstName lastName}}}' % (user.id)}
#     
#             response = self.client.post("/graphql", data=payload)
#         
#             self.assertEqual(response.status_code, 200)
#             self.assertEqual(response.get_json(), {'data': {'userUpdate': {'ok': True, 'user': {'id': '1', 'firstName': 'Isabella', 'lastName': 'Angulo Nova'}}}})
#             
#     def test_user_delete(self):
#         with self.app.app_context():
#             user = User(first_name="Isabella", last_name="Angulo")
#             db.session.add(user)
#             db.session.commit()
#         
#             payload = {"query":'mutation{userDelete(id: %s){ok user{id firstName lastName}}}' % (user.id)}
#     
#             response = self.client.post("/graphql", data=payload)
# 
#             self.assertEqual(response.status_code, 200)
#             self.assertEqual(response.get_json(), {'data': {'userDelete': {'ok': True, 'user': {'id': '1', 'firstName': 'Isabella', 'lastName': 'Angulo'}}}})