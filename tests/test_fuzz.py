import time
import subprocess
import itertools

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


@st.composite
def generate_bad_dates(draw):
    pad02 = lambda m: f'{m:02}'
    rm_leaps = lambda y: (y%4!=0 or y%100==0) and y%400!=0
    fmt_date = lambda t: '-'.join(t)

    years = st.integers(1900, 2025).map(str)
    nonleap_years = st.integers(1900, 2025).filter(rm_leaps).map(str)
    months_lt31 = st.sampled_from([2, 4, 6, 9, 11]).map(pad02)
    feb = st.just('02')
    day29 = st.just('29')
    day30 = st.just('30')
    day31 = st.just('31')

    case1 = st.tuples(years, months_lt31, day31)
    case2 = st.tuples(years, feb, (day30 | day31))
    case3 = st.tuples(nonleap_years, feb, day29)

    return draw(st.builds(fmt_date, (case1 | case2 | case3)))


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
def generate_wrong_lengths(draw):
    charset = st.characters(codec='utf-8')
    long_nickname = {
        'nickname': st.text(charset, min_size=33),
        'fullname': st.just('bar'),
        'dob': st.just('2000-01-01')
    }
    long_fullname = {
        'nickname': st.just('bar'),
        'fullname': st.text(charset, min_size=101),
        'dob': st.just('2000-01-01')
    }
    long_stack_element = {
        'nickname': st.just('bar'),
        'fullname': st.just('bar'),
        'dob': st.just('2000-01-01'),
        'stack': st.lists(st.text(charset, min_size=33), min_size=0, max_size=1)
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


@h.given(generate_wrong_lengths())
def test_wrong_lengths(body):
    res = _make_request(body)
    assert res.status_code == 422


# @h.settings(max_examples=500)
@h.given(generate_bad_dates())
def test_bad_dates(body):
    # res = _make_request(body)
    # assert res.status_code == 400
    print(body)


def test_nickname_uniqueness():
    body = {'nickname': 'foo', 'fullname': 'bar', 'dob': '2000-01-01'}
    _make_request(body)
    res = _make_request(body)
    assert res.status_code == 422


if __name__ == '__main__':
    test_bad_dates()
    ...
