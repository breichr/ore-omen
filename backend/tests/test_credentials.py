import pytest

from app.services.credentials import (
    RECOVERY_ALPHABET,
    CredentialError,
    new_recovery_key,
    normalize_recovery_key,
    username_key,
    validate_password,
    validate_username,
)


class TestUsername:
    @pytest.mark.parametrize("name", ["rosa", "Rosa_1878", "doc-mercy", "abc", "a" * 20])
    def test_valid(self, name):
        assert validate_username(name) == name

    def test_trims(self):
        assert validate_username("  rosa ") == "rosa"

    @pytest.mark.parametrize("name", ["ab", "a" * 21, ""])
    def test_length(self, name):
        with pytest.raises(CredentialError) as e:
            validate_username(name)
        assert e.value.code == "username_length"

    @pytest.mark.parametrize("name", ["rosa mae", "jörg", "rosa@x", "rosa.m"])
    def test_chars(self, name):
        with pytest.raises(CredentialError) as e:
            validate_username(name)
        assert e.value.code == "username_chars"

    def test_key_case_insensitive(self):
        assert username_key("Rosa") == username_key("rOSA ")


class TestPassword:
    def test_bounds(self):
        assert validate_password("a" * 8)
        assert validate_password("a" * 128)
        for bad in ("a" * 7, "a" * 129):
            with pytest.raises(CredentialError):
                validate_password(bad)


class TestRecoveryKey:
    def test_format(self):
        key = new_recovery_key()
        groups = key.split("-")
        assert len(groups) == 5
        assert all(len(g) == 5 and set(g) <= set(RECOVERY_ALPHABET) for g in groups)

    def test_random(self):
        assert len({new_recovery_key() for _ in range(50)}) == 50

    def test_normalize_roundtrip(self):
        key = new_recovery_key()
        assert normalize_recovery_key(key) == key.replace("-", "")

    def test_normalize_is_forgiving(self):
        assert (
            normalize_recovery_key("7k3qm d9xht-2vrpa w8nce-4fj6b") == "7K3QMD9XHT2VRPAW8NCE4FJ6B"
        )
        # look-alikes typed by hand
        assert normalize_recovery_key("O" * 25) == "0" * 25
        assert normalize_recovery_key("iIlL1" * 5) == "1" * 25

    @pytest.mark.parametrize(
        "bad", ["", "ABCDE", "U" * 25, "7K3QM-D9XHT-2VRPA-W8NCE-4FJ6", "!" * 25]
    )
    def test_normalize_rejects(self, bad):
        assert normalize_recovery_key(bad) is None
