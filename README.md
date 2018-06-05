# How to setup

### Setup local database for development

```bash
# Create the database at your psql session
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

### Run the following

```bash
pipenv install --dev # Install all the dependencies

pipenv shell # Spawns a shell within the virtualenv

alembic upgrade head # Run the database migration
```
