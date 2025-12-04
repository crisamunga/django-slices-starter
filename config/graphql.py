from core import graphql as core
from lib.graphql import GraphQLAPI, GraphQLEndpoint, relay

node_schema = relay.create_federated_node_schema(core.api.types)

node_api = GraphQLAPI(endpoints=(GraphQLEndpoint(name="node", path="node/", types=(), schema=node_schema),))

api = core.api + node_api
