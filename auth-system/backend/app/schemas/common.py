from sqlmodel import SQLModel
from typing import Optional

class Message(SQLModel):
    message: str
    detail: Optional[str] = None # Optional additional detail

# You can add other common response/request schemas here, e.g.
# class DetailResponse(SQLModel):
#     detail: str
