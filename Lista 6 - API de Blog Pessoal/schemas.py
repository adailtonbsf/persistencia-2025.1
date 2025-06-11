from pydantic import BaseModel
from typing import List

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

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

class CategoryWithPostCount(Category):
    post_count: int

    class Config:
        orm_mode = True

class PostBase(BaseModel):
    title: str
    content: str

class PostCreate(PostBase):
    user_id: int
    category_ids: List[int] = []

class Post(PostBase):
    id: int
    user_id: int
    user: User
    categories: List[Category] = []

    class Config:
        orm_mode = True

class PostWithCommentCount(Post):
    comment_count: int

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
    user: User
    post: Post

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
    user: User
    post: Post

    class Config:
        orm_mode = True