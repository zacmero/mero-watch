# Possible mero-watch applications

Ideas recorded for exploration, not implemented capabilities.

## Audio notes and audio-to-text

**Owner request:** Explore on-device audio-to-text for recording notes from meetings and classes. Record speech, produce readable notes/transcripts, and make the results accessible on the watch and the owner's machines.

**Untested:** Access to the microphone from custom firmware, recording formats, available RAM/flash, usable audio drivers, battery cost, and transcription performance. Existing voice-assistant/media behavior does not prove that a custom app can capture audio or that speech recognition runs locally.

Investigate true local transcription first as requested, with measured resource requirements. Separately assess watch recording with computer/phone transcription and a watch-facing result as a fallback; these are different execution models. Do not represent offloaded transcription as on-device recognition. Include explicit recording state, start/stop controls, storage limits, and intentional export. No recording or audio experiment has been performed for this idea.

## Other candidates

- Native agent monitor: state, elapsed time, latest event, details and refresh.
- mero-shell: short commands, history and computer-backed responses.
- Agent/ntfy events: readable history and summaries, with transport and phone background behavior tested independently.
- System panel: firmware identity, connection state and basic configuration.

The immediate implementation remains the [approved native-panel mission](mission-2026-10-15.md). Audio research is a later branch and does not replace its success criteria.
