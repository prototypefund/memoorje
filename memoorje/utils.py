from rest_framework.request import Request

from memoorje.models import CapsuleReceiver


def get_authenticated_user(request):
    if request is not None and request.user.is_authenticated:
        return request.user
    return None


def get_receiver_by_token(request: Request):
    token = request.headers.get("X-Memoorje-Receiver-Token")
    try:
        return CapsuleReceiver.objects.get_by_token(token)
    except CapsuleReceiver.DoesNotExist:
        return None
