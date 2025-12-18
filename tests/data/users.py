import random
import uuid
import itertools

from faker import Faker


fake = Faker()

STACK = [
    'Python', 'Go', 'JavaScript', 'TypeScript', 'C', 'C++', 'C#', 'Java', 'Rust',
    'Haskell', 'Ruby', 'HTML', 'CSS', 'PostgreSQL', 'MySQL', 'MongoDB', 'Docker',
    'Scala', 'Kotlin', 'Tailwind', 'React', 'React Native', 'Swift', 'Node',
    'Bun', 'Vue', 'Angular', 'Flask', 'Django', 'FastAPI', 'Elixir', 'Erlang',
    'OCaml', 'Rails', 'Linux', 'Git', 'Jenkins', 'GitHub Actions', 'Kubernetes',
    'Terraform', 'GitLab CI', 'Apache Airflow', 'Apache Kafka', 'Azure', 'AWS',
    'RabbitMQ', 'GCP', 'Databricks', 'RedShift', 'Redis', 'Memcached'
]


def generate_valid_post_data(n):
    fake.seed_instance(0)
    random.seed(0)

    result = []
    for _ in range(n):
        profile = fake.profile(fields=['username', 'name', 'birthdate'])

        nickname = profile['username'][:32]
        fullname = profile['name'][:100]

        new_user = {
            'nickname': nickname,
            'fullname': fullname,
            'dob': profile['birthdate'].isoformat(),
        }
        if random.choice((True, False)):
            new_user['stack'] = random.choice((
                None,
                random.sample(STACK, k=random.randint(1, 5))
            ))

        result.append(new_user)

    return result


def generate_sample_users(n):
    fake.seed_instance(0)
    random.seed(0)

    result = []
    for _ in range(n):
        profile = fake.profile(fields=['username', 'name', 'birthdate'])

        id_ = str(uuid.uuid4())
        nickname = profile['username'][:32]
        fullname = profile['name'][:100]
        dob = profile['birthdate'].isoformat()
        stack = random.choice((
            None, random.sample(STACK, k=random.randint(1, 5))
        ))

        result.append((id_, nickname, fullname, dob, stack))

    return result


# This piece of code is (mostly) courtesy from:
# https://mathspp.com/blog/generalising-itertools-pairwise
def _triplewise(string):
    iterators = itertools.tee(string, 3)
    for idx, iterator in enumerate(iterators):
        for _ in itertools.islice(iterator, idx):
            pass

    yield from map(lambda t: ''.join(t), zip(*iterators))


def tokenize(users: list[tuple]):
    trigrams_count = {}
    for user in users:
        user_trigrams = set()
        strings = [user[1], user[2]]
        if user[4] is not None:
            strings.extend(user[4])

        for s in strings:
            if len(s) < 3:
                continue
            for trigram in _triplewise(s):
                user_trigrams.add(trigram.lower())

        for trigram in user_trigrams:
            try:
                trigrams_count[trigram] += 1
            except KeyError:
                trigrams_count[trigram] = 1

    return trigrams_count.items()


USERS = generate_valid_post_data(100)
SAMPLE = generate_sample_users(10)
TERMS = tokenize(SAMPLE)
