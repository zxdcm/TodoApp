
from django.conf import settings
from todolib.services import AppService
from todolib.models import set_up_connection

def get_service():
    session = set_up_connection('sqlite',
                                settings.DATABASES['default']['NAME'])
    service = AppService(session)
    return service
