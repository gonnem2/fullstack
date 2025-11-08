from dataclasses import dataclass

from app.db.models.category import TypesOfCat


@dataclass
class CategoryDTO:
    id: int
    title: str
    user_id: int
    type_of_category: TypesOfCat
