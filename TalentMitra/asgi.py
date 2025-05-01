import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "TalentMitra.settings")

application = get_asgi_application()

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
