import pytest

import utils
from data.users import USERS, TERMS


@pytest.mark.parametrize('new_user', USERS)
def test_create_valid_user(new_user, truncate):
    res1 = utils.create(new_user)
    assert res1.status_code == 201

    res2 = utils.get_user(res1.headers['location'])
    assert res2.status_code == 200

    created_user = res2.json()
    new_user['id'] = created_user['id']
    if not new_user.get('stack', 0):
        new_user['stack'] = None
    assert new_user == created_user


@pytest.mark.parametrize('term,count', TERMS)
def test_search_for_term(term, count, populate_db, truncate):
    res = utils.search({'q': term})
    assert res.status_code == 200

    results = res.json()
    assert len(results) >= count


def test_search_expect_empty():
    res = utils.search({'q': 'foobarbaz'})
    assert res.status_code == 200

    results = res.json()
    assert len(results) == 0
