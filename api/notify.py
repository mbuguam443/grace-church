import json
from urllib import request as urlrequest

from django.contrib.auth import get_user_model

from core.models import Notification


def broadcast(title, message, kind=''):
    User = get_user_model()
    users = list(User.objects.filter(is_active=True).only('id'))
    if users:
        Notification.objects.bulk_create(
            [Notification(user=u, title=title, message=message, kind=kind) for u in users],
            batch_size=200,
        )
    _push_expo(title, message, kind)


def _push_expo(title, message, kind):
    from .models import DeviceToken

    tokens = list(DeviceToken.objects.values_list('token', flat=True))
    if not tokens:
        return
    body = json.dumps(
        [
            {
                'to': token,
                'title': title,
                'body': (message or '')[:180],
                'sound': 'default',
                'data': {'kind': kind},
            }
            for token in tokens
        ]
    ).encode('utf-8')
    req = urlrequest.Request(
        'https://exp.host/--/api/v2/push/send',
        data=body,
        headers={'Content-Type': 'application/json', 'Accept': 'application/json'},
        method='POST',
    )
    try:
        urlrequest.urlopen(req, timeout=8).read()
    except Exception:
        pass
