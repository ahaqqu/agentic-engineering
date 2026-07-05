from pydantic import BaseModel, Field


class ItemCreateBody(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
