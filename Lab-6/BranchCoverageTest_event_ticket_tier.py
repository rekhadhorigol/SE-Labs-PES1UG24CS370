
import pytest
from event_ticket_tier import process_ticket_manifest, monitor_gate_flow


def make_manifest(
    tier="general",
    orders=None,
    confirmed=True,
    lounge=False,
):
    return {
        "is_confirmed": confirmed,
        "tier": tier,
        "orders": [] if orders is None else orders,
        "exclusive_lounge": lounge,
    }


@pytest.mark.parametrize(
    "manifests,tax",
    [
        ("not a list", 0),
        ([], -0.01),
    ],
)
def test_validation_rejection(manifests, tax):
    with pytest.raises(ValueError):
        process_ticket_manifest(manifests, tax)


def test_unconfirmed_manifest_is_skipped():
    assert process_ticket_manifest(
        [make_manifest(confirmed=False)], 0
    )["status"] == "ZERO_SALES"


@pytest.mark.parametrize(
    "tier,expected",
    [("vip", 150), ("premium", 90), ("general", 45)],
)
def test_each_supported_tier(tier, expected):
    result = process_ticket_manifest(
        [make_manifest(tier, [{"qty": 1}])], 0
    )
    assert result["total_revenue"] == expected


def test_unknown_tier_is_rejected():
    result = process_ticket_manifest(
        [make_manifest("student")], 0
    )
    assert result["status"] == "ZERO_SALES"


def test_zero_and_negative_quantities():
    result = process_ticket_manifest(
        [make_manifest(orders=[{"qty": 0}, {"qty": -2}])], 0
    )
    assert result["status"] == "ZERO_SALES"


def test_earlybird_and_volume_discount():
    result = process_ticket_manifest(
        [make_manifest(orders=[
            {"qty": 1, "promo": "EARLYBIRD"},
            {"qty": 4},
            {"qty": 5},
        ])],
        0,
    )
    assert result["total_revenue"] == 45 * 0.8 + 180 + 205


def test_fraud_for_vip_breaks_order_loop():
    result = process_ticket_manifest(
        [make_manifest("vip", [
            {"qty": 1, "promo": "FRAUD_RISK"},
            {"qty": 1},
        ])],
        0,
    )
    assert result["total_revenue"] == 0
    assert result["status"] == "ZERO_SALES"


def test_fraud_for_general_continues_order_loop():
    result = process_ticket_manifest(
        [make_manifest("general", [
            {"qty": 1, "promo": "FRAUD_RISK"},
            {"qty": 1},
        ])],
        0,
    )
    assert result["total_revenue"] == 90


def test_lounge_addon():
    result = process_ticket_manifest(
        [make_manifest(orders=[{"qty": 1}], lounge=True)], 0
    )
    assert result["total_revenue"] == 120


def test_audit_threshold():
    orders = [{"qty": 0} for _ in range(5)]
    assert process_ticket_manifest(
        [make_manifest(orders=orders)], 0
    )["status"] == "AUDIT_REJECTED"

    orders = [{"qty": 0} for _ in range(4)]
    assert process_ticket_manifest(
        [make_manifest(orders=orders)], 0
    )["status"] == "ZERO_SALES"


def test_completed_status_and_tax():
    result = process_ticket_manifest(
        [make_manifest(orders=[{"qty": 2}])], 0.1
    )
    assert result == {
        "total_revenue": 99.0,
        "status": "COMPLETED",
    }


def test_empty_gate_data():
    assert monitor_gate_flow([]) == "NO_DATA"


def test_congestion_needs_two_consecutive_high_rates():
    assert monitor_gate_flow([[51]]) == "FLOW_NORMAL"
    assert monitor_gate_flow([[51, 52]]) == "OVERFLOW"


def test_low_rate_resets_congestion_streak():
    assert monitor_gate_flow([[51, 20, 52]]) == "FLOW_NORMAL"


def test_multiple_streams():
    assert monitor_gate_flow([[51], [52, 53]]) == "OVERFLOW"
    assert monitor_gate_flow([[], [10, 20]]) == "FLOW_NORMAL"
