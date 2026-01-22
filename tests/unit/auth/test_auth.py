from unittest.mock import patch

import jwt
import pytest

from src.core.exceptions.exceptions import AuthenticationException
from src.modules.auth.service import authenticate_user, create_access_token
from src.modules.user.schemas import SUserInDB


class TestAuthenticateUser:
    """Tests for authenticate_user"""

    @pytest.mark.asyncio
    async def test_authenticate_user_success(
        self, mock_user_service, sample_user_in_db
    ):
        email = "test@example.com"
        password = "correct_password"

        mock_user_service.get_by_email.return_value = sample_user_in_db

        with patch("src.modules.auth.service.verify_password") as mock_verify:
            mock_verify.return_value = True

            result = await authenticate_user(mock_user_service, email, password)

            assert isinstance(result, SUserInDB)
            assert result.email == email
            mock_user_service.get_by_email.assert_called_once_with(email)
            mock_verify.assert_called_once_with(
                plain_password=password, hash_password=sample_user_in_db.password
            )

    @pytest.mark.asyncio
    async def test_authenticate_user_not_found(self, mock_user_service):
        """Test for not exists user auth"""

        email = "nonexistent@example.com"
        password = "password123"

        mock_user_service.get_by_email.return_value = None

        with pytest.raises(AuthenticationException) as exc_info:
            await authenticate_user(mock_user_service, email, password)

        assert email in str(exc_info.value)
        mock_user_service.get_by_email.assert_called_once_with(email)

    @pytest.mark.asyncio
    async def test_authenticate_user_wrong_password(
        self, mock_user_service, sample_user_in_db
    ):
        """Test for wrong password user"""
        email = "test@example.com"
        wrong_password = "wrong_password"

        mock_user_service.get_by_email.return_value = sample_user_in_db

        with patch("src.modules.auth.service.verify_password") as mock_verify:
            mock_verify.return_value = False

            with pytest.raises(AuthenticationException) as exc_info:
                await authenticate_user(mock_user_service, email, wrong_password)

            assert email in str(exc_info.value)
            mock_user_service.get_by_email.assert_called_once_with(email)
            mock_verify.assert_called_once_with(
                plain_password=wrong_password, hash_password=sample_user_in_db.password
            )

    @pytest.mark.asyncio
    async def test_authenticate_user_empty_password(
        self, mock_user_service, sample_user_in_db
    ):
        """Test for user with empty password"""

        email = "test@example.com"
        empty_password = ""

        mock_user_service.get_by_email.return_value = sample_user_in_db

        with patch("src.modules.auth.service.verify_password") as mock_verify:
            mock_verify.return_value = False

            with pytest.raises(AuthenticationException):
                await authenticate_user(mock_user_service, email, empty_password)

    @pytest.mark.asyncio
    async def test_authenticate_user_service_raises_exception(self, mock_user_service):

        email = "test@example.com"
        password = "password123"

        mock_user_service.get_by_email.side_effect = Exception("Database error")

        with pytest.raises(Exception) as exc_info:
            await authenticate_user(mock_user_service, email, password)

        assert "Database error" in str(exc_info.value)
        mock_user_service.get_by_email.assert_called_once_with(email)


class TestCreateAccessToken:
    """Tests for create_access_token"""

    def test_create_access_token(self, mock_settings, sample_token_data):
        """Create token with out expires_delta, 15 mins default"""
        with (
            patch("src.core.config.get_settings", return_value=mock_settings),
            patch("src.modules.auth.service.jwt.encode") as mock_jwt_encode,
        ):
            mock_jwt_encode.return_value = "encoded_jwt_token"

            result = create_access_token(sample_token_data)

            assert result.access_token == "encoded_jwt_token"
            assert result.token_type == "bearer"

    def test_create_access_token_empty_data(self, mock_settings):
        empty_data = {}

        with (
            patch("src.modules.auth.service.get_settings", return_value=mock_settings),
            patch("src.modules.auth.service.jwt.encode") as mock_jwt_encode,
        ):
            mock_jwt_encode.return_value = "encoded_empty_token"

            result = create_access_token(empty_data)

            assert result.access_token == "encoded_empty_token"
            call_payload = mock_jwt_encode.call_args[0][0]
            assert "exp" in call_payload

    def test_create_access_token_with_additional_fields(
        self, mock_settings, sample_token_data
    ):
        """Test for create token with extra data"""
        extended_data = {
            **sample_token_data,
            "role": "admin",
            "permissions": ["read", "write"],
            "custom_field": "custom_value",
        }

        with (
            patch("src.modules.auth.service.get_settings", return_value=mock_settings),
            patch("src.modules.auth.service.jwt.encode") as mock_jwt_encode,
        ):
            mock_jwt_encode.return_value = "encoded_extended_token"

            create_access_token(extended_data)

            call_payload = mock_jwt_encode.call_args[0][0]
            assert "role" in call_payload
            assert "permissions" in call_payload
            assert "custom_field" in call_payload

    def test_create_access_token_jwt_encoding_error(
        self, mock_settings, sample_token_data
    ):
        """Test for jwt encoding error"""

        with (
            patch("src.modules.auth.service.get_settings", return_value=mock_settings),
            patch("src.modules.auth.service.jwt.encode") as mock_jwt_encode,
        ):
            mock_jwt_encode.side_effect = jwt.PyJWTError("Invalid key")

            with pytest.raises(jwt.PyJWTError):
                create_access_token(sample_token_data)

    def test_create_access_token_verify_token_structure(
        self, mock_settings, sample_token_data
    ):
        """Test for verity token structure"""

        with patch("src.modules.auth.service.get_settings", return_value=mock_settings):
            result = create_access_token(sample_token_data)

            assert hasattr(result, "access_token")
            assert hasattr(result, "token_type")
            assert result.token_type == "bearer"
            assert isinstance(result.access_token, str)
            assert len(result.access_token) > 0
