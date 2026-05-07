from pydantic import HttpUrl, BaseModel, Field
from typing import Optional


class CheckUrl(BaseModel):
    url: HttpUrl


class CheckCreate(CheckUrl):
    text: str | None = Field(
        default=None, min_length=3, pattern="^([a-zA-Z0-9_-]{3,})?$", examples=[None]
    )


class CheckTemporary(CheckUrl):
    time: int | None = Field(default=None, gt=0, le=8760, examples=[None])


class Update(CheckUrl):
    id: int


class CheckAll(CheckTemporary, CheckCreate):
    pass


class CreateQr(BaseModel):
    url: str
    fill_color: str = "#000000"
    back_color: str = "#FFFFFF"
    gradient_type: str | None = None
    gradient_color: str | None = None
    dots_style: str = "square"
    eye_style: str = "square"
    border_style: str = "square"


class CheckAuth(BaseModel):
    login: str = Field(min_length=3, max_length=30)
    password: str = Field(min_length=5, max_length=50)
