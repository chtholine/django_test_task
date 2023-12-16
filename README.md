#### Basic django commands:

* make migrations `python manage.py makemigrations`
* migrate (init db) `python manage.py migrate`
* collect static files `python manage.py collectstatic --noinput`
* run dev server `python manage.py runserver`
* run gunicorn `gunicorn core.wsgi:application --bind 0.0.0.0:8000 --reload`


#### API documentation:
* `/swagger/`
* `/redoc/`

#### Front end:
Templates and static files are stored in "apps" directory.<br>

#### Useful links
* [Django templates and language](https://docs.djangoproject.com/en/4.2/topics/templates/)
* [Static files in django](https://docs.djangoproject.com/en/4.2/howto/static-files/)
* [Static files deployment](https://docs.djangoproject.com/en/4.2/howto/static-files/deployment/)


