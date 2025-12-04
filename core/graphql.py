from lib.graphql import GraphQLAPI, GraphQLEndpoint

from .auth import graphql as auth

api = GraphQLAPI(
    endpoints=(GraphQLEndpoint(name="auth", path="auth/", types=auth.types, schema=auth.schema),),
)
