import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType, get_query
from graphene import NonNull

import models

class PostType(SQLAlchemyObjectType):
    class Meta:
        model = models.Post
        
    @staticmethod
    def get_or_raise(id):
        query = models.Post.query.get(id)
        if query is None:
            raise Exception("No Post with id %s" % id)
        return query

class Query(graphene.ObjectType):
    post = graphene.Field(PostType, id=NonNull(graphene.ID))
    posts = NonNull(graphene.List(NonNull(PostType)))
    
    def resolve_post(self, info):
        return PostType.get_or_raise(id)
    
    def resolve_posts(self, info):
        return PostType.get_query(info)

class PostCreate(graphene.Mutation):
    class Arguments:
        title = NonNull(graphene.String)
        description = NonNull(graphene.String)
    
    ok = NonNull(graphene.Boolean)
    post = graphene.Field(PostType)
    def mutate(self, info, title, description):
        model = models.Post(title=title, description=description)
        session = models.db.session
        session.add(model)
        session.commit()
        
        return PostCreate(ok=True, post=model)
    
class PostUpdate(graphene.Mutation):
    class Arguments:
        id = NonNull(graphene.ID)
        title = NonNull(graphene.String)
        description = NonNull(graphene.String)
    
    ok = NonNull(graphene.Boolean)
    post = graphene.Field(PostType)
    def mutate(self, info, id, title, description):
        model = PostType.get_or_raise(id)
        model.title = title
        model.description = description
        
        session = models.db.session
        session.add(model)
        session.commit()
        
        return PostCreate(ok=True, post=model)
    
class PostDelete(graphene.Mutation):
    class Arguments:
        id = NonNull(graphene.ID)
    
    ok = NonNull(graphene.Boolean)
    post = graphene.Field(PostType)
    
    def mutate(self, info, id):
        model = PostType.get_or_raise(id)
        
        session = models.db.session
        session.delete(model)
        session.commit()
        
        return PostCreate(ok=True, post=model)
    
class Mutation(graphene.ObjectType):
    post_create = PostCreate.Field(required=True)
    post_update = PostUpdate.Field(required=True)
    post_delete = PostDelete.Field(required=True)
        
    
schema = graphene.Schema(query=Query, mutation=Mutation)