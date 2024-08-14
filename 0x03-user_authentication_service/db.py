#!/usr/bin/env python3
"""DB module for the project
"""
from sqlalchemy import create_engine, tuple_
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from sqlalchemy.orm.exc import NoResultFound
from user import Base, User


class DB:
    """DB class initilize
    """

    def __init__(self) -> None:
        """Initialize a new DB instance
        """
        self._engine = create_engine("sqlite:///a.db")
        Base.metadata.drop_all(self._engine)
        Base.metadata.create_all(self._engine)
        self.__session = None

    @property
    def _session(self) -> Session:
        """session start
        """
        if self.__session is None:
            DBSession = sessionmaker(bind=self._engine)
            self.__session = DBSession()
        return self.__session

    def add_user(self, email: str, hashed_password: str) -> User:
        """ Creates new User to db
            Args:
                - email
                - hashed_password
            Return:
                - new User object
        """
        session = self._session
        try:
            add_user = User(email=email, hashed_password=hashed_password)
            session.add(add_user)
            session.commit()
        except Exception:
            session.rollback()
            add_user = None
        return add_user

    def find_user_by(self, **kwargs) -> User:
        """ Find user with given key
            Args:
                - Attributes to use as search
                  parameters
            Return:
                - User object
        """

        attr_val, keys = [], []
        for att, key in kwargs.items():
            if not hasattr(User, att):
                raise InvalidRequestError()
            attr_val.append(getattr(User, att))
            keys.append(key)

        sess_db = self._session
        query = sess_db.query(User)
        user_find = query.filter(tuple_(*attr_val).in_([tuple(keys)])).first()
        if not user_find:
            raise NoResultFound()
        return user_find

    def update_user(self, user_id: int, **kwargs) -> None:
        """ Searches for user instance using given id parameter
            Args:
                - user_id: user's id
            Return:
                - User instance found
        """
        user = self.find_user_by(id=user_id)
        session = self._session
        for attr, val in kwargs.items():
            if not hasattr(User, attr):
                raise ValueError
            setattr(user, attr, val)
        session.commit()
