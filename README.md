# How to setup

### Setup local database for development

```bash
# Create the database
#postgres=#CREATE DATABASE lifeline;

# Edit the database connection information in alembic.ini file
sqlalchemy.url = postgresql://postgres:postgres@127.0.0.1/lifeline

TODO: Take this URL out of the repository in the future
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
pipenv shell # Spawns a shell within the virtualenv

alembic upgrade head # Run the database migration
```

### Enter the Run the database migration
