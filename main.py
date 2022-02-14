# FastApi has some advantages:
# (1) asynchronous/non-blocking i.e. not every request handlers needs to run in its own thread
# and blocks any other executions within the same thread.
# Flask on the other hand is based on WSGI (which is synchronous by default, there is
# also an asynchronous version of WSGI: ASGI)
# (2) built-in data validation
# (3) websocket-support
# (4) automatic documentation of API endpoints

import enum
import typing

import fastapi
import fastapi.encoders as encoders
import pydantic

# Start app by: "pipenv run uvicorn main:app --reload"
# "--reload" for hot-reload on code changes
# Endpoint exposed at: http://localhost:8000
# Docs exposed at: http://localhost:8000/docs
app = fastapi.FastAPI()


# Typing is essential & important in FastAPI:
# Because all validations & even returned response fields
# are determined by types in the request handler
# Also typing define what parameters in the request handler
# belong to the request body (BaseModel)
# or to the query parameters

# Send a request body: Declare custom subclass of Pydantic's BaseModel
# and define static class fields (similar to SQLAlchemy-Models)
class Person(pydantic.BaseModel):
    name: str
    age: typing.Optional[int]


persons: typing.List[Person] = [Person(**kwargs) for kwargs in [
    {"name": "Judy", "age": 10},
    {"name": "Jeremy", "age": 20},
    {"name": "Max", "age": 30},
    {"name": "Jonas", "age": 50},
    {"name": "Sam", "age": 60},
    {"name": "Ashley", "age": 70},
    {"name": "Jack", "age": 80}
]]


# Example: http://localhost:8000
# Returns: {"gruss":"hallo","id":1,"name":"Max"}
@app.get("/")
def index():
    """Documentation available at http://localhost:8000/docs
    Returns some random dict
    """
    # explicitly encode objects to json-response with FastAPI:
    # for dict this is not mandatory
    # but for a non-dict object this json-decoder would be mandatory:
    return encoders.jsonable_encoder({
        "gruss": "hallo",
        "id": 1,
        "name": "Max"
    })


# Define Custom-Enum
class OrderBy(str, enum.Enum):
    AGE = "age"
    NAME = "name"


# Catch GET/POST-Parameters directly with arguments in request-handlers
# Example: http://localhost:8000/persons?filter=j&limit=2&orderby=age
# Returns: [{"name":"Judy","age":10},{"name":"Jeremy","age":20}]
# - Parameters: Use Python typings for each argument
# FastAPI will evaluate each type and use them for the Docs
# - Response: FastAPI will take care of filtering out all
# the data that is not declared in the output model (using Pydantic)
@app.get("/persons", response_model=typing.List[Person])
async def items(
        # defining Optional parameter:
        filter: typing.Optional[str] = None,
        limit: int = 10,
        orderby: OrderBy = OrderBy.NAME
):
    """
    Returns all persons based on filter, limited & ordered
    """

    # builtin-function "sorted" returns new list
    def key_func(p: Person) -> typing.Union[str, int]:
        if orderby == OrderBy.NAME:
            return p.name
        elif orderby == OrderBy.AGE:
            return p.age

    filtered: [Person] = sorted([p for p in persons
                                 if not filter or filter in p.name.lower()][0: limit],
                                key=key_func)
    return filtered


# Catch Path-Parameters with "/../{key}" pattern in the path
# Example: http://localhost:8000/persons/jack
# Returns: {"name":"Jack","age":80}
# Parameters in Request Handlers that are not part of the path
# are assumed to be provided by query-parameters
@app.get("/persons/{name}", response_model=typing.Optional[Person])
def get_person(name: str):
    # use a generator in order to get the first element
    # matching a predicate in a list:
    generator = (p for p in persons if p.name.lower() == name)
    return next(generator, None)


# Example: POST-Request to http://localhost:8000/persons
# Re
@app.post("/persons", response_model=Person)
async def add_person(person: Person) -> Person:
    persons.append(person)
    return person
