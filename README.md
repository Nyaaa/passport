[![Coverage Status](https://coveralls.io/repos/github/Nyaaa/passport/badge.svg)](https://coveralls.io/github/Nyaaa/passport)
# passport
Packing list management tool / inventory management tool

### Running:
`docker-compose up -d --build` sets up a staging environment in Docker with collectstatic and migrations applied.

Running `python manage.py migrate` creates an empty database prefilled with the following initial data for the company:

Distributor "Warehouse" - intended for managing stock\
Recipient "[Incomplete]" - intended for keeping incomplete/broken/otherwise unusable stock\
Recipient "[Main]" - main warehouse

These objects are referred to by their IDs in the code and can be safely renamed, but shouldn't be removed. Checks are in place to prevent deletion in the UI, but they can still be vulnerable to direct SQL queries.

### Sample dataset:
To fill database with auto-generated sample data, run `python .\manage.py populate_db`. This requires 'testing' group of dependencies to be installed.

### Testing & development:
Use `--settings=passport.test_settings` with 'dev' dependency group installed.

## ERD

![ERD](docs/ERD.png)

## TODO
* implement analytics
* export for detail views?
* image storage solution
