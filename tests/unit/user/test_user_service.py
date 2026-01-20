import datetime
from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import IntegrityError, NoResultFound, SQLAlchemyError

from src.core.exceptions.exceptions import (
    AlreadyExistsException,
    DataBaseException,
    NotFoundException,
    ValidationException,
)
from src.enums.enums import UserTarifPlan
from src.modules.link.schemas import SLinkResponse
from src.modules.user.schemas import SUserInDB, SUserResponse, SUserWithLinks


class TestUserServiceCreate:
    """Tests for create"""

    @pytest.mark.asyncio
    async def test_create_success(
        self,
        mock_user_repo,
        user_service,
        sample_user_create,
    ):
        """User create success"""
        plain_password = sample_user_create.password
        mock_user_repo.exists_by_email.return_value = False
        mock_user_repo.create.return_value = MagicMock(
            id=1, email=sample_user_create.email, tarifplan=UserTarifPlan.Base
        )

        result = await user_service.create(sample_user_create)

        assert isinstance(result, SUserResponse)
        assert result.id == 1
        assert result.email == sample_user_create.email
        assert result.tarifplan == UserTarifPlan.Base
        call_args = mock_user_repo.create.call_args
        assert "password" in call_args.kwargs
        password = call_args.kwargs["password"]
        assert password != plain_password

    @pytest.mark.asyncio
    async def test_create_fail_not_unique_email(
        self,
        mock_user_repo,
        user_service,
        sample_user_create,
    ):
        """User create fail due to not unique user email"""
        mock_user_repo.exists_by_email.return_value = True

        with pytest.raises(AlreadyExistsException) as exc_info:
            await user_service.create(sample_user_create)

        assert sample_user_create.email in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_fail_due_to_db_error(
        self, mock_user_repo, user_service, sample_user_create
    ):
        """User create fail due to database error"""
        mock_user_repo.exists_by_email.return_value = False
        mock_user_repo.create.side_effect = SQLAlchemyError(
            "Database connection failed"
        )
        with pytest.raises(DataBaseException):
            await user_service.create(sample_user_create)


class TestUserServiceGetById:
    """Tests for get_by_id"""

    @pytest.mark.asyncio
    async def test_get_by_id_success(
        self, mock_user_repo, user_service, sample_user_data
    ):
        mock_user_repo.get_by_email.return_value = sample_user_data

        result = await user_service.get_by_email(sample_user_data["email"])

        assert isinstance(result, SUserInDB)
        assert result.id == sample_user_data["id"]
        assert result.email == sample_user_data["email"]

    @pytest.mark.parametrize(
        "Db_exception, buisuness_exception",
        [
            (NoResultFound, NotFoundException),
            (IntegrityError, ValidationException),
            (SQLAlchemyError, DataBaseException),
        ],
    )
    @pytest.mark.asyncio
    async def test_user_by_email_fail(
        self, mock_user_repo, user_service, Db_exception, buisuness_exception
    ):
        mock_user_repo.get_by_email.side_effect = Db_exception("1", "2", "3")
        with pytest.raises(buisuness_exception):
            await user_service.get_by_email("pisyatdva@example.com")


class TestUserServiceGetByEmail:
    """Tests for get_by_email"""

    @pytest.mark.asyncio
    async def test_user_by_email_success(
        self, mock_user_repo, user_service, sample_user_data
    ):
        mock_user_repo.get_by_id.return_value = sample_user_data

        result = await user_service.get_by_id(sample_user_data["id"])

        assert isinstance(result, SUserInDB)
        assert result.id == sample_user_data["id"]
        assert result.email == sample_user_data["email"]

    @pytest.mark.parametrize(
        "Db_exception, buisuness_exception",
        [
            (NoResultFound, NotFoundException),
            (IntegrityError, ValidationException),
            (SQLAlchemyError, DataBaseException),
        ],
    )
    @pytest.mark.asyncio
    async def test_get_by_id_fail(
        self, mock_user_repo, user_service, Db_exception, buisuness_exception
    ):
        mock_user_repo.get_by_id.side_effect = Db_exception("1", "2", "3")
        with pytest.raises(buisuness_exception):
            await user_service.get_by_id(52)


class TestUserServiceGetWithLinks:
    """Tests for get_with_links"""

    @pytest.mark.asyncio
    async def test_get_with_links_success(
        self, mock_user_repo, user_service, sample_user_data
    ):
        """Test for get_with_links success"""
        user_with_links = {
            **sample_user_data,
            "links": [
                SLinkResponse(
                    id=1,
                    user_id=1,
                    base_url="https://example.com",
                    url="aaaaa",
                    click_counter=5,
                    created_at=datetime.datetime.now(),
                    updated_at=datetime.datetime.now(),
                ),
                SLinkResponse(
                    id=2,
                    user_id=1,
                    base_url="https://example.com",
                    url="aaaab",
                    click_counter=5,
                    created_at=datetime.datetime.now(),
                    updated_at=datetime.datetime.now(),
                ),
            ],
        }
        mock_user_repo.get_with_links.return_value = user_with_links

        result = await user_service.get_with_links(user_with_links["id"])

        assert isinstance(result, SUserWithLinks)
        assert isinstance(result.links[0], SLinkResponse)
        assert isinstance(result.links[1], SLinkResponse)
        assert result.id == user_with_links["id"]
        assert result.email == user_with_links["email"]

    @pytest.mark.parametrize(
        "Db_exception, buisuness_exception",
        [
            (NoResultFound, NotFoundException),
            (IntegrityError, ValidationException),
            (SQLAlchemyError, DataBaseException),
        ],
    )
    @pytest.mark.asyncio
    async def test_get_with_links_fail(
        self, mock_user_repo, user_service, Db_exception, buisuness_exception
    ):
        mock_user_repo.get_with_links.side_effect = Db_exception("1", "2", "3")
        with pytest.raises(buisuness_exception):
            await user_service.get_with_links(52)


class TestUserServiceUpdate:
    """Tests for update"""

    # TODO СДелать тест для обновления части данных и всех данных
    @pytest.mark.asyncio
    async def test_update_success(
        self, mock_user_repo, user_service, sample_user_update
    ):
        """Test for update success"""
        mock_user_repo.update.return_value = SUserResponse(
            **sample_user_update.model_dump(),
            created_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now(),
        )

        result = await user_service.update(sample_user_update)

        assert isinstance(result, SUserResponse)
        assert result.id == sample_user_update.id
        assert result.email == sample_user_update.email
        assert result.tarifplan == UserTarifPlan.Premium

    @pytest.mark.parametrize(
        "Db_exception, buisuness_exception",
        [
            (NoResultFound, NotFoundException),
            (IntegrityError, ValidationException),
            (SQLAlchemyError, DataBaseException),
        ],
    )
    @pytest.mark.asyncio
    async def test_update_fail(
        self,
        mock_user_repo,
        user_service,
        Db_exception,
        buisuness_exception,
        sample_user_update,
    ):
        mock_user_repo.update.side_effect = Db_exception("1", "2", "3")
        with pytest.raises(buisuness_exception):
            await user_service.update(sample_user_update)


class TestUserServiceDelete:
    """Tests for delete"""

    @pytest.mark.asyncio
    async def test_delete_success(
        self,
        mock_user_repo,
        user_service,
    ):
        """Test for delete success"""
        user_id = 1
        mock_user_repo.delete.return_value = True

        result = await user_service.delete(user_id)

        assert result is True

    @pytest.mark.parametrize(
        "Db_exception, buisuness_exception",
        [
            (NoResultFound, NotFoundException),
            (IntegrityError, ValidationException),
            (SQLAlchemyError, DataBaseException),
        ],
    )
    @pytest.mark.asyncio
    async def test_update_fail(
        self,
        mock_user_repo,
        user_service,
        Db_exception,
        buisuness_exception,
    ):
        mock_user_repo.delete.side_effect = Db_exception("1", "2", "3")
        with pytest.raises(buisuness_exception):
            await user_service.delete(52)
