import string
import random
from django.conf import settings


def validate_settings():
    assert settings.AWS, \
        "No AWS settings found"
    assert settings.AWS.get('ACCESS_KEY'), \
        "AWS access key is not set in settings"
    assert settings.AWS.get('SECRET_KEY'), \
        "AWS secret key is not set in settings"
    assert settings.AWS.get('BUCKET'), \
        "AWS bucket name is not set in settings"


ID_FIELD_LENGTH = 24

alphabet = string.ascii_lowercase + string.digits
for loser in 'l1o0':
    i = alphabet.index(loser)
    alphabet = alphabet[:i] + alphabet[i + 1:]


def byte_to_base32_chr(byte):
    return alphabet[byte & 31]


def random_id():
    rand_id = [random.randint(0, 0xFF) for i in range(ID_FIELD_LENGTH)]
    return ''.join(map(byte_to_base32_chr, rand_id))
