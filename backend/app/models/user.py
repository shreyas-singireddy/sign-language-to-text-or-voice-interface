from datetime import datetime
from pydantic import BaseModel, EmailStr

class UserModel(BaseModel):
    id: str
    name: str
    email: EmailStr
    hashed_password: str
    role: str = 'user'
    createdAt: datetime = datetime.utcnow()
