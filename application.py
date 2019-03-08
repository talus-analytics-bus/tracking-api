from flask import Flask

from flask_graphql import GraphQLView
from schema import schema


application = Flask(__name__, static_url_path="", static_folder="static")
application.debug = True

application.add_url_rule('/graphql',
                         view_func=GraphQLView.as_view('graphql', schema=schema,
                                                       graphiql=True))


if __name__ == '__main__':
    application.run()
