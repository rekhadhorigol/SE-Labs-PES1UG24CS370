
from hypothesis import given, strategies as st

from processor import (
    decode_promo_voucher,
    calculate_seat_tier_price,
    parse_attendee_badge,
)


@given(st.text() | st.none())
def test_decode_promo_voucher_no_crash(value):
    try:
        decode_promo_voucher(value)
    except Exception as error:
        assert False, f"decode_promo_voucher crashed with {value!r}: {error}"


@given(st.text() | st.none())
def test_calculate_seat_tier_price_safe(value):
    try:
        calculate_seat_tier_price(value)
    except Exception as error:
        assert False, f"calculate_seat_tier_price crashed with {value!r}: {error}"


@given(st.text() | st.none())
def test_parse_attendee_badge_safe(value):
    try:
        parse_attendee_badge(value)
    except Exception as error:
        assert False, f"parse_attendee_badge crashed with {value!r}: {error}"
