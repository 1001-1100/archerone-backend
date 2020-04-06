# ArcherOne

## Prerequisites

https://www.python.org/downloads/

https://nodejs.org/en/download/

https://pypi.org/project/pipenv/

https://classic.yarnpkg.com/en/docs/install/

http://www.mingw.org/

## Installation

`pip install django djangorestframework django-cors-headers django-cors-middleware django-rest-auth django-allauth django-extensions django-annoying djangorestframework-jwt z3-solver requests html5lib bs4`

Then go to the frontend directory to install react dependencies:

`cd frontend`

`yarn global add create-react-app`

`yarn add create-react-app bootstrap reactstrap axios`

Additional packages that need to be installed:

`yarn add simple-flexbox react-smooth-dnd react-router @devexpress/dx-react-core @devexpress/dx-react-scheduler @material-ui/core @material-ui/icons @devexpress/dx-react-scheduler-material-ui group-array`

## Usage

You need to run both the React Server and the Django Server.

Start React Server:

`cd frontend`

`yarn start`

Start Django Server:

`cd backend`

Make migrations and migrate:

`python manage.py makemigrations`

`python manage.py migrate`

Run the server:

`python manage.py runserver`

## REST API

Login:

`/api/auth/login`

Register:

`/api/auth/registration`

Get user info of logged in user:

`/api/auth/user`

Get list of users:

`/api/users`