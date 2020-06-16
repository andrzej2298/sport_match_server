# Sport Match
Sport Match was written as a bachelor thesis by
Gabilcious (https://github.com/Gabilcious)
shaponiuk (https://github.com/shaponiuk) and
andrzej2298 (https://github.com/andrzej2298)

## Mobile application
Sport Match application (https://github.com/Gabilcious/Sport-Match) focuses on integrating people via common workouts, that are handled by the system. The events are recommended to the users, taking into consideration their features and past choices of the users. A user has the possibility of joining a previously recommended event and the author can either accept or reject his participation request.
The mobile application can be run on the Android operating system. However, the use of the Kotlin Multiplatform technology gives the opportunity to easily add other platforms, such as an iOS application, a Web application or a desktop application.

## Server
The backend was written in Django REST Framework and communicates with the app via the HTTP protocol. It also follows the REST principles. Furthermore, the backend uses the PostGIS database, which makes operations based on geographic data easier. The recommendation system is a part of the backend code. It was written using the Tensorflow framework.
This is the repository containing the backend code.

# Setup
```
docker-compose build
docker-compose up
```

# Database migrations
Because creating a migration requires
connecting to the database, you can do it this way:
```
# deleting previous migrations
# because keeping them
# is currently unnecessary
rm -rf api/migrations
docker-compose kill db
# info about migrations is
# also kept in the database
docker-compose rm db

# generating new migrations
docker-compose up
docker-compose exec api bash
./manage.py makemigrations api
./manage.py migrate
```
By default Docker creates files with root permissions,
so additionally you can change the owner of the
migrations folder to yourself instead of root.

# API endpoints

Mock API endpoints are available at `firefox localhost:8000/api/`.

# Mock API endpoints

Mock API endpoints are available at `firefox localhost:8000/api/mock/`.

# API documentation

All of the allowed actions are shown in the `api_documentation.json`.
To try them out (or add examples for a new action) install the
[Insomnia HTTP Client](https://insomnia.rest/) and go to
`Application > Preferences > Data` to import (or export) data.

# Relevant links
- [GeoDjango](https://docs.djangoproject.com/en/3.0/ref/contrib/gis/)
- [PostGIS](https://postgis.net)
