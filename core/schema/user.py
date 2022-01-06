import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType, get_query
from graphene import NonNull

import models

class UserType(SQLAlchemyObjectType):
    class Meta:
        model = models.User
        
    @staticmethod
    def get_or_raise(id):
        query = models.User.query.get(id)
        if query is None:
            raise Exception("No User with id %s" % id)
        return query

class Query(graphene.ObjectType):
    hello_world = graphene.String()
    
    user = graphene.Field(UserType, id=NonNull(graphene.ID))
    users = NonNull(graphene.List(NonNull(UserType)))
    
    def resolve_hello_world(self, info):
        return "Hello World"
    
    def resolve_user(self, info):
        return UserType.get_or_raise(id)
    
    def resolve_users(self, info):
        return UserType.get_query(info)

class UserCreate(graphene.Mutation):
    class Arguments:
        first_name = NonNull(graphene.String)
        last_name = NonNull(graphene.String)
    
    ok = NonNull(graphene.Boolean)
    user = graphene.Field(UserType)
    def mutate(self, info, first_name, last_name):
        model = models.User(first_name=first_name, last_name=last_name)
        session = models.db.session
        session.add(model)
        session.commit()
        
        return UserCreate(ok=True, user=model)
    
class UserUpdate(graphene.Mutation):
    class Arguments:
        id = NonNull(graphene.ID)
        first_name = NonNull(graphene.String)
        last_name = NonNull(graphene.String)
    
    ok = NonNull(graphene.Boolean)
    user = graphene.Field(UserType)
    def mutate(self, info, id, first_name, last_name):
        model = UserType.get_or_raise(id)
        model.first_name = first_name
        model.last_name = last_name
        
        session = models.db.session
        session.add(model)
        session.commit()
        
        return UserCreate(ok=True, user=model)
    
class UserDelete(graphene.Mutation):
    class Arguments:
        id = NonNull(graphene.ID)
    
    ok = NonNull(graphene.Boolean)
    user = graphene.Field(UserType)
    
    def mutate(self, info, id):
        model = UserType.get_or_raise(id)
        
        session = models.db.session
        session.delete(model)
        session.commit()
        
        return UserCreate(ok=True, user=model)
    
class Mutation(graphene.ObjectType):
    user_create = UserCreate.Field(required=True)
    user_update = UserUpdate.Field(required=True)
    user_delete = UserDelete.Field(required=True)
        
    
schema = graphene.Schema(query=Query, mutation=Mutation)