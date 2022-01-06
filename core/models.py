from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.orm.attributes import get_history
from uuid import uuid4
from flask import g
import json
db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(120), nullable=False)


class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.String(80), nullable=False)
    history = db.Column(db.Text(), nullable=True)
    model_name = db.Column(db.String(80), nullable=False)
    original_id = db.Column(db.Integer)
    db_event_name = db.Column(db.String(80), nullable=False)


@event.listens_for(db.session, 'after_flush')
def db_after_flush(session, flush_context):
    for instance in session.new:
        if isinstance(instance, AuditLog):
            continue
        al = AuditLog(request_id=str(g.request_id), model_name="user",
                      original_id=instance.id,  db_event_name="create")
        session.add(al)


@event.listens_for(db.session, 'before_flush')
def db_before_flush(session, flush_context, instances):
    for instance in session.dirty:
        if isinstance(instance, AuditLog):
            continue
        if isinstance(instance, User):
            history = {}
            if get_history(instance, 'first_name').deleted:
                history['first_name'] = get_history(
                    instance, 'first_name').deleted[0]
            if get_history(instance, 'last_name').deleted:
                history['last_name'] = get_history(
                    instance, 'last_name').deleted[0]
            if len(history):
                al = AuditLog(request_id=str(g.request_id), model_name="user",
                              original_id=instance.id,  db_event_name="edit", history=json.dumps(history))
                session.add(al)
    for instance in session.deleted:
        if isinstance(instance, AuditLog):
            continue
        if isinstance(instance, User):
            history = {
                'first_name': get_history(instance, 'first_name').unchanged[0],
                'last_name':  get_history(instance, 'last_name').unchanged[0]
            }
            if len(history):
                al = AuditLog(request_id=str(g.request_id), model_name="user",
                              original_id=instance.id,  db_event_name="delete", history=json.dumps(history))
                session.add(al)