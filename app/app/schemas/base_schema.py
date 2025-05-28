# Enable Python's type annotation features, allowing for forward references in type hints
from __future__ import annotations

# Import required Pydantic components for data validation and model creation
from pydantic import ConfigDict, BaseModel, Field

# Import UUID for unique identifier handling
from uuid import UUID

# Import date and datetime for temporal data handling
from datetime import date, datetime

# Import json for JSON data manipulation (though not directly used in this file)
import json

# Import custom enum types from the application
from app.schema_types import BaseEnum


class BaseSchema(BaseModel):
    """Base schema class that all other schemas inherit from."""

    model_config = ConfigDict(
        from_attributes=True,
        exclude_none=True,  # This will exclude null values from responses by default
        populate_by_name=True,
    )

    @property
    def as_db_dict(self):
        """
        Converts the model to a database-friendly dictionary format.
        - Excludes default values
        - Excludes None values
        - Excludes 'identifier' and 'id' fields initially
        - Converts UUID fields to hexadecimal strings
        """
        to_db = self.model_dump(
            exclude_defaults=True, exclude_none=True, exclude={"identifier", "id"}
        )  # noqa
        # Convert UUID fields (id and identifier) to hexadecimal strings if they exist
        for key in ["id", "identifier"]:
            if key in self.model_dump().keys():
                to_db[key] = self.model_dump()[key].hex
        return to_db


class MetadataBaseSchema(BaseSchema):
    """
    Base schema for metadata with optional fields.
    Following Dublin Core Metadata Initiative (DCMI) specifications.
    """

    # Title field - optional string
    title: str | None = Field(
        None, description="A human-readable title given to the resource."
    )  # noqa

    # Description field - optional string
    description: str | None = Field(
        None,
        description="A short description of the resource.",
    )

    # Active status field - optional boolean, defaults to True
    isActive: bool | None = Field(
        default=True, description="Whether the resource is still actively maintained."
    )  # noqa

    # Privacy status field - optional boolean, defaults to True
    isPrivate: bool | None = Field(
        default=True,
        description="Whether the resource is private to team members with appropriate authorisation.",  # noqa
    )


class MetadataBaseCreate(MetadataBaseSchema):
    """
    Schema for creating new metadata entries.
    Inherits all fields from MetadataBaseSchema without modification.
    Used when creating new resources where identifier is not yet assigned.
    """

    pass


class MetadataBaseUpdate(MetadataBaseSchema):
    """
    Schema for updating existing metadata entries.
    Extends MetadataBaseSchema by requiring an identifier.
    """

    # Required UUID field for identifying the resource to update
    identifier: UUID = Field(
        ..., description="Automatically generated unique identity for the resource."
    )


class MetadataBaseInDBBase(MetadataBaseSchema):
    """
    Schema representing how metadata is stored in the database.
    All fields are required and non-optional.
    """

    # Required UUID field for unique identification
    identifier: UUID = Field(
        ..., description="Automatically generated unique identity for the resource."
    )

    # Required date field for creation timestamp
    createdAt: date = Field(
        ..., description="Automatically generated date resource was created."
    )

    # Required boolean field for active status
    isActive: bool = Field(
        ..., description="Whether the resource is still actively maintained."
    )

    # Required boolean field for privacy status
    isPrivate: bool = Field(
        ...,
        description="Whether the resource is private to team members with appropriate authorisation.",
    )

    # Configure model to work with ORM by allowing creation from attributes
    model_config = ConfigDict(from_attributes=True)
