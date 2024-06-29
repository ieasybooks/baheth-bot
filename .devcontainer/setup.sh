curl -sSL https://install.python-poetry.org | python -
poetry config virtualenvs.create false
poetry install

test -f .env || cp .env.example .env
