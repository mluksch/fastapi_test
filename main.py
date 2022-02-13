# FastApi has some advantages:
# (1) asynchronous/non-blocking i.e. not every request handlers needs to run in its own thread
# and blocks any other executions within the same thread.
# Flask on the other hand is based on WSGI (which is synchronous by default, there is
# also an asynchronous version of WSGI: ASGI)
# (2) built-in data validation
# (3) websocket-support
# (4) automatic documentation of API endpoints

import fastapi
import fastapi.encoders as encoders

# Start app by: "pipenv run uvicorn main:app --reload"
# "--reload" for hot-reload on code changes
# Endpoint exposed at: http://localhost:8000
# Docs exposed at: http://localhost:8000/docs
app = fastapi.FastAPI()

persons = [
    {"name": "Judy", "age": 10},
    {"name": "Jeremy", "age": 20},
    {"name": "Max", "age": 30},
    {"name": "Jonas", "age": 50},
    {"name": "Sam", "age": 60},
    {"name": "Ashley", "age": 70},
    {"name": "Jack", "age": 80}
]


# Example: http://localhost:8000
# Returns: {"gruss":"hallo","id":1,"name":"Max"}
@app.get("/")
def index():
    # explicitly encode objects to json-response with FastAPI:
    return encoders.jsonable_encoder({
        "gruss": "hallo",
        "id": 1,
        "name": "Max"
    })


# Catch GET/POST-Parameters directly with arguments in request-handlers
# Example: http://localhost:8000/persons?filter=j&limit=2&orderby=age
# Returns: [{"name":"Judy","age":10},{"name":"Jeremy","age":20}]
@app.get("/persons")
def items(filter: str = "", limit: int = 10, orderby: str = "name"):
    # explicitly encode objects to json-response with FastAPI:
    # builtin-function "sorted" returns new list
    filtered = sorted([p for p in persons
                       if filter in p.get("name").lower()][0:limit],
                      key=lambda p: p[orderby])
    return encoders.jsonable_encoder(filtered)


# Catch Path-Parameters with "/../{key}" pattern in the path
# Example: http://localhost:8000/persons/jack
# Returns: {"name":"Jack","age":80}
@app.get("/persons/{name}")
def add_item(name: str):
    # use a generator in order to get the first element
    # matching a predicate in a list:
    generator = (p for p in persons if p.get("name").lower() == name)
    return next(generator, None)
