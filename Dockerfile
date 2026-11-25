FROM python:3.15.1 AS requirements-stage

WORKDIR /tmp
# The version that wrote poetry.lock. Poetry 2 no longer ships `poetry export`.
RUN pip install poetry==1.8.4
COPY ./pyproject.toml ./poetry.lock* /tmp/
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM python:3.15.1-slim

ENV DEBIAN_FRONTEND=noninteractive

# Debian's Chromium and its driver, since Google builds Chrome for Linux only for
# x86 and the server is ARM. The driver is installed at /usr/bin/chromedriver,
# where src/processors.py looks for it.
RUN apt-get update \
    && apt-get install -y chromium chromium-driver --no-install-recommends \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /code

COPY --from=requirements-stage /tmp/requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./ /code/

CMD ["python", "-u", "./src/main.py"]
