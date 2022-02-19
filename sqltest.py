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


class PersonOutput(pydantic.BaseModel):
    id: str
    name: str
    age: typing.Optional[int]


class PostInput(pydantic.BaseModel):
    authorName: str


class PostOutput(pydantic.BaseModel):
    authorName: str


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
        session: sqlmodel.Session = fastapi.Depends(get_session)):
    # scalars(): transform results to object.property-syntax instead dicts
    # otherwise Pydantic cannot transform results to json:
    return session.execute(sqlmodel.select(db.Person)).scalars().all()


if __name__ == "__main__":
    uvicorn.run("sqltest:app", host="0.0.0.0", port=9000, reload=True)
