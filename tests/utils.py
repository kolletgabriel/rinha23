import requests


BASE_URL = 'http://localhost:9999'


def create(body: dict) -> requests.Response:
    return requests.post(f'{BASE_URL}/users',
                  headers={'Content-Type': 'application/json'},
                  json=body)


def get_user(maybe_uuid: str) -> requests.Response:
    return requests.get(f'{BASE_URL}/{maybe_uuid}')


def search(params: dict[str, str] | None) -> requests.Response:
    return requests.get(f'{BASE_URL}/users', params=params)


def get_users_count() -> int:
    return int(requests.get(f'{BASE_URL}/users-count').content)
