# Task 13 - Booking Conflict Scheduler
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Booking:
    booking_id: str
    room: str
    start: datetime
    end: datetime


@dataclass(frozen=True)
class BookingResult:
    accepted: bool
    reason: str = ""
    conflicts: tuple = ()


class Scheduler:
    def __init__(self):
        self._by_room = {}
        self._ids = set()

    def add_booking(self, booking_id, room, start, end):
        """Accept the booking if it does not overlap another one in the room.
        Adjacent bookings (end == next start) are allowed."""
        if not isinstance(start, datetime) or not isinstance(end, datetime):
            raise TypeError("start and end must be datetime objects")
        if end <= start:
            return BookingResult(False, "end must be after start")
        if booking_id in self._ids:
            return BookingResult(False, f"duplicate booking id {booking_id!r}")

        bookings = self._by_room.setdefault(room, [])
        conflicts = tuple(b for b in bookings if start < b.end and b.start < end)
        if conflicts:
            return BookingResult(False, "time conflict", conflicts)

        bookings.append(Booking(booking_id, room, start, end))
        bookings.sort(key=lambda b: b.start)
        self._ids.add(booking_id)
        return BookingResult(True)

    def bookings_for(self, room):
        return list(self._by_room.get(room, []))


if __name__ == "__main__":
    def at(h, m=0):
        return datetime(2026, 11, 9, h, m)

    s = Scheduler()
    print(s.add_booking("b1", "A", at(9), at(10)))
    print(s.add_booking("b2", "A", at(10), at(11)))
    res = s.add_booking("b3", "A", at(9, 30), at(10, 30))
    print(res.accepted, res.reason, [b.booking_id for b in res.conflicts])
    print(s.add_booking("b4", "B", at(9, 30), at(10, 30)))
    print(s.add_booking("b1", "C", at(9), at(10)))
    print(s.add_booking("b5", "A", at(12), at(12)))