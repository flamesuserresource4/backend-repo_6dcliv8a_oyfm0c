"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List

# Example schemas (replace with your own):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Blog app schemas

class Sector(BaseModel):
    name: str = Field(..., description="Sector name, e.g., Marketing, Sales")
    slug: str = Field(..., description="URL-friendly unique identifier")
    description: Optional[str] = Field(None, description="Short description of the sector")

class Tool(BaseModel):
    name: str = Field(..., description="Tool name")
    sector_slug: str = Field(..., description="Slug of sector this tool belongs to")
    summary: str = Field(..., description="Short tool summary")
    strengths: List[str] = Field(default_factory=list, description="Key strengths")
    limitations: List[str] = Field(default_factory=list, description="Known limitations")
    website: Optional[HttpUrl] = Field(None, description="Official website")
    pricing: Optional[str] = Field(None, description="Pricing summary")
    rating: Optional[float] = Field(None, ge=0, le=5, description="Editor rating out of 5")

class Comparison(BaseModel):
    sector_slug: str = Field(..., description="Sector slug for this comparison")
    headline: str = Field(..., description="Comparison headline")
    intro: Optional[str] = Field(None, description="Intro paragraph")
    top_tools: List[str] = Field(default_factory=list, description="List of tool names in ranked order")

# Note: The Flames database viewer will automatically:
# 1. Read these schemas from GET /schema endpoint
# 2. Use them for document validation when creating/editing
# 3. Handle all database operations (CRUD) directly
# 4. You don't need to create any database endpoints!
