from pathlib import Path

p = Path(r"c:\Users\anima\QuickDesk\QuickDesk\quickdesk-backend\app\services\ticketservice.py")
raw = p.read_bytes()
nl = "\r\n" if b"\r\n" in raw else "\n"
text = raw.decode("utf-8")
lines = text.split(nl)


def insert_before(idx: int, comment: str) -> None:
    lines.insert(idx, comment)


rollbacks = [i for i, line in enumerate(lines) if line == "        await db.rollback()"]
assert len(rollbacks) == 2, rollbacks
insert_before(rollbacks[1], "        # Drop the partial log and field writes if any step fails.")

lock_idxs = [i for i, line in enumerate(lines) if "with_for_update()" in line]
assert len(lock_idxs) == 1
insert_before(lock_idxs[0], "        # Lock the ticket so two agents cannot write it at once.")

upd = [i for i, line in enumerate(lines) if line.startswith("async def update_ticket_by_agent")]
assert len(upd) == 1
insert_before(
    upd[0] + 1,
    '    """Apply an agent\'s field changes and record each change in the agent log."""',
)

emps = [i for i, line in enumerate(lines) if line.strip() == "if user.role == UserRole.EMPLOYEE:"]
assert len(emps) == 2, emps
insert_before(emps[1], "    # Employees only see their own tickets; other roles see the full list.")

ga = [i for i, line in enumerate(lines) if line.startswith("async def get_all_tickets")]
assert len(ga) == 1
insert_before(
    ga[0] + 1,
    '    """Return one page of tickets, scoped to the caller when the caller is an employee."""',
)

emps = [i for i, line in enumerate(lines) if line.strip() == "if user.role == UserRole.EMPLOYEE:"]
insert_before(
    emps[0],
    "    # Employees may only read a ticket they opened; other roles may read any ticket.",
)

gid = [i for i, line in enumerate(lines) if line.startswith("async def get_ticket_by_id")]
assert len(gid) == 1
insert_before(
    gid[0] + 1,
    '    """Return one ticket, limited to the caller\'s own row when the caller is an employee."""',
)

flushes = [i for i, line in enumerate(lines) if line.strip() == "await db.flush()"]
assert len(flushes) == 2, flushes
insert_before(
    flushes[0],
    "        # Flush to assign an id before the response is built; the commit below persists the row.",
)

rollbacks = [i for i, line in enumerate(lines) if line == "        await db.rollback()"]
insert_before(rollbacks[0], "        # Drop the flushed insert if the response build or the commit fails.")

cr = [i for i, line in enumerate(lines) if line.startswith("async def create_ticket")]
assert len(cr) == 1
insert_before(cr[0] + 1, '    """Insert a ticket for the caller and commit it."""')

out = nl.join(lines)
if raw.endswith(b"\r\n") or raw.endswith(b"\n"):
    if not out.endswith(nl):
        out += nl
p.write_bytes(out.encode("utf-8"))
print("ok", len(lines))
