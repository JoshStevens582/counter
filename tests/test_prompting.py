from counter.services.prompting import DEVELOPER_INSTRUCTIONS, build_user_payload
from tests.stubs import fees_chunk


def test_developer_instructions_refuse_booking_and_mail() -> None:
    lowered = DEVELOPER_INSTRUCTIONS.casefold()
    assert "does not book" in lowered or "cannot book" in lowered
    assert "send" in lowered
    assert "do not know" in lowered


def test_developer_instructions_forbid_em_dashes() -> None:
    assert "\u2014" not in DEVELOPER_INSTRUCTIONS
    assert "do not use em dashes" in DEVELOPER_INSTRUCTIONS.casefold()


def test_build_user_payload_wraps_context() -> None:
    payload = build_user_payload("What does it cost?", [fees_chunk()])
    assert "<context>" in payload
    assert "Session fees" in payload
    assert "<user_query>" in payload
