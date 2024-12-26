from fastapi import APIRouter, Depends
from pydantic import BaseModel
from containers import Container
from dependency_injector.wiring import inject, Provide
from user.application.user_service import UserService
from datetime import datetime

router = APIRouter(prefix="/users")

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    created_at: datetime
    updated_at: datetime

class CreateUserBody(BaseModel):
    name: str
    email: str
    password: str

@router.post("", status_code=201)
@inject
def create_user(
    user: CreateUserBody,
    user_service: UserService = Depends(Provide[Container.user_service]),
):
    created_user = user_service.create_user(
        user.name, 
        user.email,
        user.password
    )
    
    return created_user
