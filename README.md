# table-builder-backend

This is a simple backend for a table builder app, where the user can build tables dynamically.
This app has the following endpoints:

1. /api/table

    - method: POST
    - request body:

        ```json
        {
            "table_name": "test_table",
            "fields": [
                {
                    "name": "field1",
                    "type": "string"
                },
                {
                    "name": "field2",
                    "type": "boolean"
                },
                {
                    "name": "field3",
                    "type": "number"
                }
            ]
        }
        ```

2. /api/table/:id

    - method: PUT
    - request body:

        ```json
        "fields": [
            {
                "name": "field1",
                "type": "string"
            },
            {
                "name": "field2",
                "type": "string"
            },
            {
                "name": "field3",
                "type": "boolean"
            },
            {
                "name": "field4",
                "type": "number"
            }
        ]
        ```

3. /api/table/:id/row

    - method: POST
    - request body:

        ```json
        {
            "data": {
                "field1": "value1",
                "field2": "value2",
                "field3": "value3",
                "field4": "value4"
            }
        }
        ```

    - method: GET

## How to run?

1. Setup PostgreDB in your machine.
2. Create `.env` file in this project root directory and Edit `.env` file with your DB credentials.

    ```bash
    cp .env.example .env
    ```

3. Make your virtualenv and install the dependencis

    ```bash
    pipenv shell --python 3.8
    pipenv install
    ```

4. Make migration.

    ```bash
    python manage.py migrate
    ```

5. Run Django app

    ```bash
    python manage.py runserver
    ```

## How to run unit test?

```bash
python manage.py test
```
