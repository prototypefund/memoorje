from rest_framework import permissions

from memoorje.models import Capsule


class IsCapsuleOwner(permissions.BasePermission):
    @staticmethod
    def get_capsule_from_object(obj):
        if isinstance(obj, Capsule):
            return obj
        return None

    @staticmethod
    def get_capsule_from_request(request):
        try:
            pk = request.GET.get("capsule")
            # we set request.capsule as a side effect
            request.capsule = Capsule.objects.get(pk=pk)
            return request.capsule
        except Capsule.DoesNotExist:
            return None

    @staticmethod
    def has_capsule_permission(request, capsule):
        if capsule is not None:
            return request.user == capsule.owner
        else:
            return False

    def has_permission(self, request, view):
        if view.action in ["create", "list"]:
            capsule = self.get_capsule_from_request(request)
            return self.has_capsule_permission(request, capsule)
        else:
            return super().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        capsule = self.get_capsule_from_object(obj)
        return self.has_capsule_permission(request, capsule)
