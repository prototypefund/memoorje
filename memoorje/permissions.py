from rest_framework import permissions


class IsCapsuleOwner(permissions.BasePermission):
    @staticmethod
    def get_capsule(request, obj):
        return obj or None

    def has_capsule_permission(self, request, obj=None):
        capsule = self.get_capsule(request, obj)
        if capsule is not None:
            return request.user == capsule.owner
        else:
            return False

    def has_permission(self, request, view):
        if view.action in ["retrieve"]:
            # object level permissions will be checked in has_object_permission()
            return True
        else:
            return self.has_capsule_permission(request)

    def has_object_permission(self, request, view, obj):
        return self.has_capsule_permission(request, obj)
