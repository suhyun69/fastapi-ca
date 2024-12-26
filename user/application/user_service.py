from ulid import ULID
from datetime import datetime
from user.domain.user import User
from user.infra.repository.user_repo import UserRepository
from fastapi import HTTPException
from utils.crypto import Crypto
from dependency_injector.wiring import Provide, inject


class UserService:
    @inject
    def __init__(self, user_repo: UserRepository = Provide["user_repo"]):
        self.user_repo = user_repo
        self.ulid = ULID()
        self.crypto = Crypto()

    def create_user(
            self, 
            name: str, 
            email: str, 
            password: str,
            memo: str | None = None
        ) -> User:
        _user = None
        
        try:
            _user = self.user_repo.find_by_email(email)
        except HTTPException as e:
            if e.status_code != 422:
                raise e
        
        if _user:
            raise HTTPException(status_code=400, detail="User already exists")
        
        hashed_password = self.crypto.encrypt(password)
        new_user = User(
            id=self.ulid.generate(),
            name=name, 
            email=email, 
            password=hashed_password, 
            memo=memo,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        self.user_repo.save(new_user)
        return new_user
    
    def update_user(
            self,
            user_id: str,
            name: str | None = None,
            password: str | None = None,
    ):
        user = self.user_repo.find_by_id(user_id)
        
        if name:
            user.name = name
        if password:
            user.password = self.crypto.encrypt(password)
        user.updated_at = datetime.utcnow()

        self.user_repo.update(user)

        return user
    
    def get_users(self, page: int, items_per_page: int) -> tuple[int, list[User]]:
        users = self.user_repo.get_users(page, items_per_page)
        return users
    
    def delete_user(self, user_id: str):
        self.user_repo.delete(user_id)