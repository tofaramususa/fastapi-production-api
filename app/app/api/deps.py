# Dependency injection utilities for the API
from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from motor.core import AgnosticDatabase

from app import crud, models, schemas
from app.core.config import settings
from app.database.session import MongoDatabase


# get_db provides a database connection for dependency injection
def get_db() -> Generator:
    """
    Provides a database connection for dependency injection.
    Yields a MongoDB database instance.
    """
    try:
        db = MongoDatabase()
        yield db
    finally:
        pass


# get_user_id provides a test user ID for development purposes
async def get_user_id():
    """
    A simple function that returns a fixed user ID for testing purposes.
    In a real application, this would parse a token or session.
    """
    # Return a constant test user ID
    return "test-user-id-123"


# is_admin provides a test admin status for development purposes
async def is_admin():
    """
    A simple function that always returns True for testing purposes.
    In a real application, this would check the user's permissions.
    """
    # Always return True to grant admin access during testing
    return True
