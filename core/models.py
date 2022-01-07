from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.orm.attributes import get_history
from uuid import uuid4
from flask import g
import json
db = SQLAlchemy()

class Resource(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
class User(Resource):
    __tablename = "user"
    __versioned__ = {}
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(120), nullable=False)
    
class Post(Resource):
    __tablename = "post"
    __versioned__ = {}
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text(), nullable=True)


class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # request_id = db.Column(db.String(80), nullable=False)
    history = db.Column(db.Text(), nullable=True)
    model_name = db.Column(db.String(80), nullable=False)
    original_id = db.Column(db.Integer)
    db_event_name = db.Column(db.String(80), nullable=False)
    


@event.listens_for(db.session, 'after_flush')
def db_after_flush(session, flush_context):
    for instance in session.new:
        if hasattr(instance, "__versioned__"):
            d = {}
            for column in instance.__table__.columns:
                d[column.name] = str(getattr(instance, column.name))
                
            al = AuditLog(history=str(d), model_name=instance.__tablename__, original_id=instance.id,  db_event_name="create")
            session.add(al)
            
        # if isinstance(instance, AuditLog):
        #     continue
        # al = AuditLog(request_id=str(g.request_id), model_name="user",
        #               original_id=instance.id,  db_event_name="create")
        # session.add(al)
# 
# 
# @event.listens_for(db.session, 'before_flush')
# def db_before_flush(session, flush_context, instances):
#     for instance in session.dirty:
#         if isinstance(instance, AuditLog):
#             continue
#         if isinstance(instance, User):
#             history = {}
#             if get_history(instance, 'first_name').deleted:
#                 history['first_name'] = get_history(
#                     instance, 'first_name').deleted[0]
#             if get_history(instance, 'last_name').deleted:
#                 history['last_name'] = get_history(
#                     instance, 'last_name').deleted[0]
#             if len(history):
#                 al = AuditLog(request_id=str(g.request_id), model_name="user",
#                               original_id=instance.id,  db_event_name="edit", history=json.dumps(history))
#                 session.add(al)
#     for instance in session.deleted:
#         if isinstance(instance, AuditLog):
#             continue
#         if isinstance(instance, User):
#             history = {
#                 'first_name': get_history(instance, 'first_name').unchanged[0],
#                 'last_name':  get_history(instance, 'last_name').unchanged[0]
#             }
#             if len(history):
#                 al = AuditLog(request_id=str(g.request_id), model_name="user",
#                               original_id=instance.id,  db_event_name="delete", history=json.dumps(history))
#                 session.add(al)