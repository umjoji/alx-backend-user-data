#!/usr/bin/env python3

"""DB module."""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import InvalidRequestError

from user import Base, User


class DB:
    """DB class."""

    def __init__(self) -> None:
        """Initialise a new DB instance"""

        self._engine = create_engine("sqlite:///a.db", echo=True)
        # Create all tables in the engine.
        # This is equivalent to "Create Table"
        # statements in raw SQL.
        Base.metadata.drop_all(self._engine)
        Base.metadata.create_all(self._engine)
        self.__session = None

    @property
    def _session(self) -> Session:
        """Memoized section object"""
        if self.__session is None:
            DBSession = sessionmaker(bind=self._engine)
            self.__session = DBSession()
        return self.__session

    def add_user(self, email: str, hashed_password: str) -> User:
        """
        Create a user object and save it to the db
        Args:
            email(str): user's email addreess
            hashed_passwword(str): password hashed by bcrypt hashpw
        Return:
            Newly created user object
        """

        user = User(email=email, hashed_password=hashed_password)
        self._session.add(user)
        try:
            self._session.commit()
        except Exception as e:  # pylint: disable=broad-except
            print('Error adding user', repr(e))
        return user

    def find_user_by(self, **kwargs) -> User:
        """
        Return a user who has an attribute matching the kwargs
        Args:
            attributes (dict): a dictionary of attributes to match the user
        Return:
            matching user or raise error
        """
        all_users = self._session.query(User)
        for k, v in kwargs.items():
            if k not in User.__dict__:
                raise InvalidRequestError
            for usr in all_users:
                if getattr(usr, k) == v:
                    return usr
        raise NoResultFound

    def update_user(self, user_id: int, **kwargs) -> None:
        """
        Update a user's attributes
        Args:
            user_id (int): user's id
            kwargs (dict): dict of key, value pairs representing
                            the attributes to update and the values
                            to update them with
        Return:
            None
        """

        try:
            usr = self.find_user_by(id=user_id)
        except NoResultFound:
            raise ValueError()
        for k, v in kwargs.items():
            if hasattr(usr, k):
                setattr(usr, k, v)
            else:
                raise ValueError
        self.__session.commit()
