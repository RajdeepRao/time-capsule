import datetime
import os
from urllib.parse import quote
from botocore.signers import CloudFrontSigner
from temp_secrets import PUBLIC_KEY_ID, PATH_TO_LOCAL_PRIVATE_KEY, PATH_TO_DOCKER_PRIVATE_KEY
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

CFD_BASE_URL='https://dazfl01h50k5a.cloudfront.net' # Todo: Store this as an env var also prob directly via terraform

# Use the local private key when it's present (running `python routes.py`
# outside a container); fall back to the in-container path for docker.
PRIVATE_KEY_PATH = PATH_TO_LOCAL_PRIVATE_KEY if os.path.exists(PATH_TO_LOCAL_PRIVATE_KEY) else PATH_TO_DOCKER_PRIVATE_KEY

def generate_signed_urls(object_key):
    def rsa_signer(message):
        with open(PRIVATE_KEY_PATH, 'rb') as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None,
                backend=default_backend()
            )
        return private_key.sign(message, padding.PKCS1v15(), hashes.SHA1())

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
