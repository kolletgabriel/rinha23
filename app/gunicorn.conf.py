from db import close_conn


def worker_exit(server, worker):
    close_conn()
