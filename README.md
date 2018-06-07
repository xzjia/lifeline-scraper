# What is this

This is a collection of scripts that collects data for lifeline project.

# Common tasks

## Set up

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

alembic upgrade +3 # Run the Data Definition Language and Data Manipulation Language for label table
alembic upgrade head # Run the Data Manipulation Language for event table
```

And check your database's table to make sure date are correctly inserted.

## How to make a new revision and put some data in migration?

```bash
pipenv shell # Spawns a shell within the virtualenv
alembic revision -m "${THE_REVISION_MESSAGE}" # This will create a new revision and a new file will be generated under alembic/versions
```

Edit the generated file so that it do the migration. [Here](http://alembic.zzzcomputing.com/en/latest/ops.html) are some useful information.

## How to upgrade to the most up-to-date status?

Note: the revision in this repository has the following meaning.

- First revision: `1e4b3e20e30d`, create `label` table
- Second revision: `1e4b3e20e30d`, create `event` table
- Third revision: `c3ba36e57a09`, insert into `label` table with data
- All the following revision: insert into `event` table with data

```bash
pipenv shell
alembic upgrade head # Upgrade to the most recent one
alembic upgrade +1 # Upgrade one revision
alembic upgrade +2 # Upgrade two revisions
```

## How to downgrade to the very beginning?

```bash
alembic downgrade -1 # Downgrade to one revision
alembic downgrade -2 # Downgrade to two revisions
alembic downgrade base # Downgrade to the very beginning, which is usually a fresh start
```

## How to query the NYT API using this script

```bash
# At root directory
python nyt/main.py
# You will need to specify a date inside nyt/main.py to indicate which date's data you want.
# And currently, for unknown reasons, some date doesn't have date populated correctly.
```
