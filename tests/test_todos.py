from http import HTTPStatus

import factory.fuzzy
import pytest

from fast_zero.models import Todo, TodoState


class TodoFactory(factory.Factory):
    class Meta:
        model = Todo

    title = factory.Faker('sentence', nb_words=4)
    description = factory.Faker('paragraph', nb_sentences=2)
    state = factory.fuzzy.FuzzyChoice([state for state in TodoState])
    user_id = 1


def test_create_todo(client, token, mock_db_time):
    with mock_db_time(model=Todo) as time:
        response = client.post(
            '/todos/',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'title': 'Test Todo',
                'description': 'This is a test todo item',
                'state': 'draft',
            },
        )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'title': 'Test Todo',
        'description': 'This is a test todo item',
        'state': 'draft',
        'created_at': time.isoformat(),
        'updated_at': time.isoformat(),
    }


@pytest.mark.asyncio
async def test_create_todo_missing_fields(client, token):
    response = client.post(
        '/todos/',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'title': 'Test Todo',
            # 'description' is optional
            # 'state' is missing
        },
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json() == {
        'detail': [
            {
                'input': {
                    'title': 'Test Todo',
                },
                'loc': ['body', 'state'],
                'msg': 'Field required',
                'type': 'missing',
            }
        ]
    }


@pytest.mark.asyncio
async def test_create_todo_invalid_state(client, token):
    response = client.post(
        '/todos/',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'title': 'Test Todo',
            'description': 'This is a test todo item',
            'state': 'invalid_state',
        },
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json() == {
        'detail': [
            {
                'input': 'invalid_state',
                'loc': ['body', 'state'],
                'msg': "Input should be 'draft', 'todo', 'doing', 'done' or 'trash'",  # noqa: E501
                'type': 'enum',
                'ctx': {
                    'expected': "'draft', 'todo', 'doing', 'done' or 'trash'",
                },
            }
        ]
    }


@pytest.mark.asyncio
async def test_list_todos_should_return_5_todos(session, client, user, token):
    # Create 5 todos for the user
    expected_todos = 5
    session.add_all(TodoFactory.create_batch(5, user_id=user.id))
    await session.commit()

    response = client.get(
        '/todos/',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert 'todos' in data
    assert len(data['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_pagination_should_return_2_todos(
    session, client, user, token
):
    # Create 5 todos for the user
    expected_todos = 2
    session.add_all(TodoFactory.create_batch(5, user_id=user.id))
    await session.commit()

    response = client.get(
        '/todos/?offset=1&limit=2',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert 'todos' in data
    assert len(data['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_with_title_filter_should_return_5_todos(
    session, client, user, token
):
    # Create 5 todos for the user
    expected_todos = 5
    session.add_all(
        TodoFactory.create_batch(5, user_id=user.id, title='Test todo 1')
    )
    await session.commit()

    response = client.get(
        '/todos/?title=Test todo',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert 'todos' in data
    assert len(data['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_with_description_filter_should_return_5_todos(
    session, client, user, token
):
    # Create 5 todos for the user
    expected_todos = 5
    session.add_all(
        TodoFactory.create_batch(5, user_id=user.id, description='description')
    )
    await session.commit()

    response = client.get(
        '/todos/?description=desc',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert 'todos' in data
    assert len(data['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_with_state_filter_should_return_5_todos(
    session, client, user, token
):
    # Create 5 todos for the user
    expected_todos = 5
    session.add_all(
        TodoFactory.create_batch(5, user_id=user.id, state=TodoState.draft)
    )
    await session.commit()

    response = client.get(
        '/todos/?state=draft',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert 'todos' in data
    assert len(data['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_filter_combined_should_return_5_todos(
    session, client, user, token
):
    # Create 5 todos for the user
    expected_todos = 5
    session.add_all(
        TodoFactory.create_batch(
            5,
            user_id=user.id,
            title='Test todo combined',
            description='combined description',
            state=TodoState.done,
        )
    )

    session.add_all(
        TodoFactory.create_batch(
            3,
            user_id=user.id,
            title='Outhert title',
            description='outher description',
            state=TodoState.todo,
        )
    )

    await session.commit()

    response = client.get(
        '/todos/?title=Test&description=combined&state=done',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert 'todos' in data
    assert len(data['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_valid_fields_returned(
    session, client, user, token, mock_db_time
):
    with mock_db_time(model=Todo) as time:
        todo = TodoFactory(
            user_id=user.id,
            title='Test Title',
            description='Test Description',
            state=TodoState.doing,
        )

        session.add(todo)
        await session.commit()
        await session.refresh(todo)

    response = client.get(
        '/todos/',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert 'todos' in data
    assert len(data['todos']) == 1

    todo_data = data['todos'][0]

    assert todo_data == {
        'id': todo.id,
        'title': 'Test Title',
        'description': 'Test Description',
        'state': 'doing',
        'created_at': time.isoformat(),
        'updated_at': time.isoformat(),
    }


@pytest.mark.asyncio
async def test_list_todos_error_when_title_length_less_than_3_chars(
    session, client, user, token
):
    response = client.get(
        '/todos/?title=ab',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json() == {
        'detail': [
            {
                'input': 'ab',
                'loc': ['query', 'title'],
                'msg': 'String should have at least 3 characters',
                'type': 'string_too_short',
                'ctx': {'min_length': 3},
            }
        ]
    }


@pytest.mark.asyncio
async def test_list_todos_error_when_title_length_greater_than_20_chars(
    session, client, user, token
):
    response = client.get(
        '/todos/?title=' + 'a' * 21,
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json() == {
        'detail': [
            {
                'input': 'a' * 21,
                'loc': ['query', 'title'],
                'msg': 'String should have at most 20 characters',
                'type': 'string_too_long',
                'ctx': {'max_length': 20},
            }
        ]
    }


@pytest.mark.asyncio
async def test_list_todos_error_when_description_length_less_than_3_chars(
    session, client, user, token
):
    response = client.get(
        '/todos/?description=ab',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json() == {
        'detail': [
            {
                'input': 'ab',
                'loc': ['query', 'description'],
                'msg': 'String should have at least 3 characters',
                'type': 'string_too_short',
                'ctx': {'min_length': 3},
            }
        ]
    }


@pytest.mark.asyncio
async def test_list_todos_error_when_description_length_greater_than_20_chars(
    session, client, user, token
):
    response = client.get(
        '/todos/?description=' + 'a' * 21,
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json() == {
        'detail': [
            {
                'input': 'a' * 21,
                'loc': ['query', 'description'],
                'msg': 'String should have at most 20 characters',
                'type': 'string_too_long',
                'ctx': {'max_length': 20},
            }
        ]
    }


@pytest.mark.asyncio
async def test_patch_todo(session, client, user, token):
    todo = TodoFactory(user_id=user.id)

    session.add(todo)
    await session.commit()
    await session.refresh(todo)

    response = client.patch(
        f'/todos/{todo.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={'title': 'Updated Title'},
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()

    assert data == {
        'id': todo.id,
        'title': 'Updated Title',
        'description': todo.description,
        'state': todo.state.value,
        'created_at': todo.created_at.isoformat(),
        'updated_at': data['updated_at'],
    }


@pytest.mark.asyncio
async def test_patch_todo_not_found(client, token):
    response = client.patch(
        '/todos/999',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'title': 'Updated Title',
            'description': 'Updated Description',
            'state': 'done',
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Todo not found'}


@pytest.mark.asyncio
async def test_delete_todo(session, client, user, token):
    todo = TodoFactory(user_id=user.id)

    session.add(todo)
    await session.commit()
    await session.refresh(todo)

    response = client.delete(
        f'/todos/{todo.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Todo deleted successfully'}


@pytest.mark.asyncio
async def test_delete_todo_not_found(client, token):
    response = client.delete(
        '/todos/999',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Todo not found'}
