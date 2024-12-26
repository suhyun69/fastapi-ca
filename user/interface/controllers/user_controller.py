from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr, Field
from containers import Container
from dependency_injector.wiring import inject, Provide
from user.application.user_service import UserService
from datetime import datetime
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from common.auth import CurrentUser, get_current_user, get_admin_user

router = APIRouter(prefix="/users")

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    created_at: datetime
    updated_at: datetime

class CreateUserBody(BaseModel):
    name: str = Field(min_length=2, max_length=32)
    email: str = Field(max_length=64)
    password: str = Field(min_length=8, max_length=32)

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    created_at: datetime
    updated_at: datetime

@router.post("", status_code=201)
@inject
def create_user(
    user: CreateUserBody,
    user_service: UserService = Depends(Provide[Container.user_service]),
) -> UserResponse:
    created_user = user_service.create_user(
        user.name, 
        user.email,
        user.password
    )
    
    return created_user

class UpdateUserBody(BaseModel):
    name: str | None = Field(min_length=2, max_length=32, default=None)
    password: str | None = Field(min_length=8, max_length=32, default=None)

@router.put("", response_model=UserResponse)
@inject
def update_user(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    body: UpdateUserBody,
    user_service: UserService = Depends(Provide[Container.user_service]),
):
    user = user_service.update_user(
        user_id=current_user.id,
        name=body.name,
        password=body.password
    )
    
    return user

class GetUsersResponse(BaseModel):
    total_count: int
    page: int
    users: list[UserResponse]

@router.get("")
@inject
def get_users(
    page: int = 1,
    items_per_page: int = 10,
    current_use: CurrentUser = Depends(get_admin_user),
    user_service: UserService = Depends(Provide[Container.user_service]),
) -> GetUsersResponse:
    total_count, users = user_service.get_users(page, items_per_page)

    return {
        "total_count": total_count,
        "page": page,
        "users": users
    }

@router.delete("", status_code=204)
@inject
def delete_user(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    body: UpdateUserBody,
    user_service: UserService = Depends(Provide[Container.user_service]),
):
    user_service.delete_user(current_user.id)

@router.post("/login")
@inject
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_service: UserService = Depends(Provide[Container.user_service]),
):
    accesss_token = user_service.login(
        form_data.username, 
        form_data.password
    )
    
    return {
        "access_token": accesss_token,
        "token_type": "bearer"
    }