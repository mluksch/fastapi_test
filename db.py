# Take care:
# !!!DB-Models & FastAPI need to be in different files!!!
# Otherwise sqlmodel-magic gets confused with
# mutually dependent Relationships of table

# Super simple FastAPI Database integration
import datetime
import typing

import sqlmodel


# create model-subclasses derived from sqlmodel.SQLModel:
# SQLModel-classes are both:
# Pydantic-dataclasses + SqlALchemy-Table-classes
class Person(sqlmodel.SQLModel, table=True):
    # not required here (because of table=True) unlike in SQLAlchemy:
    # __tablename__ = "person"

    # id is optional in order to insert new Person-objects:
    # see here: https://sqlmodel.tiangolo.com/tutorial/automatic-id-none-refresh/
    id: typing.Optional[int] = sqlmodel.Field(primary_key=True, description="id of person")
    name: str = sqlmodel.Field(None,
                               # Creates a Table-Index on this field in SQL:
                               index=True,
                               # Pass arguments to SQLAlchemy-Column-definition:
                               # unique constraint: https://github.com/tiangolo/sqlmodel/issues/82
                               sa_column_kwargs={"unique": True},
                               description="The name of the person")
    age: typing.Optional[int]
    updated_on: datetime.datetime = sqlmodel.Field(
        # rename table-column-name: but here not needed
        # just for demonstration
        alias="updated_on",
        # default-value set by factory-function:
        default_factory=datetime.datetime.now)
    created_on: datetime.datetime = sqlmodel.Field(alias="created_on",
                                                   # default-value set by factory-function:
                                                   default_factory=datetime.datetime.now)
    # relationship
    posts: typing.List["Post"] = sqlmodel.Relationship(back_populates="author")


class Post(sqlmodel.SQLModel, table=True):
    # not required here (because of table=True) unlike in SQLAlchemy:
    # __tablename__ = "post"
    id: int = sqlmodel.Field(primary_key=True)
    comment: str
    # foreign key field:
    author_id: int = sqlmodel.Field(foreign_key="person.id")
    # relationships: https://sqlmodel.tiangolo.com/tutorial/relationship-attributes/define-relationships-attributes/
    # use string here due to order of class declaration & cyclic mutual reference:
    # avoids error "class is not defined"
    author: Person = sqlmodel.Relationship(
        back_populates="posts")
    updated_on: datetime.datetime = sqlmodel.Field(default_factory=datetime.datetime.now)
    created_on: datetime.datetime = sqlmodel.Field(default_factory=datetime.datetime.now)
