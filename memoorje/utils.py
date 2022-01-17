from rest_framework.request import Request

from memoorje.models import CapsuleRecipient


def get_authenticated_user(request):
    if request is not None and request.user.is_authenticated:
        return request.user
    return None


def get_recipient_by_token(request: Request):
    token = request.headers.get("X-Memoorje-Recipient-Token")
    try:
        return CapsuleRecipient.objects.get_by_token(token)
    except CapsuleRecipient.DoesNotExist:
        return None
