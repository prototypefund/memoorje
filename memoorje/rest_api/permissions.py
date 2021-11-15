from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, SAFE_METHODS


class IsCapsuleOwner(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        try:
            capsule = obj.capsule
            is_own_capsule = capsule.owner == request.user
            return is_own_capsule
        except AttributeError:
            return False


class IsCapsuleOwnerOrReadOnly(IsAuthenticatedOrReadOnly):
    """
    Either the user is authenticated and owns the capsule or access is read-only.

    Which capsules are read-only accessible is handled by restricting the queryset.
    """

    def has_object_permission(self, request, view, obj):
        try:
            capsule = obj.capsule
            is_read_only = request.method in SAFE_METHODS
            is_own_capsule = capsule.owner == request.user
            return is_read_only or is_own_capsule
        except AttributeError:
            return False
