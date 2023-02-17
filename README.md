# passport
Packing list management tool / inventory management tool

### Running:
Running `python manage.py migrate` creates an empty database prefilled with the following initial data for the company:

Distributor "Warehouse" - intended for managing stock\
Recipient "[Incomplete]" - intended for keeping incomplete/broken/otherwise unusable stock\
Recipient "[Main]" - main warehouse

These objects are referred to by their IDs in the code and can be safely renamed.

### Sample dataset:
To fill database with auto-generated sample data, run:

`python .\manage.py populate_db`

## TODO:
* add success messages
* implement analytics
* change filter date picker to range
* add page breaks for printing
* add tests
* export for detail views?
* images?