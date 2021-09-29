from contextlib import contextmanager
from tempfile import TemporaryFile

from rest_framework.reverse import reverse

from memoorje.models import Capsule, CapsuleContent, User


@contextmanager
def create_test_data_file(data):
    with TemporaryFile() as f:
        f.write(data)
        f.seek(0)
        yield f


class UserMixin:
    user: User
    password: str
    email: str

    def create_user(self):
        self.email = f"test{User.objects.count()}@example.org"
        self.password = "test12345"
        self.user = User.objects.create_user(self.email, self.password, name="Test Name")

    def ensure_user_exists(self):
        if not hasattr(self, "user"):
            self.create_user()

    def authenticate_user(self):
        self.ensure_user_exists()
        if hasattr(self.client, "force_authentication"):
            self.client.force_authenticate(user=self.user)
        else:
            self.client.force_login(user=self.user)


class CapsuleMixin(UserMixin):
    capsule: Capsule
    capsule_description: str
    capsule_name: str

    def get_capsule_url(self, capsule=None, response=None):
        if capsule is None:
            capsule = self.capsule
        request = None
        if response is not None:
            request = response.wsgi_request
        return reverse("capsule-detail", args=[capsule.pk], request=request)

    def create_capsule(self) -> Capsule:
        self.ensure_user_exists()
        self.capsule_name = "test"
        self.capsule_description = "test"
        self.capsule = Capsule.objects.create(
            owner=self.user, name=self.capsule_name, description=self.capsule_description
        )
        return self.capsule

    def ensure_capsule_exists(self):
        if not hasattr(self, "capsule"):
            self.create_capsule()


class CapsuleContentMixin(CapsuleMixin):
    capsule_content: CapsuleContent
    data: bytes
    metadata: bytes

    def create_capsule_content(self):
        self.ensure_capsule_exists()
        self.metadata = b"Just any arbitrary metadata (encrypted)"
        self.data = b"Some encrypted data"
        self.capsule_content = CapsuleContent.objects.create(capsule=self.capsule, metadata=self.metadata)
        with create_test_data_file(self.data) as f:
            self.capsule_content.data.save("testfile", f)
