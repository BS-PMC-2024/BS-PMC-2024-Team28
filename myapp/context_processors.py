# myapp/context_processors.py
from IDAS_3 import settings


def api_key(request):
    return {
        'CHAT_API_KEY': settings.CHAT_API_KEY
    }
