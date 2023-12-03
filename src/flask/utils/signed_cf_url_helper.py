import datetime
from botocore.signers import CloudFrontSigner
from temp_secrets import PUBLIC_KEY_ID, PATH_TO_LOCAL_PRIVATE_KEY, PATH_TO_DOCKER_PRIVATE_KEY
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

CFD_BASE_URL='https://dazfl01h50k5a.cloudfront.net' # Todo: Store this as an env var also prob directly via terraform

def generate_signed_urls(object_key):
    def rsa_signer(message):
        with open(PATH_TO_LOCAL_PRIVATE_KEY, 'rb') as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None,
                backend=default_backend()
            )
        return private_key.sign(message, padding.PKCS1v15(), hashes.SHA1())

    key_id = PUBLIC_KEY_ID
    url = f"{CFD_BASE_URL}/{object_key}"
    expire_date = datetime.datetime.today() + datetime.timedelta(days=1)

    cloudfront_signer = CloudFrontSigner(key_id, rsa_signer)

    # Create a signed url that will be valid until the specific expiry date
    # provided using a canned policy.
    signed_url = cloudfront_signer.generate_presigned_url(
        url, date_less_than=expire_date)
    return signed_url
