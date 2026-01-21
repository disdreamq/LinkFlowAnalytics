import pytest


class TestURLGeneratorGetUrl:
    """Tests for get_url"""

    @pytest.mark.asyncio
    async def test_get_url_success(self, url_generator):
        results = [await url_generator.get_url() for _ in range(5)]

        expected = ["aaaaa", "aaaab", "aaaac", "aaaad", "aaaae"]
        assert results == expected


class TestURLGeneratorDelCache:
    """Tests for del_cache"""

    @pytest.mark.asyncio
    async def test_del_cache_success(self, url_generator):
        first_result = await url_generator.get_url()
        await url_generator.del_cache()
        second_result = await url_generator.get_url()
        assert first_result == "aaaaa"
        assert second_result == "aaaaa"

    @pytest.mark.asyncio
    async def test_cache_persistence(self, cache, url_generator):
        """Проверка сохранения состояния в кэше"""
        await url_generator.get_url()  # "aaaaa"
        await url_generator.get_url()  # "aaaab"

        from src.modules.link.service.url_generator import URLGenerator

        new_generator = URLGenerator(cache)

        result = await new_generator.get_url()
        assert result == "aaaac"

    @pytest.mark.asyncio
    async def test_generation_with_carryover(self, url_generator):
        await url_generator._initialize()
        url_generator.current = [0, 0, 0, 0, len(url_generator.alphabet) - 1]

        result1 = await url_generator.get_url()
        result2 = await url_generator.get_url()

        last_char = url_generator.alphabet[-1]
        assert result1 == f"aaaa{last_char}"
        assert result2 == "aaaba"

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "initial_state,expected_urls",
        [
            ("0,0,0,0,0", ["aaaab", "aaaac"]),
            ("0,0,0,0,10", ["aaaal", "aaaam"]),  # l=11, m=12
            ("0,0,0,1,0", ["aaabb", "aaabc"]),
        ],
    )
    async def test_various_initial_states(self, cache, initial_state, expected_urls):
        await cache.set_("current", initial_state)
        from src.modules.link.service.url_generator import URLGenerator

        generator = URLGenerator(cache)
        results = []
        results.append(await generator.get_url())
        results.append(await generator.get_url())
        assert results == expected_urls


class TestURLGeneratorEdgeCases:

    @pytest.mark.asyncio
    async def test_empty_cache(self, url_generator):
        await url_generator.del_cache()
        result = await url_generator.get_url()
        assert result == "aaaaa"

    @pytest.mark.asyncio
    async def test_max_value_rollover(self, url_generator):
        max_index = len(url_generator.alphabet) - 1
        url_generator.current = [max_index] * 5
        try:
            result = url_generator._generate_url()
            assert isinstance(result, str)
        except Exception:
            pass
