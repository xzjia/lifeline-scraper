# How to setup the Database

### Setup local database for development

```bash
# Create a database at your psql session
#postgres=#CREATE DATABASE lifeline;

# Add the environment variable DATABASE_URL.
# You can do this manually, or use something like https://github.com/kennethreitz/autoenv
export DATABASE_URL=postgresql://postgres:postgres@127.0.0.1/lifeline
```

### Install pipenv

```bash
# On Mac
brew install pipenv
```

Note: It's possible that you will need to set up Locale on your Mac as discussed [here](https://github.com/pypa/pipenv/issues/187).
Add the following two lines in your shell RC file.

```
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8
```

### Run the following to setup

```bash
pipenv install --dev # Install all the dependencies

pipenv shell # Spawns a shell within the virtualenv

alembic upgrade head # Run the database migration
```

And check your database's table to make sure date are correctly inserted.

## To downgrade and upgrade with more flexibility

```bash
pipenv shell
alembic upgrade head # Upgrade to the most recent one
alembic upgrade +1 # Upgrade one revision
alembic upgrade +2 # Upgrade two revisions

alembic downgrade -1 # Downgrade to one revision
alembic downgrade -2 # Downgrade to two revisions
alembic downgrade base # Downgrade to the very beginning, which is usually a fresh start
```

# How to query the NYT API using this script

```bash
# At root directory
python nyt/main.py
# You will need to specify a date inside nyt/main.py to indicate which date's data you want.
# And currently, for unknown reasons, some date doesn't have date populated correctly.
```
