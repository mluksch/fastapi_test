# Super simple FastAPI Database integration
import typing

import fastapi
import pydantic
import sqlmodel
import uvicorn

# Take care:
# !!!DB-Models & FastAPI need to be in different files!!!
# Otherwise sqlmodel-magic gets confused with
# mutually dependent Relationships of table
import db


# Define FastAPI's Input + Output types:
class PersonInput(pydantic.BaseModel):
    age: typing.Optional[int]
    name: str


class PostOutput(pydantic.BaseModel):
    id: int
    comment: str


class PersonOutput(pydantic.BaseModel):
    id: str
    name: str
    age: typing.Optional[int]
    posts: typing.Optional[typing.List[PostOutput]]


class PostInput(pydantic.BaseModel):
    authorName: str
    comment: str


app = fastapi.FastAPI()
engine = sqlmodel.create_engine("sqlite:///test.db", future=True, echo=True)


@app.on_event("startup")
def on_startup():
    sqlmodel.SQLModel.metadata.create_all(engine)


# Factory function for sessions
# used to for session-injection into request handler
def get_session():
    with sqlmodel.Session(engine) as session:
        yield session


@app.post("/person", response_model=PersonOutput)
def create_person(
        # request body data:
        person: PersonInput,
        # inject a session:
        session: sqlmodel.Session = fastapi.Depends(get_session)):
    new_person: db.Person = db.Person(name=person.name, age=person.age)
    session.add(new_person)
    session.commit()
    # normally SQLAlchemy refetches data from the DB after a commit,
    # if fields are getting accessed.
    # But that SQLAlchemy-magic is not triggered here,
    # if the model is returned to FastAPI.
    # We need an explicit refresh therefore
    session.refresh(new_person)
    return new_person


@app.get("/person", response_model=typing.List[PersonOutput])
def get_persons(
        sort_by: str = fastapi.Query(default="name",
                                     # visible in the /docs:
                                     description="Sort by name or age",
                                     # alias used as query parameter:
                                     alias="sortby"),
        session: sqlmodel.Session = fastapi.Depends(get_session)
):
    # scalars(): transform results to object.property-syntax instead dicts
    # otherwise Pydantic cannot transform results to json:
    return session.execute(sqlmodel.select(db.Person).order_by(sort_by)).scalars().all()


import sqlalchemy.orm as orm


@app.get("/person/{name}", summary="get a person by his/her name", response_model=PersonOutput)
def get_person(name: str, session: sqlmodel.Session = fastapi.Depends(get_session)):
    # - one() throws an Exception, if no result has been found
    # - first() returns None, if no result has been found
    # Important: ALways use scalars()!!
    # Since relationships are by default lazily loaded & not fetched until
    # the fields are actually accessed, we need to
    # explicitly tell sqlAlchemy to fetch all relationships:
    # "options(orm.selectinload(db.Person.posts))"
    return session.execute(sqlmodel.select(db.Person).options(orm.selectinload(db.Person.posts)).where(
        db.Person.name == name)).scalars().one()


@app.post("/post", summary="Creates a Post", response_model=PostOutput)
def create_post(new_post: PostInput, session: sqlmodel.Session = fastapi.Depends(get_session)):
    author = session.execute(sqlmodel.select(db.Person).where(db.Person.name == new_post.authorName)).scalars().one()
    post = db.Post(comment=new_post.comment, author=author)
    session.add(post)
    session.commit()
    session.refresh(post)
    return post


if __name__ == "__main__":
    uvicorn.run("02_fastapi_with_db:app", host="0.0.0.0", port=8000, reload=True)
