import hypothesis as h
import hypothesis.strategies as st

import utils


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

    return {
        'nickname': 'bar',
        'fullname': 'bar',
        'dob': draw(st.builds(fmt_date, (case1 | case2 | case3)))
    }


@st.composite
def generate_wrong_types(draw):
    primitives = (st.integers(-1,1) | st.floats(-1,1) | st.booleans())
    strings = st.text(st.characters(codec='utf-8'), max_size=10)
    lists = st.lists(primitives | strings)
    dicts = st.dictionaries(strings, primitives)
    containers = (lists | dicts)
    wrong_types = (primitives | containers)

    return {
        'nickname': draw(wrong_types),
        'fullname': draw(wrong_types),
        'dob': draw(wrong_types),
        'stack': draw(wrong_types | st.none())
    }


@st.composite
def generate_none_or_missing(draw):
    no_nickname: dict[str, st.SearchStrategy] = {
        'fullname': st.just('bar'),
        'dob': st.just('2000-01-01')
    }
    no_fullname: dict[str, st.SearchStrategy] = {
        'nickname': st.just('bar'),
        'dob': st.just('2000-01-01')
    }
    no_dob: dict[str, st.SearchStrategy] = {
        'nickname': st.just('bar'),
        'fullname': st.just('bar')
    }

    case1 = st.fixed_dictionaries(no_nickname, optional={'nickname': st.none()})
    case2 = st.fixed_dictionaries(no_fullname, optional={'fullname': st.none()})
    case3 = st.fixed_dictionaries(no_dob, optional={'dob': st.none()})

    return draw(case1 | case2 | case3)


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

    case1 = st.fixed_dictionaries(long_nickname)
    case2 = st.fixed_dictionaries(long_fullname)
    case3 = st.fixed_dictionaries(long_stack_element)

    return draw(case1 | case2 | case3)


@st.composite
def generate_maybe_uuids(draw):
    # Valid, but (hopefully) non-existent:
    case1 = st.uuids(allow_nil=True)

    # (probaly) Invalid:
    case2 = st.text(st.characters(codec='utf-8'), min_size=1, max_size=128)

    return draw(case1 | case2)


def test_nickname_uniqueness():
    body = {'nickname': 'foo', 'fullname': 'bar', 'dob': '2000-01-01'}
    utils.create(body)
    assert utils.create(body).status_code == 422


@h.given(generate_none_or_missing())
def test_none_or_missing(body):
    assert utils.create(body).status_code == 422


@h.given(generate_wrong_types())
def test_wrong_types(body):
    assert utils.create(body).status_code == 400


@h.given(generate_wrong_lengths())
def test_wrong_lengths(body):
    assert utils.create(body).status_code == 422


@h.given(generate_bad_dates())
def test_bad_dates(body):
    assert utils.create(body).status_code == 400


@h.given(generate_maybe_uuids())
def test_fetch_404(maybe_uuid):
    assert utils.get_user(maybe_uuid).status_code in {400, 404}


def test_num_users():
    assert utils.get_users_count() == 1


def test_bad_search():
    assert utils.search(None).status_code == 400
    assert utils.search({'q': ''}).status_code == 400


if __name__ == '__main__':
    ...
