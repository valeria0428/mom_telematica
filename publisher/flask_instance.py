from flask import Flask
from flask_cors import CORS
import os


class FlaskInstance:
    __instance = None
    __app = Flask(__name__)
    __port = int(float(os.environ.get("PORT", 5000)))

    def __init__(self):
        if self.__instance is None:
            self.__instance = object.__new__(self)
            CORS(self.__app)

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
            CORS(cls.__app)
        return cls.__instance

    @property
    def __getinstance__(self):
        """
        Retrive singleton instance
        @return: Singleton instance of flask_instance
        """
        if self.__instance is None:
            self.__instance = object.__new__(self)
            CORS(self.__app)
        return self.__instance

    def get_app(self) -> Flask:
        return self.__app

    def run(self):
        self.__app.run(host="0.0.0.0", port=self.__port, debug=False)

    def add_endpoint(self, endpoint=None, endpoint_name=None, handler=None, methods=[]):
        """
        Create a new http endpoint for the services
        @param endpoint: Url to match with the request
        @type endpoint: str
        @param endpoint_name: Internal name to recognize the endpoint in the system
        @type endpoint_name: str
        @param handler: Execution method
        @param methods: HTTP methods can be: "GET", "POST", "PUT", "DELETE" lowercase is allowed
        @type methods: list
        """
        methods = [x.upper() for x in methods]
        self.__app.add_url_rule(endpoint, endpoint_name, handler, None, methods=methods)
