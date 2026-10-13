# Custom agent status on the watch

## Current route

Use a local custom Python bridge: Codex rollout lifecycle events → compact status text → authenticated AE01/AE02 RCSP → watch Messages. Firmware modification is unnecessary for this demonstrated text path.

`scripts/codex_watch.py` reads the local Codex state database in read-only mode and follows one explicitly selected rollout. It emits only an explicit label (or project directory name) and a lifecycle state. Prompts, session titles, tool arguments and agent responses are not transmitted. The bridge never sends terminal input or controls the agent.

The locally observed Codex event types map `task_started` to `working`, `task_complete` to `done`, and `turn_aborted` to `aborted`. A working session with no event for two minutes reports `stale`; that does not prove it stopped. Unknown formats remain `unknown`. This observed local format is not a stable public API, and session data alone does not prove process liveness or reliably distinguish approval waits.

Herdr is the preferred later source for richer lifecycle status (including blocked states) when the bridge runs in a Herdr-managed pane. This investigation session had no `HERDR_ENV`, so no Herdr session was inspected or controlled. No Herdr integration has been implemented yet.

## Run

Use the repository environment and ensure both watch Bluetooth bearers are connected. The media bearer alone does not expose the data GATT characteristics.

```bash
rtk proxy .venv/bin/python scripts/codex_watch.py --list
rtk proxy .venv/bin/python scripts/codex_watch.py --thread THREAD_ID --label Agent
rtk proxy .venv/bin/python scripts/codex_watch.py --thread THREAD_ID --label Agent \
  --send --address WATCH_ADDRESS --auth-helper /absolute/private/auth_helper.py \
  --follow --duration 3600
```

Without `--send`, the command is a dry run. Follow mode sends an initial snapshot, then only changed states; it is bounded by `--duration` (default 120 seconds). Errors stop the run without dumping authentication exception text. It does not automatically reconnect, retry delivery, install a service, or monitor multiple sessions.

Authentication is loaded from a separately inspected local Python helper exposing `AuthSession(transport, step_timeout=...)`. The transport provides `send_to_ae01(data)` and `recv_ae02_raw(timeout)`. The validated helper and its cryptographic material remain in ignored private captures. The public repository does not contain the keys; the helper is executable local code and must be the inspected copy. `requirements.txt` declares the direct `dbus-fast` dependency.

`scripts/watch_notifications.py` discovers characteristic paths dynamically, performs the observed SDK authentication flow and an informational metadata query, then sends the source-derived single-fragment legacy text format. The metadata reply can contain an authentication key and is discarded without logging. No raw Bluetooth traffic is recorded by the bridge. It supports only short text, checks byte limits, and correlates replies by opcode and command sequence. There is no arbitrary GATT-write interface or firmware/update command.

## 2026-10-13 validation

- **Observed:** Another local Codex rollout reported `working`, with recent event activity. The real bridge sent `Mero Codex` / `Codex | Agent run | working` and received RCSP transport status 0, application parameters `[2,1]`. Its bounded 60-second follow run completed without a second state change. Application parameter semantics remain unresolved; transport acknowledgement alone does not prove screen display.
- **Owner-reported, preceding notification test:** The earlier `Mero status` text caused vibration and appeared in Messages, with no popup. Visual confirmation of this new Codex-specific message is pending at this record's creation.
- **Observed:** Eight unit tests passed: four existing command-map tests, plus incremental/partial rollout handling, stale state, notification envelope/limits, and fragmented reply correlation. Dry-run output used the actual selected session. No actual agent completion or physical watch command occurred in this test.
- **Observed:** The Bluetooth service remained active with its original daemon command and no experimental runtime override before this integration.

Next: confirm the Codex message on the watch, connect a Herdr status source from an authorized managed pane, investigate popup policy offline, and map a deliberate watch button to a narrowly defined agent action. Remote terminal execution and modified firmware installation remain separate work.
