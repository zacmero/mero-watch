# Watch modification research — 2026-10-12

Objective: find evidence-backed ways to make the existing watch useful for Linux agent status and short commands; determine whether replacing features/native apps is feasible.

## Phases

1. Baseline and owner priorities — complete. Owner prioritizes agent status and short commands, and reports Siri interaction without a health app. Later disconnection is recorded separately from the earlier verified stability window.
2. Read-only host capability inventory — complete. AVRCP input/media interfaces observed; actual events and Linux voice capture remain experimental follow-up. Native tools are installed. Reconnect/key error and unavailable LE route recorded.
3. Primary-source protocol and firmware research — complete for this research pass. Official SDK/source comparisons support an RCSP-family hypothesis. Exact app binary, hardware and firmware target remain unknown and are explicit future identification tasks.
4. Modification options and next experiment — complete. Ranked host-control, voice, status display, vendor bridge, watch-face and native firmware paths documented in docs/modification-options.md.
5. Documentation verification — complete. Whitespace checks and local Markdown file-link checks passed; ignored research artifacts remain private.

## Constraints

Preserve the watch and historical records. Do not send undocumented GATT/serial commands, initiate DFU, reset bonds, open the case or program hardware. Raw captures remain ignored. Host applications are possible research outcomes; native execution is unverified.

## Errors

- Built-in web search failed to decode its response. Try the available alternative web connector; direct primary-source retrieval is a fallback.
- Alternative web connector returned search and official app-listing results.
- The initial input-node path disappeared before capability decoding. Resolve the AVRCP device dynamically rather than reuse event14.
- Both external repository searches failed with import error 504. Use targeted official documentation and GitHub tree/raw retrieval rather than retrying repository imports.
- Some official documentation URLs failed in the browser connector; direct HTTPS retrieval succeeded for the RCSP documentation. One append failed to match a long context line; corrected using a smaller known anchor.
- A second long-line patch anchor failed; subsequent edits use section-heading anchors.
- `evtest --help` returned exit 1 while printing its supported capture/query usage. Use documented `evtest DEVICE` syntax; do not use exclusive grab.
- Normal reconnect failed with br-connection-key-missing/remote termination. Owner reports no intervening phone reconnection or mode change. No pairing reset was attempted.
- Explicit CLI LE connection reported Bearer.LE1 unavailable. No permanent preference was changed; diagnostic client was closed.

## Follow-up implementation prerequisites

Restore and diagnose the normal connection without guessing protocol writes. Capture real watch-only control events, then build a small host bridge. Verify Linux microphone/playback before promising voice. Identify board/firmware/recovery before native feature removal. These are follow-up experiments, not completed capabilities.

## Follow-up: publish milestones, restore and test — complete

User authorized committing/pushing current milestones and restoring the computer connection, and requested online identification of the health app for installation on this computer. Milestone commit created as 04ac1be; pushed successfully. Standard watch-specific pairing repair is authorized as part of restoring the connection; no watch reset, firmware or speculative protocol write is authorized. Inspect native app/platform availability before proposing an installation.

Dual BLE/Classic connection restored; full GATT inventory, one AE02 notification and actual Linux play/pause events verified. Official mobile app candidates identified; exact compatibility and Linux health application remain unverified. Follow-up evidence recorded for publication.

## Firmware and custom watch information investigation — active

Owner prioritizes OS access and custom computer information over button mappings; confirms GFit Pro and supplies manual URL and firmware screenshots. Phases: inspect evidence; inspect official web/app assets and update mechanisms; locate and inspect matching firmware offline; assess native access and display channels; publish source-backed findings and unresolved prerequisites. No update or restoration command is authorized.

Research errors: official legacy website returned 404; two upstream repository import searches returned 504. Direct vendor JavaScript and GitHub API/raw source retrieval used instead.

Further research errors: Tencent GFit package page 404; APKCombo DNS failure; browser connector failed on APK mirrors and some official SDK pages. Direct HTTPS retrieved GFit Pro mirror and official GSFit APK for offline analysis. Metadata request preparation stopped before sending because the RSA key is stored as a field, not a method literal; inspect the correct field.

Research pass status: screenshot inspection, vendor/manual inspection, offline app analysis, source-backed display/native options and tool assessment complete. Exact device firmware retrieval remains unresolved: vendor response code 422; authenticated app response/cache needed. OS access and display test are still pending; no firmware or protocol-write experiment performed. Public report written; local Markdown links and whitespace checks passed. Publish this research milestone.

Final query correction: timestamp units were corrected to seconds; server still returned code 422. Preparation error and initial incomplete wrapper were not evidence of a missing firmware.

## Owner-authorized iPhone firmware capture — active

Prepare isolated temporary host proxy, limit TLS inspection to vendor domains, save only relevant firmware requests/responses in ignored private captures, verify connectivity, guide iPhone proxy/certificate setup, then observe normal app/version page without starting update/restoration. Disconnect capture and remove temporary phone proxy/certificate after test. Capture configuration and result pending.

Capture setup correction: local proxy verification did not establish phone reachability. Host firewalld port allowance was missing; added bounded runtime rule for capture port only. Retry phone onboarding, then verify inbound traffic before app test.

## 2026-10-12 capture follow-up — complete

- [x] Verify owner phone traffic and certificate trust, capture vendor firmware lookup.
- [x] Decode exact PID76/version1004/type0 restoration metadata.
- [x] Download matching vendor package to computer, verify vendor checksum, preserve original bytes.
- [x] Unpack application/boot components offline; inventory outer resources and record board-family evidence.
- [x] Stop capture listeners and remove temporary firewall rules; verify cleanup. Owner reports phone proxy off and certificate trust disabled.
- [x] Record public-safe findings; retain private capture setup by owner request.
- [ ] Correlate AC701/BR28/7012AF_J1 with SDK and CPU support, inspect resource format and text-display handler.
- [ ] Establish an explained synthetic status-display experiment; OS/shell/custom native apps and recovery remain research branches.

## 2026-10-13 offline build pass

- [x] Correlate BR28 SDK target and use vendor PI32v2/r3 decoder on unchanged application bytes.
- [x] Establish application mapping from package entry and string-reference evidence.
- [x] Compare kernel code against symbolized SDK; record strong uC/OS-II-derived inference and limits.
- [x] Decrypt resource image and check all 13 file chains; inventory 11 JLFS bundles and RU30 assets.
- [x] Trace app text serializer and native command0xA1 dispatcher without sending a watch command.
- [ ] Resolve RCSP framing/authentication and capability-dependent message path; prepare validated offline synthetic packet.
- [ ] Trace type2 receive/storage/rendering callback and decode RU30/style/preview assets.
- [ ] Establish a live synthetic computer-status display with an explained command; firmware flashing remains separately gated.


## 2026-10-13 command-test milestone

Completed: synthetic button mapping, live read-only identification, authenticated metadata query, owner-confirmed custom text delivery. Pending: popup policy, actual agent API integration, physical button dispatch check, firmware validation/recovery boundaries. No update transfer authorized or performed.


## Codex integration milestone

Completed: read-only local lifecycle source, source-derived text sender with private authentication, actual-session delivery acknowledgement, bounded change watcher, eight tests. Pending: owner confirmation of Mero Codex display, Herdr source from a managed pane, popup policy, narrowly scoped agent commands.


## Custom-screen branch

Owner confirmed Codex delivery but rejects Messages as the primary UI. Dual-link repair and post-repair message-only behavior verified. Informational query established reported 240x296 screen, W002 compatibility and 16 MiB external flash. Offline screen concept prepared. Next: stock RU30/resource round trip, compatible custom-face artifact for review, native UI entry/memory/display analysis. No resource or firmware transfer performed.


## RU30 milestone

Completed: decode stock single-image backgrounds, verify CRC16 and packed row fields, pixel-preserving round trip, execute native converter offline, generate native-compatible own-artwork candidate, 13 tests, serve phone PNG. Owner confirmed custom-photo upload capability. Pending: our actual screen appearance, direct Linux file transfer/activation with restoration plan, native live-render/menu integration.


Custom picture now owner-confirmed on watch, with vendor clock overlay and transient factory-image fallback. Background milestone achieved. Next: style/view format and native callbacks for replacing clock/menu layout.


## Native firmware / normal-update branch

Active priority: actual native agent app/UI, not background or stored notifications. Completed offline: dual-code-image byte-exact roundtrip, both-image mutation fixture and CRC checks, preserved loader/resources/config, negative CRC tests, seven verified updater decodes. Next: native updater acceptance/ROM call trace, app RAM/section mapping, meaningful renderer/input patch, exact-board recovery. No firmware transfer or image exploit performed.


### 2026-10-13 native architecture checkpoint

Completed offline runtime mapping, updater direct-call inventory and native style directory/relocation inspection. Current next step: explain 130 stock window-data CRC mismatches, then map real widgets/event handlers and prepare a verified offline native-layout fixture. Firmware installation remains dependent on boot validation and a demonstrated recovery path. See docs/native-architecture.md.

## 2026-10-14 — computer-only update verification
Entry from normal firmware: confirmed by host transfer and owner display. Active: complete stock resource pass, loader handoff, firmware pass, verify normal boot. Then native UI mods.

Fresh stock update: both Linux-initiated passes, loader relink, final success and reboot acknowledgement completed. Pending owner normal-boot confirmation. No new firmware modification was installed in this test.

Fresh computer-only stock update verification: COMPLETE. Owner confirmed normal boot. Next: traced, visibly testable native UI modification using the established Linux updater; arbitrary modifications and failed-boot recovery remain unproved.
