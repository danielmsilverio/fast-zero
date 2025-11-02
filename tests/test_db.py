from dataclasses import asdict

import pytest
from sqlalchemy import select

from fast_zero.models import Todo, User


@pytest.mark.asyncio
async def test_create_user(session, mock_db_time):
    with mock_db_time(model=User) as time:
        new_user = User(
            username='test',
            password='testpassword',
            email='testuser@example.com',
        )
        session.add(new_user)
        await session.commit()

    user = await session.scalar(select(User).where(User.username == 'test'))

    assert asdict(user) == {
        'id': 1,
        'username': 'test',
        'password': 'testpassword',
        'email': 'testuser@example.com',
        'todos': [],
        'created_at': time,
        'updated_at': time,
    }


@pytest.mark.asyncio
async def test_create_todo(session, user):
    todo = Todo(
        title='Test Todo',
        description='This is a test todo item.',
        state='todo',
        user_id=user.id,
    )

    session.add(todo)
    await session.commit()

    todo = await session.scalar(select(Todo))

    assert asdict(todo) == {
        'id': 1,
        'title': 'Test Todo',
        'description': 'This is a test todo item.',
        'state': 'todo',
        'user_id': user.id,
        'created_at': todo.created_at,
        'updated_at': todo.updated_at,
    }


@pytest.mark.asyncio
async def test_user_todo_relationship(session, user: User):
    todo = Todo(
        title='First Todo',
        description='First todo item.',
        state='todo',
        user_id=user.id,
    )

    session.add(todo)
    await session.commit()
    await session.refresh(user)

    user = await session.scalar(select(User).where(User.id == user.id))

    assert user.todos == [todo]
