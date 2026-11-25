from app.core.security import (
    hash_password,
    hash_token,
    new_session_token,
    verify_password,
)


def test_hash_is_not_the_password_and_verifies() -> None:
    hashed = hash_password("my-secret-password")
    assert hashed != "my-secret-password"
    assert hashed.startswith("$argon2")
    assert verify_password(hashed, "my-secret-password") is True


def test_wrong_password_fails() -> None:
    hashed = hash_password("my-secret-password")
    assert verify_password(hashed, "other-password") is False


def test_same_password_gets_different_hashes() -> None:
    assert hash_password("same") != hash_password("same")


def test_garbage_hash_does_not_crash() -> None:
    assert verify_password("not-a-hash", "whatever") is False


def test_session_tokens_are_unique_and_long() -> None:
    first, second = new_session_token(), new_session_token()
    assert first != second
    assert len(first) >= 40


def test_token_hash_is_stable_and_differs_from_token() -> None:
    token = new_session_token()
    assert hash_token(token) == hash_token(token)
    assert hash_token(token) != token
    assert len(hash_token(token)) == 64
