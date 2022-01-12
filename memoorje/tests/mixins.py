from django_otp.plugins.otp_totp.models import TOTPDevice

from memoorje.models import Capsule, CapsuleContent, CapsuleReceiver, Keyslot, PartialKey, Trustee, User
from memoorje.tests.memoorje import create_test_data_file
from memoorje_2fa.users import create_default_device_for_user
from memoorje_2fa.utils import get_totp_for_device


class BaseMixin:
    def get_request_headers(self, **kwargs):
        return {}


class UserMixin(BaseMixin):
    two_factor_device: TOTPDevice
    two_factor_token: str
    user: User
    password: str
    email: str

    def authenticate_user(self):
        self.ensure_user_exists()
        self.client.force_login(user=self.user)

    def create_user(self, is_2fa_enabled=False):
        self.email = f"test{User.objects.count()}@example.org"
        self.password = "test12345"
        self.user = User.objects.create_user(self.email, self.password, name="Test Name")
        if is_2fa_enabled:
            self.two_factor_device = create_default_device_for_user(self.user)
            self.two_factor_token = get_totp_for_device(self.two_factor_device).token()

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

    def create_keyslot(self, data=None, purpose=Keyslot.Purpose.PASSWORD):
        self.ensure_capsule_exists()
        self.data = data or b"Some encrypted data"
        self.purpose = purpose
        self.keyslot = Keyslot.objects.create(capsule=self.capsule, data=self.data, purpose=self.purpose)


class PartialKeyMixin(CapsuleMixin):
    combined_secret: bytes
    partial_key: PartialKey
    data: bytes

    def create_partial_key(self):
        self.ensure_capsule_exists()
        self.data = b"Partial key data"
        self.partial_key = PartialKey.objects.create(capsule=self.capsule, data=self.data)

    def create_combinable_partial_keys(self):
        self.ensure_capsule_exists()
        self.combined_secret = b"Arbitrary Password!"
        PartialKey.objects.create(
            capsule=self.capsule,
            data=bytes.fromhex(
                "01ecbb2bee4722db397100e83b9702aad04776a9c8d5ce24930dc4815f6ca51a3789"
                "d26a308016d4e04e413042e61b1e5cbf247ef7d6360143920fc3ca62506e2c1e8d0d"
            ),
        )
        PartialKey.objects.create(
            capsule=self.capsule,
            data=bytes.fromhex(
                "02a76763d4633e22d858383ddb87ff624992683809971bb658142221ee208c795089"
                "d26a308016d4e04e413042e61b1e5cbf247ef7d6360143920fc3ca62506e2c1e8d0d"
            ),
        )


class TrusteeMixin(CapsuleMixin):
    partial_key_data: bytes
    trustee_email: str
    trustee: Trustee

    def create_trustee(self):
        self.ensure_capsule_exists()
        self.trustee_email = "trustee@example.org"
        self.partial_key_data = b"Partial key data according to Shamir's Secret Sharing Scheme" + bytes(
            Trustee.objects.count()
        )
        self.trustee = Trustee.objects.create(
            capsule=self.capsule,
            email=self.trustee_email,
            partial_key_hash=PartialKey.hash_key_data(self.partial_key_data),
        )
