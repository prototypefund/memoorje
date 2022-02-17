from django.db.models import Q

from memoorje.models import CapsuleRecipient
from memoorje.utils import get_authenticated_user, get_recipient_by_token


class FilterMixin:
    def get_filter(self):
        # always false, can be combined with "|"
        return Q(pk__in=[])


class OwnedCapsuleRelatedFilterMixin(FilterMixin):
    def get_filter(self):
        user = get_authenticated_user(self.request)
        return super().get_filter() | Q(capsule__owner=user)


class ReceivedCapsuleRelatedFilterMixin(FilterMixin):
    def get_filter(self):
        result = super().get_filter()
        recipient = get_recipient_by_token(self.request)
        if recipient is not None:
            result |= self.get_recipient_filter(recipient)
        return result

    def get_recipient_filter(self, recipient: CapsuleRecipient) -> Q:
        return Q(capsule__recipients=recipient)


class OwnedOrReceivedCapsuleRelatedFilterMixin(OwnedCapsuleRelatedFilterMixin, ReceivedCapsuleRelatedFilterMixin):
    pass


class FilteredQuerySetMixin(FilterMixin):
    def get_queryset(self):
        return self.queryset.filter(self.get_filter())


class OwnedCapsuleRelatedQuerySetMixin(OwnedCapsuleRelatedFilterMixin, FilteredQuerySetMixin):
    pass


class OwnedOrReceivedCapsuleRelatedQuerySetMixin(OwnedOrReceivedCapsuleRelatedFilterMixin, FilteredQuerySetMixin):
    """
    Restricts the query set to objects for which the capsule is either owned by the current user or for which a
    recipient token exists.
    """
