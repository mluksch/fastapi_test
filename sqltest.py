# Super simple FastAPI Database integration
import datetime
import typing

import fastapi
import sqlmodel
import uvicorn

metadata = sqlmodel.MetaData()


# create model-subclasses derived from sqlmodel.SQLModel:
# SQLModel-classes are both:
# Pydantic-dataclasses + SqlALchemy-Table-classes
class PersonBase(sqlmodel.SQLModel):
    name: str = sqlmodel.Field(None,
                               # Creates a Table-Index on this field in SQL:
                               index=True,
                               description="The name of the person")
    age: typing.Optional[int]


class PostBase(sqlmodel.SQLModel, table=False):
    id: int = sqlmodel.Field(primary_key=True)
    comment: str


# Define Table classes:


class Person(PersonBase, table=True):
    __table_args__ = {'extend_existing': True}
    id: typing.Optional[int] = sqlmodel.Field(primary_key=True, description="id of person")
    updatedOn: datetime.datetime = sqlmodel.Field(alias="updated_on")
    createdOn: datetime.datetime = sqlmodel.Field(alias="created_on")
    # relationship
    # posts: List["sqltest.Post"] = sqlmodel.Relationship(back_populates="author")


class Post(PostBase, table=True):
    __table_args__ = {'extend_existing': True}
    # foreign key field:
    author_id: int = sqlmodel.Field(foreign_key="person.id")
    # relationships: https://sqlmodel.tiangolo.com/tutorial/relationship-attributes/define-relationships-attributes/
    # use string here due to order of class declaration & cyclic mutual reference:
    # avoids error "class is not defined"
    # author: "sqltest.Person" = sqlmodel.Relationship(back_populates="posts")
    updated_on: datetime.datetime
    created_on: datetime.datetime


# Define FastAPI's Input + Output types
class PersonInput(PersonBase):
    pass


class PersonOutput(PersonBase):
    pass


class PostInput(PostBase):
    authorName: str


class PostOutput(PostBase):
    authorName: str


engine = sqlmodel.create_engine("sqlite:///test.db", future=True, echo=True)

app = fastapi.FastAPI()

try:
    # sqlmodel.SQLModel.metadata.create_all(engine)
    pass
except Exception:
    pass


@app.on_event("startup")
def on_startup():
    pass


# Create all tables (which are subclassed)
sqlmodel.SQLModel.metadata.create_all(engine)


def get_session():
    with sqlmodel.Session(engine) as session:
        yield session


@app.post("/person", response_model=PersonOutput)
def create_person(person: PersonInput, session: sqlmodel.Session = fastapi.Depends(get_session)):
    now = datetime.datetime.now()
    new_person: Person = Person(name=person.name, age=person.age, updated_on=now, created_on=now)
    session.add(new_person)
    session.commit()
    return new_person


if __name__ == "__main__":
    uvicorn.run("sqltest:app", host="0.0.0.0", port=9000, reload=True)
