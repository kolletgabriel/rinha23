# Rinha de Backend 2023

**TL;DR:** A playful exercise on optimizing a Python stack for high throughput workloads without `asyncio` under the rules settled by [this challenge](https://github.com/zanfranceschi/rinha-de-backend-2023-q3/blob/main/INSTRUCOES.md) (instructions in pt-br).

## How to Run

You can `source sourceme.sh` for setting up useful aliases and environment variables for easily executing the helper scripts. Otherwise:

```bash
docker compose up -d \
    && cd benchmarks \
    && docker build -t 'gatling' . \
    && docker run --rm --name=gatling --network=host -v ./results:/opt/gatling/results gatling \
    && curl http://localhost:9999/users-count \
    && echo \
    && docker compose down
```

The results of the load test will be at `benchmarks/results/`. Just open `index.html` with a web browser to see them.

## A Brief Overview on the Challenge Itself

First and foremost, the word "rinha" stands for "brawl", "cockfight", "cage match", "rumble" *etc*. It's a challenge started in 2023, made for/by the dev community in Brazil, and which constists in delivering a RESTful service easy to implement yet tricky to make it survive the load tests.

This project implements the 1st edition of the challenge, whose restrictions went as follows:

- at least 4 services: database, load balancer and 2 instances of the API (more services e.g. for cache were optional);
- maximum of 1.5 CPUs and 3GB of RAM distributed across **all** services;
- endpoints for creating, fetching and querying resources;
- json as the representation format;
- all running within Docker Compose.

Finally, the **winning criteria:** biggest number of insertions in the database at the end of the load test.

### The Load Test

The test script is written in Scala, using the framework Gatling. It runs during 3m26s.

The script consumes `.tsv` files containing the load for the test. Unfortunely the files themselves had to be brought to this repository since the original generator scripts weren't seeded.

## About this Implementation

Lots of participants made their own submissions, and this one is mine... or at least it *would* be if I could go back in time!

The entire stack is composed of:

- Python:
    * Flask as the WSGI application framework;
    * Gunicorn as the WSGI server;
    * Psycopg2 as the database driver;
    * Pydantic as the validation tool;
- PostgreSQL;
- Nginx.

My intent was to see how far I could go by using only an *asyncless* Python framework with just a relational database, without cache.

Worth noting that the original path names for each endpoint were translated to english, and the `.randomize` method present in the "warmup" phase of the original test is absent.

### Main Strategy

Knowing beforehand that the *heavy-lifting* would be done by Postgres, most of the availabe resources were allocated to it. As a result, there wasn't much left for the API instances to work with so Gunicorn was capped at only 1 (single-threaded) worker.

With only 1 sync worker per instance, there's no use to a connection pool. So, to reduce the overhead of opening and closing connections to the database, each worker maintains an open connection during the entire application's lifetime.
