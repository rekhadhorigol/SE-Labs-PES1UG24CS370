
def decode_promo_voucher(voucher_code):
    if not isinstance(voucher_code, str):
        return "Invalid voucher code"

    code = voucher_code.strip()

    if code.count("-") != 1:
        return "Invalid voucher code"

    prefix, pct_str = code.split("-", 1)
    prefix = prefix.strip()

    if not prefix or not pct_str.strip():
        return "Invalid voucher code"

    try:
        percentage = int(pct_str.strip())
    except ValueError:
        return "Invalid voucher code"

    if not 0 <= percentage <= 100:
        return "Invalid voucher code"

    return f"Valid {prefix.upper()}: {percentage}% OFF"


def calculate_seat_tier_price(tier_spec):
    if not isinstance(tier_spec, str):
        return None

    parts = tier_spec.split("@")

    if len(parts) != 2:
        return None

    tier = parts[0].strip().upper()
    row_text = parts[1].strip()

    tier_rates = {
        "VIP": 150.0,
        "PREMIUM": 90.0,
        "GENERAL": 45.0
    }

    if tier not in tier_rates or not row_text:
        return None

    try:
        row = int(row_text)
    except ValueError:
        return None

    if row < 0:
        return None

    return tier_rates[tier] + (row * 2.0)


def parse_attendee_badge(badge_csv):
    if not isinstance(badge_csv, str):
        return "Invalid attendee badge"

    tokens = badge_csv.split(",")

    if len(tokens) != 3:
        return "Invalid attendee badge"

    name = tokens[0].strip()
    age_text = tokens[1].strip()
    seat = tokens[2].strip()

    if not name or not age_text or not seat:
        return "Invalid attendee badge"

    try:
        age = int(age_text)
    except ValueError:
        return "Invalid attendee badge"

    if age < 0:
        return "Invalid attendee badge"

    category = "Child" if age < 18 else "Adult"

    return f"{name} [{category}] - Seat {seat}"


def main():
    print("==== Running decode_promo_voucher ====")
    v_input = input("Enter voucher (e.g. EARLY-20): ")
    print("Voucher:", decode_promo_voucher(v_input))

    print("\n==== Running calculate_seat_tier_price ====")
    t_input = input("Enter tier spec (e.g. VIP@4): ")
    print("Seat Price:", calculate_seat_tier_price(t_input))

    print("\n==== Running parse_attendee_badge ====")
    b_input = input("Enter badge CSV (Name,Age,Seat): ")
    print("Badge:", parse_attendee_badge(b_input))


if __name__ == "__main__":
    main()
