from pydantic import HttpUrl, BaseModel, Field

class CheckUrl(BaseModel):
    url: HttpUrl

class CheckCreate(CheckUrl):
    text: str = Field(..., min=3, pattern="^[a-zA-Z0-9_-]+$")

class CheckTemporary(CheckUrl):
    time: int = Field(..., gt=0, le=8760)

class Update(CheckUrl):
    id: int

class CreateQr(BaseModel):
    url: str
    fill_color: str = "#000000"
    back_color: str = "#FFFFFF"
    gradient_type: str | None = None
    gradient_color: str | None = None
    dots_style: str = "square" 
    eye_style: str = 'square'
    border_style: str = "square"
