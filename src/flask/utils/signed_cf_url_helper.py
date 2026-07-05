import datetime
from urllib.parse import quote
from botocore.signers import CloudFrontSigner
from config import PUBLIC_KEY_ID, CFD_BASE_URL, get_cf_private_key_pem
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

# Parse the CloudFront private key once and cache it (avoids re-reading/parsing
# the PEM on every signed-URL request).
_private_key = None


def _load_private_key():
    global _private_key
    if _private_key is None:
        _private_key = serialization.load_pem_private_key(
            get_cf_private_key_pem().encode(),
            password=None,
            backend=default_backend(),
        )
    return _private_key


def generate_signed_urls(object_key):
    def rsa_signer(message):
        return _load_private_key().sign(message, padding.PKCS1v15(), hashes.SHA1())

    key_id = PUBLIC_KEY_ID
    # URL-encode the key path so objects with spaces / special chars sign against
    # the same URL the browser will request (safe='/' keeps path separators).
    url = f"{CFD_BASE_URL}/{quote(object_key, safe='/')}"
    expire_date = datetime.datetime.today() + datetime.timedelta(days=1)

    cloudfront_signer = CloudFrontSigner(key_id, rsa_signer)

    # Create a signed url that will be valid until the specific expiry date
    # provided using a canned policy.
    signed_url = cloudfront_signer.generate_presigned_url(
        url, date_less_than=expire_date)
    return signed_url
