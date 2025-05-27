from typing import Optional, List
from pydantic import BaseModel


class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

    class Config:
        orm_mode = True

class PostBase(BaseModel):
    title: str
    content: str

class PostCreate(PostBase):
    category_ids: Optional[List[int]] = []

class PostUpdate(PostBase):
    title: Optional[str] = None
    content: Optional[str] = None
    category_ids: Optional[List[int]] = None

class Post(PostBase):
    id: int
    user_id: int
    categories: List[int] = []

    class Config:
        orm_mode = True

class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int

    class Config:
        orm_mode = True

class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    pass

class Comment(CommentBase):
    id: int
    post_id: int
    user_id: int

    class Config:
        orm_mode = True

class LikeBase(BaseModel):
    pass

class LikeCreate(LikeBase):
    pass

class Like(LikeBase):
    id: int
    post_id: int
    user_id: int

    class Config:
        orm_mode = True