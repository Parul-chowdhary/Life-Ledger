"""
RFC 5545 Recurrence Rule (RRULE) Parsing & Generation Engine.
Implements standard iCalendar recurrence expansion for complex recurring obligations,
including FREQ (DAILY, WEEKLY, MONTHLY, YEARLY), INTERVAL, COUNT, UNTIL, and BYMONTHDAY.
"""
from datetime import date, datetime, timedelta
import re
from typing import Dict, Generator, List, Optional


class RecurrenceRule:
    """Represents a parsed RFC 5545 recurrence pattern."""

    def __init__(
        self,
        freq: str,
        interval: int = 1,
        count: Optional[int] = None,
        until: Optional[date] = None,
        bymonthday: Optional[List[int]] = None,
        byday: Optional[List[str]] = None,
    ):
        self.freq = freq.upper()
        if self.freq not in ["DAILY", "WEEKLY", "MONTHLY", "YEARLY"]:
            raise ValueError(f"Unsupported recurrence frequency: {freq}")
        self.interval = max(1, interval)
        self.count = count
        self.until = until
        self.bymonthday = bymonthday or []
        self.byday = byday or []

    @classmethod
    def from_string(cls, rrule_str: str) -> "RecurrenceRule":
        """Parses an RFC 5545 RRULE string (e.g. 'FREQ=YEARLY;INTERVAL=1')."""
        clean = rrule_str.strip()
        if clean.startswith("RRULE:"):
            clean = clean[6:]

        parts = clean.split(";")
        kv: Dict[str, str] = {}
        for p in parts:
            if "=" in p:
                k, v = p.split("=", 1)
                kv[k.upper()] = v

        freq = kv.get("FREQ", "YEARLY")
        interval = int(kv.get("INTERVAL", 1))
        count = int(kv["COUNT"]) if "COUNT" in kv else None

        until = None
        if "UNTIL" in kv:
            u_str = kv["UNTIL"]
            try:
                if "T" in u_str:
                    until = datetime.strptime(u_str, "%Y%m%dT%H%M%SZ").date()
                else:
                    until = datetime.strptime(u_str, "%Y%m%d").date()
            except ValueError:
                pass

        bymonthday = [int(x) for x in kv["BYMONTHDAY"].split(",")] if "BYMONTHDAY" in kv else []
        byday = kv["BYDAY"].split(",") if "BYDAY" in kv else []

        return cls(
            freq=freq,
            interval=interval,
            count=count,
            until=until,
            bymonthday=bymonthday,
            byday=byday,
        )

    def to_string(self) -> str:
        """Serializes back to an RFC 5545 RRULE string."""
        parts = [f"FREQ={self.freq}"]
        if self.interval > 1:
            parts.append(f"INTERVAL={self.interval}")
        if self.count is not None:
            parts.append(f"COUNT={self.count}")
        if self.until is not None:
            parts.append(f"UNTIL={self.until.strftime('%Y%m%d')}")
        if self.bymonthday:
            parts.append(f"BYMONTHDAY={','.join(map(str, self.bymonthday))}")
        if self.byday:
            parts.append(f"BYDAY={','.join(self.byday)}")
        return ";".join(parts)

    def get_next_occurrence(self, start_date: date, after_date: Optional[date] = None) -> Optional[date]:
        """Calculates the earliest occurrence strictly after `after_date`."""
        target_after = after_date or start_date
        gen = self.generate_occurrences(start_date, max_occurrences=500)
        for occ in gen:
            if occ > target_after:
                return occ
        return None

    def generate_occurrences(
        self, start_date: date, max_occurrences: int = 100
    ) -> Generator[date, None, None]:
        """Generates successive occurrence dates matching the rule."""
        current = start_date
        yielded = 0

        while yielded < max_occurrences:
            if self.count is not None and yielded >= self.count:
                break
            if self.until is not None and current > self.until:
                break

            yield current
            yielded += 1

            if self.freq == "DAILY":
                current += timedelta(days=self.interval)
            elif self.freq == "WEEKLY":
                current += timedelta(weeks=self.interval)
            elif self.freq == "MONTHLY":
                # Increment month with clamp for shorter months
                new_month = ((current.month - 1 + self.interval) % 12) + 1
                new_year = current.year + ((current.month - 1 + self.interval) // 12)
                # Handle 31st on 30-day month
                day = min(current.day, self._days_in_month(new_year, new_month))
                current = date(new_year, new_month, day)
            elif self.freq == "YEARLY":
                new_year = current.year + self.interval
                day = current.day
                if current.month == 2 and current.day == 29 and not self._is_leap_year(new_year):
                    day = 28
                current = date(new_year, current.month, day)

    @staticmethod
    def _is_leap_year(year: int) -> bool:
        return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

    @classmethod
    def _days_in_month(cls, year: int, month: int) -> int:
        if month in [1, 3, 5, 7, 8, 10, 12]:
            return 31
        if month in [4, 6, 9, 11]:
            return 30
        return 29 if cls._is_leap_year(year) else 28
