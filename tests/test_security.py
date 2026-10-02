import pytest

from sitepulse.security import validate_public_url


@pytest.mark.parametrize(
    "url",
    [
        "http://127.0.0.1",
        "http://localhost",
        "http://10.0.0.1",
        "http://192.168.1.1",
        "http://169.254.169.254",
    ],
)
def test_private_and_local_targets_are_rejected(url):
    with pytest.raises(ValueError, match="public website"):
        validate_public_url(url)
