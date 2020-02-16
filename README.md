The Money Transfer System is REST API service based on Django Rest Framework and Docker containers.
The purpose of the project is service for providing money transfers from user to user in different currencies and exchange rates. 
The system allows to operate with plenty of currencies and chronological exchange rates of courses.
Automatically downloads list of currencies and their exchange rates from service https://api.exchangeratesapi.io/latest
Supports JSON Web Token authorization.

Functionality of the system is described by its REST API end-points.

Main end-points:
 - /api/token/ - authenticate through JSON Web Tokens;
 - /api/token/refresh/ - refresh JWT-token;
 - /api/users/ - user issues 
 - /api/money/ - money transfer issues
 
 USERS end-points:
 - /api/users/ - get list of all users (HTTP GET method);
 - /api/users/create/ - register new user (HTTP POST method);
 - /api/users/accounts/ - get current user's accounts including balance information (HTTP GET method);
 - /api/users/accounts/create/ - create new account for cuurent user (HTTP POST method);
 - /api/users/{id}/ - get info about user of particular id (HTTP GET method);
 - /api/users/{id}/edit/ - edit particular user (HTTP PATCH method);
 - /api/users/{id}/accounts/ - get accounts of particular user (HTTP GET method);
 
 MONEY end-points:
 - /api/money/currencies/ - get list of currencies (HTTP GET method);
 - /api/money/courses/ - get list of courses rates (HTTP GET method);
 - /api/money/transfers/ - get list transfers of current user (HTTP GET method);
 - /api/money/transfers/create/ - create new transfer (HTTP POST method).
 
Project directory structure:
 1. postgres - directory for building PostgreSQL container for supporting database of the project;
 2. nginx - directory for building Nginx container for supporting web-server of the project;
 3. redis - directory for building Redis container for supporting ampq based on redis for Celery asynchronos tasks;
 4. web - directory for building WSGI container for supporting gunicorn wsgi server, contains Django source files of the system.

Django project is located in ./web/src/mts_django
The project is provided by testing module located in ./web/src/mts_django/money/tests.py
Python requirements-file path is ./web/requirements.txt
Asynchronous Celery task periodically fetches currency/rates json-data. It is coded in ./web/src/mts_django/money/tasks.py