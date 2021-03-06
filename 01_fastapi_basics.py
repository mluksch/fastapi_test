"""
Testing out FastAPI
"""
# standard python3 libs used for typing:
import datetime
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
# - data validation
# - parsing/formatting objects to/from JSON
# - BaseModel-subclasses are expected in the request body
import pydantic
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

# Start app by: "pipenv run uvicorn main:app --reload"
# "--reload" for hot-reload on code changes
# Endpoint exposed at: http://localhost:8000
# SwaggerUI-Docs exposed at: http://localhost:8000/docs
app = fastapi.FastAPI()

if __name__ == "__main__":
    uvicorn.run("01_fastapi_basics:app", host="0.0.0.0", port=8000, reload=True)


######### Types in FastAPI #########
# Typing is essential & important in FastAPI:
# Because all validations & documentation & behaviour
# are determined by types used in the request handler
# For example:
# Types do define what parameters in the request handler
# belong to the request body (BaseModel)
# or to the query parameters


class Person(pydantic.BaseModel):
    """
    Declare a Pydantic-Dataclass:
    By deriving from Basemodel
    you get json parsing, formatting, validation, documentation,
    an __init__-constructor with kwargs, object.property-access
    out of the box
    """
    name: str
    age: typing.Optional[int]


class OrderBy(str, enum.Enum):
    """
    Define a Custom-Enum
    Enums are subclass of str + Enum:
    """
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

# Metadata about the endpoint, such as:
# summary, description, tags, response_model are put into the Route-decorator
@app.get("/",
         # put the endpoint into categories into the /docs by tags
         tags=["senseless index endpoint"],
         # Summary visible on top-level on the /docs-page
         summary="My senseless endpoint visible in the docs",
         # description can also put into the docstring below
         description="Description hidden the details of the endpoint doc"
         )
# However request-data, response-data are put into the parameter-list:         
def index():
    # Docstring of the request handler is not visible
    """
    Description in the docstring
    ALternative place for the endpoint description for multiline text.
    Otherwise any onliner description can be easily put in the decorator alternatively.
    However the docstring description will get hidden/shadowed on /docs-page, 
    if the description had already been passed to the decorator
    in the decorator

    **Double stars** make things bold in the description,
    just like in a normal docstring

    - Hyphen for listing texts just like in normal docstring
    - Hyphen

    - **arg1** My 1st argument
    - **arg2** My 2nd argument
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


#### Adding Metadata to single Parameters
# by assigning Metadata as default parameter #####
# (1) Route-Parameters
# (2) Query-Parameters:
# def index(arg = Query(None, title="My title doesnt show up", description="My description")
# (3) Body-Parameters


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

# In the Route-Decorator provide Metadata about the endpoint,
# used for validation, parsing/formatting (response_model)
# /docs-page (summary, tags, description)
@app.get("/persons", response_model=typing.List[Person], tags=["persons", "list"], summary="List all persons")
# In the Request-Handler provide the parameters/data itself:
async def items(
        # defining Optional parameter:
        # filter_by: typing.Optional[str] = None,

        # Add query-parameter metadata
        # (Query-Parameter with Metadata: title + description + alias + validators)
        filter_by: typing.Optional[str] = fastapi.Query(None, title="Title: Not displayed in the /docs",
                                                        description="Description: Displayed in the /docs",
                                                        # alias used as query parameter
                                                        alias="filter",
                                                        # some validators:
                                                        # doesnt make sense here though
                                                        min_length=3,
                                                        max_length=10,
                                                        regex="(name|age)"
                                                        ),
        # Assigning default values to Parameters:
        # (Query-Parameter without any Metadata)
        limit: int = 10,
        # Assigning default values to Parameters:
        # (Query-Parameter with Metadata)
        order_by: OrderBy = fastapi.Query(OrderBy.NAME, description="Order by age or name")
):
    """
    Alternative place for the description instead of in the decorator. Just some Docstring
    here for SwaggerUi describing the endpoint.
    Returns all persons based on filter, limited & ordered.

    - **filter_by** optional searchterm for person name
    - **limit** max result size
    - **order_by** either "name" or "age"
    """

    # builtin-function "sorted" returns new list
    def key_func(person: Person) -> typing.Union[str, int]:
        if order_by == OrderBy.NAME:
            return person.name
        elif order_by == OrderBy.AGE:
            return person.age

    filtered: typing.List[Person] = sorted([p for p in persons
                                            if not filter_by or filter_by in p.name.lower()][0: limit],
                                           key=key_func)
    return filtered


########## Path-Parameters ##########
# Route: http://localhost:8000/persons/jack
# Returns: {"name":"Jack","age":80}
#
# Parameters that are part of the
# path-definition: "/../{my_key}/.." are called Path-Parameters
# & are provided by kwargs-parameter to the request Handler:
@app.get("/persons/{name}", response_model=typing.Optional[Person],
         tags=["persons", "one"],
         summary="Get a person's data")
def get_person(response: fastapi.Response,
               # add path-parameter metadata (analogue to query parameters)
               name: str = fastapi.Path(None,
                                        description="The name of the person",
                                        # some validators:
                                        min_length=3,
                                        max_length=10,
                                        # regex: only letters allowed, min. 3 letters
                                        regex='^[a-zA-Z]{3,}$'
                                        )):
    """
    Will return a Person or 404, if person does not exist
    """
    # use a generator:
    # first element matching a predicate in a list:
    generator = (p for p in persons if p.name.lower() == name)
    first = next(generator, None)
    if not first:
        # change statuscode on fastapi.Response
        # passed as argument to request handler
        response.status_code = fastapi.status.HTTP_404_NOT_FOUND
        return None
    return first


########## Body-Parameter ##########
# Route: POST-Request to http://localhost:8000/persons
@app.post("/persons", response_model=Person,
          tags=["persons", "create"],
          summary="Create a new person here")
async def add_person(
        # Add metadata for body-parameter (analogue to Query-Metadata)
        person: Person = fastapi.Body(None,
                                      title="Not visible in /docs",
                                      description="Not visible in /docs")
) -> Person:
    """
    Here the arguments:
    - **name** mandatory string
    - **age** optional int
    """
    persons.append(person)
    return person


# Using Routers in FastAPI for separating paths from each other
# You can mount Routers to the FastAPI-app.
post_router = fastapi.APIRouter(prefix="/posts", tags=["posts"])


class Post(pydantic.BaseModel):
    id: int
    text: str
    author: Person
    date: datetime.datetime


posts: typing.List[Post] = [
    Post(id=0, text="Hello how are you?",
         author=persons[0], date=datetime.datetime.now() - datetime.timedelta(days=10)),
    Post(id=1, text="Im fine",
         author=persons[1], date=datetime.datetime.now() - datetime.timedelta(days=9)),
    Post(id=2, text="Nice to meet you",
         author=persons[0], date=datetime.datetime.now() - datetime.timedelta(days=8))
]


@post_router.get("/", tags=["list"], response_model=typing.List[Post], description="List all Posts")
async def get_posts():
    return posts


@post_router.get("/{post_id}", tags=["one"], response_model=typing.Optional[Post])
async def get_post(post_id: int, response: fastapi.Response):
    # next takes a generator and a default value which prevents raising an exception
    # using a generator comprehension/expression
    # similar to python's list comprehension
    # but lazily evaluated.
    # With generator expressions Python can express
    # constructs such as infinite sequences
    first = next((post for post in posts if post.id == post_id), None)
    if not first:
        response.status_code = fastapi.status.HTTP_404_NOT_FOUND
        return None
    return first


# Make id optional in Post-class


class NewPost(pydantic.BaseModel):
    text: str
    author_name: str


@post_router.post("/", tags=["create"], summary="This creates a new post")
async def create_post(new_post: NewPost, response: fastapi.Response):
    """
    Creates a new Post
    """
    author_person = next(
        (person for person in persons if person.name == new_post.author_name), None)
    if not author_person:
        response.status_code = fastapi.status.HTTP_404_NOT_FOUND
        return None
    created_post = Post(id=len(posts), text=new_post.text,
                        author=author_person, date=datetime.datetime.now())
    posts.append(created_post)
    return created_post


app.include_router(post_router)
