#### Getting started
Install requirements `pip install requirements.txt`

#### Basic django commands:
* make migrations `python manage.py makemigrations`
* migrate (init db) `python manage.py migrate`
* collect static files `python manage.py collectstatic --noinput`
* create admin `python manage.py createsuperuser`
* run dev server `python manage.py runserver`
* run gunicorn `gunicorn core.wsgi:application --bind 0.0.0.0:8000 --reload`

#### API documentation:
* `/swagger/`
* `/redoc/`
* API Root: `/api/v1/`
#### Bot for testing
* configure variables in `bot_config.json`
* launch bot `python bot.py`





