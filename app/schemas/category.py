from typing import List

from pydantic import BaseModel

from app.db.models.category import TypesOfCat


class CreateCategory(BaseModel):
    title: str
    type_of_category: TypesOfCat


class CategoryResponse(BaseModel):
    id: int
    title: str
    user_id: int
    type_of_category: TypesOfCat


class CategoriesResponse(BaseModel):
    categories: List[CategoryResponse]
    skip: int
    limit: int


class CategoryUpdate(BaseModel):
    title: str
    type_of_category: TypesOfCat
