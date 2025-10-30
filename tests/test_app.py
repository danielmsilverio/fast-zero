from http import HTTPStatus

from fast_zero.schemas import UserPublic


def test_root_dev_Retornar_ok_e_ola_mundo(client):
    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Olá, Mundo!'}


def test_create_user(client):
    user_data = {
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'testpassword',
    }

    response = client.post('/users/', json=user_data)

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'username': 'testuser',
        'id': 1,
        'email': 'testuser@example.com',
    }


def test_create_user_conflict_email(client, user):
    user_data = {
        'username': 'newuser',
        'email': user.email,
        'password': 'newpassword',
    }

    response = client.post('/users/', json=user_data)

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Email already registered'}


def test_create_user_conflict_username(client, user):
    user_data = {
        'username': user.username,
        'email': 'newemail@example.com',
        'password': 'newpassword',
    }

    response = client.post('/users/', json=user_data)

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username already registered'}


def test_get_users(client):
    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': []}


def test_get_users_with_existing_user(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get('/users/')
    assert response.json() == {'users': [user_schema]}


def test_get_user(client, user):
    response = client.get(f'/users/{user.id}')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': user.username,
        'id': user.id,
        'email': user.email,
    }


def test_get_user_not_found(client):
    response = client.get('/users/999')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_update_user(client, user):
    updated_user_data = {
        'username': 'updateduser',
        'email': 'updateduser@example.com',
        'password': 'updatedpassword',
    }

    response = client.put(f'/users/{user.id}', json=updated_user_data)

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'updateduser',
        'id': user.id,
        'email': 'updateduser@example.com',
    }


def test_update_user_conflict(client, user):
    client.post(
        '/users/',
        json={
            'username': 'anotheruser',
            'email': 'anotheruser@example.com',
            'password': 'anotherpassword',
        },
    )

    response = client.put(
        f'/users/{user.id}',
        json={
            'username': 'anotheruser',
            'email': user.email,
            'password': 'newpassword',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {
        'detail': 'Username or email already registered'
    }


def test_update_user_not_found(client):
    updated_user_data = {
        'username': 'nonexistentuser',
        'email': 'nonexistentuser@example.com',
        'password': 'nonexistentpassword',
    }

    response = client.put('/users/999', json=updated_user_data)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_delete_user(client, user):
    response = client.delete(f'/users/{user.id}')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted successfully'}


def test_delete_user_not_found(client):
    response = client.delete('/users/999')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}
