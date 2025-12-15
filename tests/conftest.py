import time
import subprocess

import pytest


@pytest.fixture(scope='session', autouse=True)
def setup_compose():
    subprocess.run(['docker', 'compose', 'up', '-d'])
    time.sleep(3)  # wait
    yield
    subprocess.run(['docker', 'compose', 'down'])
