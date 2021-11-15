from memoorje.models import Capsule, CapsuleContent, CapsuleReceiver, Keyslot, PartialKey, Trustee, User
from memoorje.tests.memoorje import create_test_data_file


class BaseMixin:
    def get_request_headers(self, **kwargs):
        return {}


class UserMixin(BaseMixin):
    user: User
    password: str
    email: str

    def authenticate_user(self):
        self.ensure_user_exists()
        self.client.force_login(user=self.user)

    def create_user(self):
        self.email = f"test{User.objects.count()}@example.org"
        self.password = "test12345"
        self.user = User.objects.create_user(self.email, self.password, name="Test Name")

    def ensure_user_exists(self):
        if not User.objects.exists():
            self.create_user()


class CapsuleMixin(UserMixin):
    capsule: Capsule
    capsule_description: str
    capsule_name: str

    def create_capsule(self) -> Capsule:
        self.ensure_user_exists()
        self.capsule_name = "test"
        self.capsule_description = "test"
        self.capsule = Capsule.objects.create(
            owner=self.user, name=self.capsule_name, description=self.capsule_description
        )
        return self.capsule

    def ensure_capsule_exists(self):
        self.ensure_user_exists()
        if not Capsule.objects.filter(owner=self.user).exists():
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


class CapsuleReceiverMixin(CapsuleMixin):
    capsule_receiver: CapsuleReceiver
    receiver_email: str

    def create_capsule_receiver(self, email=None):
        self.ensure_capsule_exists()
        self.receiver_email = email or "test@example.org"
        self.capsule_receiver = CapsuleReceiver.objects.create(capsule=self.capsule, email=self.receiver_email)
        return self.capsule_receiver

    def get_request_headers(self, **kwargs):
        headers = super().get_request_headers(**kwargs)
        if "with_receiver_token_for" in kwargs:
            receiver = kwargs["with_receiver_token_for"]
            token = receiver.receiver_token_generator_proxy.make_token()
            headers["HTTP_X_MEMOORJE_RECEIVER_TOKEN"] = token
        return headers


class KeyslotMixin(CapsuleMixin):
    keyslot: Keyslot
    data: bytes
    purpose: Keyslot.Purpose

    def create_keyslot(self):
        self.ensure_capsule_exists()
        self.data = b"Some encrypted data"
        self.purpose = "pwd"
        self.keyslot = Keyslot.objects.create(capsule=self.capsule, data=self.data, purpose=self.purpose)


class TrusteeMixin(CapsuleMixin):
    partial_key_data: bytes
    trustee_email: str
    trustee: Trustee

    def create_trustee(self):
        self.ensure_capsule_exists()
        self.trustee_email = "trustee@example.org"
        self.partial_key_data = b"Partial key data according to Shamir's Secret Sharing Scheme"
        self.trustee = Trustee.objects.create(
            capsule=self.capsule,
            email=self.trustee_email,
            partial_key_hash=PartialKey.hash_key_data(self.partial_key_data),
        )
