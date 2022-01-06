import graphene
from schema.user import schema as UserSchema
from schema.post import schema as PostSchema

class Query(UserSchema.Query, PostSchema.Query, graphene.ObjectType):
    pass

class Mutation(UserSchema.Mutation, PostSchema.Mutation, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)