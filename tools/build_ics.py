"""Build ab-calendar.ics, the subscribable feed for the AB Calendar.

Run from the repo root:  python3 tools/build_ics.py
Keep the dates here in step with index.html.
"""
from datetime import date, timedelta, datetime, timezone

Y = 2027
TZ = "America/New_York"
OUT = "ab-calendar.ics"

HOLIDAY_MONDAYS = {
    date(Y, 1, 18): "MLK Day",
    date(Y, 2, 15): "Presidents' Day",
    date(Y, 5, 31): "Memorial Day",
    date(Y, 7, 5): "July 4th observed",
    date(Y, 9, 6): "Labor Day",
}
CANCELLED_MEETINGS = {1: "New Year's weekend", 7: "July 4th weekend", 9: "Labor Day weekend"}
CANCELLED_ACCESS = {}
ACCESS_WEDNESDAY = {11, 12}  # Nov & Dec 2027: Wednesday before the 4th Thursday
KEY_DATES = [
    (date(Y, 3, 26), "Good Friday"),
    (date(Y, 3, 28), "Easter Sunday (All Hands)"),
    (date(Y, 5, 9), "Mother's Day"),
    (date(Y, 6, 20), "Father's Day"),
    (date(Y, 12, 26), "Christmas Sunday (All Hands)"),
]
OUTINGS = [(date(Y, 3, 20), "Q1"), (date(Y, 6, 12), "Q2"), (date(Y, 9, 18), "Q3"), (date(Y, 12, 11), "Q4")]

VTIMEZONE = """BEGIN:VTIMEZONE
TZID:America/New_York
BEGIN:DAYLIGHT
TZOFFSETFROM:-0500
TZOFFSETTO:-0400
TZNAME:EDT
DTSTART:19700308T020000
RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=2SU
END:DAYLIGHT
BEGIN:STANDARD
TZOFFSETFROM:-0400
TZOFFSETTO:-0500
TZNAME:EST
DTSTART:19701101T020000
RRULE:FREQ=YEARLY;BYMONTH=11;BYDAY=1SU
END:STANDARD
END:VTIMEZONE"""

STAMP = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def esc(s):
    return s.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def fold(line):
    out, b = [], line.encode()
    while len(b) > 74:
        cut = 74
        while (b[cut] & 0xC0) == 0x80:
            cut -= 1
        out.append(b[:cut].decode())
        b = b" " + b[cut:]
    out.append(b.decode())
    return "\r\n".join(out)


events = []


def add(uid, summary, start, end=None, hours=None, desc=None, free=False, tentative=False, rrule=None, url=None):
    lines = ["BEGIN:VEVENT", f"UID:{uid}@ab-calendar", f"DTSTAMP:{STAMP}", f"SUMMARY:{esc(summary)}"]
    if rrule:
        lines.append(f"RRULE:{rrule}")
    if url:
        lines.append(f"URL:{url}")
    if hours:
        (h1, m1), (h2, m2) = hours
        lines.append(f"DTSTART;TZID={TZ}:{start:%Y%m%d}T{h1:02d}{m1:02d}00")
        lines.append(f"DTEND;TZID={TZ}:{start:%Y%m%d}T{h2:02d}{m2:02d}00")
    else:
        lines.append(f"DTSTART;VALUE=DATE:{start:%Y%m%d}")
        lines.append(f"DTEND;VALUE=DATE:{(end or start + timedelta(days=1)):%Y%m%d}")
    if desc:
        lines.append(f"DESCRIPTION:{esc(desc)}")
        if "zoom.us" in desc:
            lines.append("LOCATION:Zoom")
            lines.append("URL:https://us02web.zoom.us/j/84578356424")
    if tentative:
        lines.append("STATUS:TENTATIVE")
    lines.append(f"TRANSP:{'TRANSPARENT' if free or not hours else 'OPAQUE'}")
    lines.append("END:VEVENT")
    events.append("\r\n".join(fold(l) for l in lines))


def nth_weekday(month, weekday, n):
    d = date(Y, month, 1)
    d += timedelta(days=(weekday - d.weekday()) % 7)
    return d + timedelta(weeks=n - 1)


# AB Summit
add("summit-2027", "AB Summit", date(Y, 1, 30))

# Consecration week (tentative)
add("consecration-2027", "Consecration Week - church-wide fast (Tentative)", date(Y, 1, 4),
    end=date(Y, 1, 10), tentative=True)

# Key dates
for d, name in KEY_DATES:
    add(f"key-{d:%Y%m%d}", name, d)

# Team meetings: first Saturday, 10am-2pm
for m in range(1, 13):
    d = nth_weekday(m, 5, 1)
    if m in CANCELLED_MEETINGS:
        add(f"meet-{d:%Y%m%d}", f"CANCELLED - AB Team Meeting ({CANCELLED_MEETINGS[m]})", d,
            hours=((10, 0), (14, 0)), free=True, desc="Cancelled. No team meeting this month.")
    else:
        add(f"meet-{d:%Y%m%d}", "AB Team Meeting", d, hours=((10, 0), (14, 0)))

# Monday SWOTs, 7pm on Zoom (Nov 2026 through Dec 2027)
ZOOM = "https://us02web.zoom.us/j/84578356424"
SWOT_DESC = f"Join on Zoom: {ZOOM}\nMeeting ID: 845 7835 6424"
d = date(2026, 11, 2)
while d.year <= Y:
    if d in HOLIDAY_MONDAYS:
        add(f"swot-{d:%Y%m%d}", f"CANCELLED - SWOT (Holiday: {HOLIDAY_MONDAYS[d]})", d,
            hours=((19, 0), (20, 0)), free=True, desc="Cancelled because it falls on a holiday.")
    else:
        add(f"swot-{d:%Y%m%d}", "AB SWOT (Zoom)", d, hours=((19, 0), (20, 0)), desc=SWOT_DESC)
    d += timedelta(weeks=1)

# Weekly due reminders (all-day, don't block time), Nov 2026 through Dec 2027
DUE = [
    ("due-swot", "Due: Submit SWOT analysis", date(2026, 11, 9), "MO",
     "https://docs.google.com/forms/d/e/1FAIpQLSdJ9eZHkPlYYCrwxbDneoTRFnQQ-d3QDFd_PDVpZPSga5W6PQ/viewform"),
    ("due-assign", "Due: Accept your weekly AB assignment (by end of day)", date(2026, 11, 10), "TU",
     "https://2819church.churchcenter.com/me"),
    ("due-fk", "Due: Register kids for Formation Kids (by end of day)", date(2026, 11, 11), "WE",
     "https://2819church.churchcenter.com/people/forms/982537"),
]
for uid, title, first, day, link in DUE:
    add(uid, title, first, rrule=f"FREQ=WEEKLY;BYDAY={day};UNTIL=20271231", url=link, desc=f"Do it here: {link}")

# Access: fourth Thursday, 7pm
for m in range(1, 13):
    d = nth_weekday(m, 3, 4)
    if m in ACCESS_WEDNESDAY:
        d -= timedelta(days=1)
    if m in CANCELLED_ACCESS:
        add(f"access-{d:%Y%m%d}", f"CANCELLED - Access (Holiday: {CANCELLED_ACCESS[m]})", d,
            hours=((19, 0), (20, 0)), free=True, desc="Cancelled because it falls on a holiday.")
    else:
        add(f"access-{d:%Y%m%d}", "Access", d, hours=((19, 0), (20, 0)),
            desc="Virtual unless announced as in person.")

# 2026 extras: Access on the last Wednesday of Nov and Dec, and Christmas Sunday
for d in (date(2026, 11, 25), date(2026, 12, 30)):
    add(f"access-{d:%Y%m%d}", "Access", d, hours=((19, 0), (20, 0)),
        desc="Wednesday this month. Virtual unless announced as in person.")
add("key-20261227", "Christmas Sunday (All Hands)", date(2026, 12, 27))

# Quarterly outings (tentative)
for d, q in OUTINGS:
    add(f"outing-{d:%Y%m%d}", f"AB {q} Outing (Tentative)", d, tentative=True)

cal = "\r\n".join([
    "BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Armor Bearers//AB Calendar//EN",
    "CALSCALE:GREGORIAN", "METHOD:PUBLISH", "X-WR-CALNAME:AB Calendar", f"X-WR-TIMEZONE:{TZ}",
    "REFRESH-INTERVAL;VALUE=DURATION:PT12H", "X-PUBLISHED-TTL:PT12H", VTIMEZONE,
    *events, "END:VCALENDAR", "",
])
with open(OUT, "w", newline="") as f:
    f.write(cal)
print(f"Wrote {OUT} with {len(events)} events")
