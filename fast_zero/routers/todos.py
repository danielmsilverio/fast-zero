from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fast_zero.database import get_session
from fast_zero.models import Todo, User
from fast_zero.schemas import (
    FilterTodo,
    Message,
    TodoList,
    TodoPublic,
    TodoSchema,
    TodoUpdate,
)
from fast_zero.security import get_current_user

router = APIRouter(prefix='/todos', tags=['todos'])

Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/', response_model=TodoPublic, status_code=HTTPStatus.CREATED)
async def create_todo(
    todo: TodoSchema, session: Session, current_user: CurrentUser
):
    db_todo = Todo(
        title=todo.title,
        description=todo.description,
        state=todo.state,
        user_id=current_user.id,
    )

    session.add(db_todo)
    await session.commit()
    await session.refresh(db_todo)

    return db_todo


@router.get('/', response_model=TodoList)
async def list_todos(
    session: Session,
    current_user: CurrentUser,
    filters: Annotated[FilterTodo, Query()],
):
    query = select(Todo).where(Todo.user_id == current_user.id)

    if filters.title:
        query = query.where(Todo.title.contains(filters.title))
    if filters.description:
        query = query.where(Todo.description.contains(filters.description))
    if filters.state:
        query = query.where(Todo.state == filters.state)

    todos = await session.scalars(
        query.offset(filters.offset).limit(filters.limit)
    )

    return {'todos': todos.all()}


@router.patch('/{todo_id}', response_model=TodoPublic)
async def patch_todo(
    todo_id: int,
    session: Session,
    user: CurrentUser,
    todo: TodoUpdate,
):
    db_todo = await session.scalar(
        select(Todo).where(Todo.user_id == user.id, Todo.id == todo_id)
    )

    if not db_todo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Todo not found'
        )

    for field, value in todo.model_dump(exclude_unset=True).items():
        setattr(db_todo, field, value)

    session.add(db_todo)
    await session.commit()
    await session.refresh(db_todo)

    return db_todo


@router.delete('/{todo_id}', response_model=Message)
async def delete_todo(
    todo_id: int,
    session: Session,
    user: CurrentUser,
):
    db_todo = await session.scalar(
        select(Todo).where(Todo.user_id == user.id, Todo.id == todo_id)
    )

    if not db_todo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Todo not found'
        )

    await session.delete(db_todo)
    await session.commit()

    return {'message': 'Todo deleted successfully'}
