__version__ = "0.1.0"


def get_authenticated_user(request):
    if request is not None and request.user.is_authenticated:
        return request.user
    return None
