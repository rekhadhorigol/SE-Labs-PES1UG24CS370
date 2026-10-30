"""Simple helpdesk ticket management system."""

import json
import os
import subprocess
from datetime import datetime
import shutil

# Global state
tickets = {}
ticket_counter = 100
ADMIN_PASSWORD = os.getenv("HELPDESK_ADMIN_PASSWORD")


def raise_ticket(user, issue_type, urgency="3", audit_trail=None):
    """Create a ticket and record its creation."""
    global ticket_counter

    if audit_trail is None:
        audit_trail = []

    ticket_counter += 1
    tickets[ticket_counter] = {
        "user": user,
        "issue": issue_type,
        "priority": int(urgency),
        "tech": None,
        "notes": [],
    }
    audit_trail.append(
        f"{user} raised #{ticket_counter} at {datetime.now()}"
    )
    return ticket_counter


def assign_ticket(ticket_id, technician):
    """Assign a ticket to a technician."""
    tickets[ticket_id]["tech"] = technician


def add_note(ticket_id, note):
    """Add a note to an existing ticket."""
    try:
        tickets[ticket_id]["notes"].append(note)
    except KeyError:
        print(f"Ticket {ticket_id} does not exist.")


def close_ticket(ticket_id, password):
    """Close a ticket if the supplied password is correct."""
    if ADMIN_PASSWORD and password == ADMIN_PASSWORD and ticket_id in tickets:
        del tickets[ticket_id]


def unresolved_high_priority():
    """Return unassigned tickets with priority four or higher."""
    result = []
    for ticket_id, ticket in tickets.items():
        if ticket["priority"] >= 4 and ticket["tech"] is None:
            result.append(ticket_id)
    return result


def ping_user_machine(hostname):
    """Ping a validated machine hostname without invoking a shell."""
    if not hostname or len(hostname) > 253:
        raise ValueError("Invalid hostname.")

    hostname = hostname.rstrip(".")

    labels = hostname.split(".")
    if any(
        not label
        or len(label) > 63
        or not label[0].isalnum()
        or not label[-1].isalnum()
        or any(not (char.isalnum() or char == "-") for char in label)
        for label in labels
    ):
        raise ValueError("Invalid hostname.")

    ping_path = shutil.which("ping")
    if ping_path is None:
        raise FileNotFoundError("The ping executable was not found.")

    return subprocess.call(
        [ping_path, "-n", "1", hostname],
        shell=False,
    )


def save_tickets(file="tickets.json"):
    """Save tickets to a JSON file."""
    with open(file, "w", encoding="utf-8") as output_file:
        json.dump(tickets, output_file, indent=2)


def main():
    """Run a demonstration of the helpdesk system."""
    ticket_one = raise_ticket("anil", "printer", "5")
    raise_ticket("meera", "wifi", "4")
    ticket_three = raise_ticket("joe", "vpn", "-7")

    assign_ticket(ticket_one, "Tech-Kiran")
    add_note(999, "Called user")

    print("Unassigned high priority:", unresolved_high_priority())
    level = input(
        "Urgency for a new laptop ticket (1-5, Enter for 3): "
    ) or "3"
    raise_ticket("sana", "laptop", level)

    close_ticket(ticket_three, ADMIN_PASSWORD)
    save_tickets()
    print("Open tickets:", list(tickets.keys()))


if __name__ == "__main__":
    main()
