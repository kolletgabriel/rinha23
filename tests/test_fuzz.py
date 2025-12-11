import time
import subprocess

import hypothesis as h
import hypothesis.strategies as st
import pytest as p
import requests as r


BASE_URL = 'http://localhost:9999'


def _make_request(body):
    return r.post(f'{BASE_URL}/users',
                  headers={'Content-Type':'application/json'},
                  json=body)


@p.fixture(scope='session', autouse=True)
def setup_compose():
    subprocess.run(['docker', 'compose', 'up', '-d'])
    time.sleep(3)  # wait
    yield
    subprocess.run(['docker', 'compose', 'down'])


# @p.fixture
# def bad_dates():
#     return [
#         '2000-01-32',
#         '2000-13-01',
#         '2000-02-30',
#         '2000-04-31',
#         '2000-06-31',
#         '2000-09-31',
#         '2000-11-31',
#         '1900-02-29',
#         '2001-02-29',
#         '5739407574325',
#         'foobarbaz',
#         ''
#     ]


@st.composite
def generate_bad_dates(draw):
    years = st.integers(1900,2025)
    nonleap_years = years.filter(lambda y: (y%4!=0 or y%100==0) and y%400!=0)
    months_30 = st.sampled_from([4, 6, 9, 11])
    bad_months = (st.just(0) | st.integers(13,99))
    bad_days = (st.just(0) | st.integers(32,99))

    t1 = (years, bad_months, bad_days)
    t2 = (nonleap_years, st.just(2), st.just(29))
    t3 = (years, months_30, st.just(31))

    x = st.builds(lambda y,m,d: f'{y:04}-{m:02}-{d:02}', *t1)
    y = st.builds(lambda y,m,d: f'{y:04}-{m:02}-{d:02}', *t2)
    z = st.builds(lambda y,m,d: f'{y:04}-{m:02}-{d:02}', *t3)

    return {
        'nickname': 'bar',
        'fullname': 'bar',
        'dob': draw(x | y | z)
    }



@st.composite
def generate_wrong_types(draw):
    _primitives = (st.integers(-1,1) | st.floats(-1,1) | st.booleans())
    _strings = st.text(st.characters(codec='utf-8'), max_size=10)
    _lists = st.lists(_primitives | _strings)
    _dicts = st.dictionaries(_strings, _primitives)
    _containers = (_lists | _dicts)
    wrong_types = (_primitives | _containers)

    return {
        'nickname': draw(wrong_types),
        'fullname': draw(wrong_types),
        'dob': draw(wrong_types),
        'stack': draw(wrong_types | st.none())
    }


@st.composite
def generate_none_or_missing(draw):
    no_nickname = {
        'fullname': st.just('bar'),
        'dob': st.just('2000-01-01')
    }
    no_fullname = {
        'nickname': st.just('bar'),
        'dob': st.just('2000-01-01')
    }
    no_dob = {
        'nickname': st.just('bar'),
        'fullname': st.just('bar')
    }

    x = st.fixed_dictionaries(no_nickname, optional={'nickname': st.none()})
    y = st.fixed_dictionaries(no_fullname, optional={'fullname': st.none()})
    z = st.fixed_dictionaries(no_dob, optional={'dob': st.none()})

    return draw(x | y | z)


@st.composite
def generate_bad_lengths(draw):
    long_nickname = {
        'nickname': st.just('bar'*11),
        'fullname': st.just('bar'),
        'dob': st.just('2000-01-01')
    }
    long_fullname = {
        'nickname': st.just('bar'),
        'fullname': st.just('bar'*34),
        'dob': st.just('2000-01-01')
    }
    long_stack_element = {
        'nickname': st.just('bar'),
        'fullname': st.just('bar'),
        'dob': st.just('2000-01-01'),
        'stack': st.just(['foo', 'bar'*11])
    }

    x = st.fixed_dictionaries(long_nickname)
    y = st.fixed_dictionaries(long_fullname)
    z = st.fixed_dictionaries(long_stack_element)

    return draw(x | y | z)


@h.given(generate_none_or_missing())
def test_none_or_missing(body):
    res = _make_request(body)
    assert res.status_code == 422


@h.given(generate_wrong_types())
def test_wrong_types(body):
    res = _make_request(body)
    assert res.status_code == 400


@h.given(generate_bad_lengths())
def test_bad_lengths(body):
    res = _make_request(body)
    assert res.status_code == 422


@h.given(generate_bad_dates())
def test_bad_dates(body):
    res = _make_request(body)
    assert res.status_code == 400


def test_nickname_uniqueness():
    body = {'nickname': 'foo', 'fullname': 'bar', 'dob': '2000-01-01'}
    _make_request(body)
    res = _make_request(body)
    assert res.status_code == 422


if __name__ == '__main__':
    ...
