from http import HTTPStatus


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


def test_get_users(client):
    # depende do teste anterior para criar um usuário, isso será corrigido
    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'users': [
            {
                'id': 1,
                'username': 'testuser',
                'email': 'testuser@example.com',
            }
        ]
    }


def test_update_user(client):
    # depende do teste anterior para criar um usuário, isso será corrigido
    updated_user_data = {
        'username': 'updateduser',
        'email': 'updateduser@example.com',
        'password': 'updatedpassword',
    }

    response = client.put('/users/1', json=updated_user_data)

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'updateduser',
        'id': 1,
        'email': 'updateduser@example.com',
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


def test_delete_user(client):
    # depende do teste anterior para criar um usuário, isso será corrigido
    response = client.delete('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted successfully'}


def test_delete_user_not_found(client):
    response = client.delete('/users/999')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}
