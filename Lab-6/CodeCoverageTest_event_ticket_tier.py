
import pytest
from event_ticket_tier import process_ticket_manifest, monitor_gate_flow


def manifest(tier="general", orders=None, confirmed=True, lounge=False):
    return {
        "is_confirmed": confirmed,
        "tier": tier,
        "orders": orders or [],
        "exclusive_lounge": lounge,
    }


def test_general_vip_and_premium_tiers():
    for tier, price in [("general", 45), ("premium", 90), ("vip", 150)]:
        result = process_ticket_manifest(
            [manifest(tier, [{"qty": 1}])], 0
        )
        assert result["total_revenue"] == price
        assert result["status"] == "COMPLETED"


def test_unconfirmed_and_unknown_tier():
    result = process_ticket_manifest(
        [manifest(confirmed=False), manifest("invalid")], 0
    )
    assert result["status"] == "ZERO_SALES"


def test_order_quantity_and_promotions():
    result = process_ticket_manifest(
        [manifest("general", [
            {"qty": 0},
            {"qty": 2, "promo": "EARLYBIRD"},
            {"qty": 5},
        ])],
        0.1,
    )
    assert result["total_revenue"] == 304.7
    assert result["status"] == "COMPLETED"


def test_fraud_vip_and_non_vip():
    result = process_ticket_manifest(
        [
            manifest("vip", [
                {"qty": 1, "promo": "FRAUD_RISK"},
                {"qty": 2},
            ]),
            manifest("general", [
                {"qty": 1, "promo": "FRAUD_RISK"},
                {"qty": 1},
            ]),
        ],
        0,
    )
    assert result["total_revenue"] == 90
    assert result["status"] == "COMPLETED"


def test_lounge_tax_and_zero_sales():
    result = process_ticket_manifest(
        [manifest("general", [{"qty": 1}], lounge=True)], 0.1
    )
    assert result["total_revenue"] == 132
    assert process_ticket_manifest([], 0)["status"] == "ZERO_SALES"


@pytest.mark.parametrize(
    "manifests,tax",
    [
        ("invalid", 0),
        ([], -0.1),
    ],
)
def test_invalid_input(manifests, tax):
    with pytest.raises(ValueError):
        process_ticket_manifest(manifests, tax)


def test_audit_rejection():
    orders = [{"qty": 0} for _ in range(5)]
    result = process_ticket_manifest([manifest(orders=orders)], 0)
    assert result["status"] == "AUDIT_REJECTED"


def test_gate_flow():
    assert monitor_gate_flow([]) == "NO_DATA"
    assert monitor_gate_flow([[10, 20, 30]]) == "FLOW_NORMAL"
    assert monitor_gate_flow([[51, 52]]) == "OVERFLOW"
