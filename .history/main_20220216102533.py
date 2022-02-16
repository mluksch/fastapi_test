# FastApi is built upon Starlette whichs is an ASGI implmentation
# and Uvicorn is a server which is capable of running ASGI-Apps
import uvicorn


# FastApi has some advantages:
# (1) asynchronous/non-blocking i.e. not every request handlers needs to run in its own thread
# and blocks any other executions within the same thread.
# Flask on the other hand is based on WSGI (which is synchronous by default, there is
# also an asynchronous version of WSGI: ASGI)
# (2) built-in data validation
# (3) websocket-support
# (4) automatic documentation of API endpoints

# standard python3 libs used for typing:
import enum
import typing

# FastApi-Lib
# FastAPI implements ASGI interface
# and can be started by any ASGI compliant server
# such as uvicorn:
# "pipenv run uvicorn <file>:<FastApi-App-object> --reload"
import fastapi
import fastapi.encoders as encoders

# Pydantic is mainly a parsing library
# and is used by FastAPI for:
# - Defining Dataclass Types (which are used by FastAPI especially for the Request Body)
# - data validation of input parameter
# - parsing & formatting (dataclass) objects to & from JSON
import pydantic

# Start app by: "pipenv run uvicorn main:app --reload"
# "--reload" for hot-reload on code changes
# Endpoint exposed at: http://localhost:8000
# SwaggerUI-Docs exposed at: http://localhost:8000/docs
app = fastapi.FastAPI()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

######### Types in FastAPI #########
# Typing is essential & important in FastAPI:
# Because all validations & documentation & behaviour
# are determined by types used in the request handler
# For example:
# Types do define what parameters in the request handler
# belong to the request body (BaseModel)
# or to the query parameters

# Declare a Pydantic-Dataclass:
# By deriving from Basemodel
# you get json parsing, formatting, validation, documentation,
# an __init__-constructor with kwargs
# out of the box


class Person(pydantic.BBaseModel):
    name: str
    age: typing.Optional[int]

# Define a Custom-Enum
# Enums are subclass of str + Enum:


class OrderBy(str, enum.Enum):
    AGE = "age"
    NAME = "name"


# Fake data
# normally fetched from a DB:
persons: typing.List[Person] = [Person(**kwargs) for kwargs in [
    {"name": "Judy", "age": 10},
    {"name": "Jeremy", "age": 20},
    {"name": "Max", "age": 30},
    {"name": "Jonas", "age": 50},
    {"name": "Sam", "age": 60},
    {"name": "Ashley", "age": 70},
    {"name": "Jack", "age": 80}
]]

######## Request Handler declaration ########
# The order of request handler declaration is important/relevant
# Request Handler whose paths are matching are chosen first by FastAPI.

# Route: http://localhost:8000
# Returns: {"gruss":"hallo","id":1,"name":"Max"}
#
# The return-value of the request handler will be sent to the client as JSON-response.
# Should return either a dict or a Pydantic-BaseModel-object
# in order to get implicitly formatted by FastAPI to a JSON-response


@app.get("/")
def index():
    """Documentation available at http://localhost:8000/docs
    Returns some random dict
    """
    # explicit encoding is not required here
    # because it is a dict.
    # But normal Python-objects (besides Pydantic-dataclass-objects)
    # needs to get explicitly decoded to JSON
    return encoders.jsonable_encoder({
        "gruss": "hallo",
        "id": 1,
        "name": "Max"
    })

########## Query-Parameters ##########
# Route: http://localhost:8000/persons?filter=j&limit=2&orderby=age
# Returns: [{"name":"Judy","age":10},{"name":"Jeremy","age":20}]
#
# Any parameter that is not found in the path-definition nor
# part of a Custom Pydantic-BaseModel is assumed to be provided as
# Query-Parameter in the Querystring.
#
# All Parameters should be typed!
# Types are used by FastAPI for validation & documentation.
#
# response_model:
# Data that is not part of response_model-Pydantic-Dataclass
# will get filtered out.


@app.get("/persons", response_model=typing.List[Person])
async def items(
        # defining Optional parameter:
        filter: typing.Optional[str] = None,
        limit: int = 10,
        orderby: OrderBy = OrderBy.NAME
):
    """
    Just some Docstring here for SwaggerUi describing the endpoint.

    - Returns all persons based on filter, limited & ordered
    """
    # builtin-function "sorted" returns new list
    def key_func(p: Person) -> typing.Union[str, int]:
        if orderby == OrderBy.NAME:
            return p.name
        elif orderby == OrderBy.AGE:
            return p.age

    filtered: typing.List[Person] = sorted([p for p in persons
                                            if not filter or filter in p.name.lower()][0: limit],
                                           key=key_func)
    return filtered

########## Path-Parameters ##########
# Route: http://localhost:8000/persons/jack
# Returns: {"name":"Jack","age":80}
#
# Parameters that are part of the
# path-definition: "/../{my_key}/.." are called Path-Parameters
# & are provided by kwargs-parameter to the request Handler:


@app.get("/persons/{name}", response_model=typing.Optional[Person])
def get_person(name: str, response: fastapi.Response):
    """
    Will return a Person or 404, if person does not exist
    """
    # use a generator:
    # first element matching a predicate in a list:
    generator = (p for p in persons if p.name.lower() == name)
    first = next(generator, None)
    if not first:
        response.status_code = fastapi.status.HTTP_404_NOT_FOUND
        return None
    return first


# Route: POST-Request to http://localhost:8000/persons
# Re
@app.post("/persons", response_model=Person)
async def add_person(person: Person) -> Person:
    persons.append(person)
    return person
