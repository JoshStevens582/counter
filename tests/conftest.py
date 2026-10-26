from __future__ import annotations

import pytest

from counter.config import Settings


@pytest.fixture
def settings() -> Settings:
    return Settings(openai_api_key="sk-test", hybrid_search_enabled=False)
