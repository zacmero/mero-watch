#!/usr/bin/env python3
"""Read local Codex lifecycle events and optionally send short watch updates.

No prompts, output text, tool arguments or session titles are transmitted.
Local rollout formats are observed implementation details, not a stable API.
"""
import argparse
import asyncio
from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
import sys
import time

STATES = {"task_started": "working", "task_complete": "done", "turn_aborted": "aborted"}


class RolloutStatus:
    def __init__(self, path):
        self.path = Path(path)
        self.offset = 0
        self.state = "unknown"
        self.last_event = None

    def read(self):
        if self.path.stat().st_size < self.offset:
            self.offset = 0
            self.state = "unknown"
            self.last_event = None
        with self.path.open("rb") as stream:
            stream.seek(self.offset)
            while True:
                start = stream.tell()
                line = stream.readline()
                if not line or not line.endswith(b"\n"):
                    self.offset = start
                    break
                self.offset = stream.tell()
                try:
                    record = json.loads(line)
                except (ValueError, UnicodeDecodeError):
                    continue
                if record.get("type") != "event_msg":
                    continue
                payload = record.get("payload", {})
                if not isinstance(payload, dict):
                    continue
                event_type = payload.get("type")
                if event_type in STATES:
                    self.state = STATES[event_type]
                stamp = record.get("timestamp")
                if isinstance(stamp, str):
                    try:
                        parsed = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
                        if parsed.tzinfo is not None:
                            self.last_event = parsed
                    except ValueError:
                        pass
        state = self.state
        if state == "working" and (self.last_event is None or (
                datetime.now(timezone.utc) - self.last_event).total_seconds() > 120):
            state = "stale"
        return state


def sessions(database):
    with sqlite3.connect(database.resolve().as_uri() + "?mode=ro", uri=True) as connection:
        return connection.execute(
            "SELECT id, rollout_path, cwd FROM threads WHERE archived=0 "
            "ORDER BY updated_at_ms DESC LIMIT 50").fetchall()


def content(label, state):
    text = f"Codex | {label} | {state}"
    if len(text.encode("utf-8")) > 160:
        raise ValueError("Choose a shorter --label (message limit 160 UTF-8 bytes)")
    return text


async def run(args):
    rows = sessions(args.database)
    if args.list:
        for thread, path, cwd in rows:
            if Path(path).is_file():
                print(json.dumps({"thread": thread, "project": Path(cwd).name,
                                  "reported_state": RolloutStatus(path).read()}))
        return
    row = next((r for r in rows if r[0] == args.thread), None)
    if row is None:
        raise ValueError("Thread not found among recent local sessions; use --list")
    reader = RolloutStatus(row[1])
    label = args.label or Path(row[2]).name
    last_sent = None
    deadline = time.monotonic() + args.duration

    async def poll(sender=None):
        nonlocal last_sent
        while True:
            state = reader.read()
            if state != last_sent:
                text = content(label, state)
                result = {"label": label, "reported_state": state, "text": text}
                if sender:
                    result["delivery"] = await sender.send("Mero Codex", text)
                else:
                    result["delivery"] = "dry_run"
                print(json.dumps(result), flush=True)
                last_sent = state
            if not args.follow or time.monotonic() >= deadline:
                return
            await asyncio.sleep(min(args.interval, max(0, deadline - time.monotonic())))

    if args.send:
        from watch_notifications import WatchNotifications
        async with WatchNotifications(args.address, args.auth_helper) as sender:
            await poll(sender)
    else:
        await poll()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, default=Path.home() / ".codex/state_5.sqlite")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--list", action="store_true")
    group.add_argument("--thread")
    parser.add_argument("--label", help="Short explicit watch label; otherwise project directory name")
    parser.add_argument("--send", action="store_true", help="Send; default is dry run")
    parser.add_argument("--address")
    parser.add_argument("--auth-helper", type=Path, help="Inspected local AuthSession helper; never commit keys")
    parser.add_argument("--follow", action="store_true")
    parser.add_argument("--duration", type=float, default=120, help="Bounded follow duration in seconds")
    parser.add_argument("--interval", type=float, default=5)
    args = parser.parse_args()
    if args.send and (not args.address or not args.auth_helper):
        parser.error("--send requires --address and --auth-helper")
    if args.duration <= 0 or args.interval < 1:
        parser.error("duration must be positive and interval at least one second")
    try:
        asyncio.run(run(args))
    except KeyboardInterrupt:
        return 130
    except Exception as error:
        # Auth helper errors may embed key/challenge bytes: never echo exception text.
        print(f"Bridge failed: {type(error).__name__}; check session and LE connection", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
