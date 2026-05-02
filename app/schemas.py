from pydantic import HttpUrl, BaseModel, Field

class CheckUrl(BaseModel):
    url: HttpUrl

class CheckCreate(CheckUrl):
    text: str = Field(..., min=3, pattern="^[a-zA-Z0-9_-]+$")

class Update(CheckUrl):
    id: int