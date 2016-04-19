import pytest
from buckets import utils


def test_validate_settings(settings):
    settings.AWS = None
    with pytest.raises(AssertionError) as e:
        utils.validate_settings()
    assert 'No AWS settings found' in str(e.value)

    settings.AWS = {
        'ACCESS_KEY': 'A',
        'SECRET_KEY': 'S',
    }
    with pytest.raises(AssertionError) as e:
        utils.validate_settings()
    assert 'AWS bucket name is not set in settings' in str(e.value)

    settings.AWS = {
        'ACCESS_KEY': 'A',
        'BUCKET': 'B'
    }
    with pytest.raises(AssertionError) as e:
        utils.validate_settings()
    assert 'AWS secret key is not set in settings' in str(e.value)

    settings.AWS = {
        'SECRET_KEY': 'S',
        'BUCKET': 'B'
    }
    with pytest.raises(AssertionError) as e:
        utils.validate_settings()
    assert 'AWS access key is not set in settings' in str(e.value)
