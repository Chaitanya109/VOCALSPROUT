# VOCALSPROUT

VOCALSPROUT (version 3.1.1, formerly AYLO) is a Windows-first, local voice productivity assistant. It provides offline speech-to-text, global dictation hotkeys, optional AI rewriting and commands, realtime OpenAI voice conversations, add direct screenshots, and an optional Gmail assistant.

Website source: [VOCALSPROUT landing page](marketing/index.html)

> **Migration notice:** VOCALSPROUT was previously named AYLO (and, before that, VoiceFlow). On first launch it copies settings, history, Gmail OAuth configuration, the local Gmail index, custom plugins, and saved API credentials from the former `%APPDATA%\Aylo` folder and `Aylo/...` Credential Manager entries (falling back to the original VoiceFlow names) without deleting the original data. The old Windows startup entry named `Aylo` is removed when you toggle "Start VOCALSPROUT with Windows". This project is not affiliated with Voiceflow, Inc.

## Status

The project is usable but still being prepared for a wider public release. APIs and user-facing behavior may change. Google Gemini Live support is planned; it is not implemented yet.

## Features

- Offline transcription with `faster-whisper`
- Hold-to-dictate and AI-command global hotkeys
- Optional Groq-powered cleanup, commands, and text chat
- OpenAI Realtime speech-to-speech conversations with interruption support
- Optional Gmail search, drafting, and sending
- Windows Credential Manager storage for API keys and OAuth tokens
- Portable Windows executable and installer build scripts

## What's new in 3.1

Maintenance update 3.1.1 keeps the orb window fixed at 148×168 while making the visible circle and ring slightly more compact on high-DPI displays.

- Mouse side-button push-to-talk: hold Back to dictate or Forward to run an AI command, then release to process.
- Screenshot markup with crop, arrows, rectangles, ellipses, red/blue highlights, text notes, and clipboard copy.
- Larger, clearer screenshot and Ask AI interfaces with one-click reply copying.
- Animated speaking/thinking orb states without changing the orb's compact size.
- More reliable microphone recovery and short-phrase capture.
- Cleaner Groq chat and screenshot answers with hidden model reasoning.

## Requirements

- Windows 10 or 11, 64-bit
- Python 3.11 or 3.12, 64-bit
- A working microphone
- Optional provider API keys for cloud AI features

The source code is free and open source. Cloud providers may charge for API usage. A ChatGPT or Gemini consumer subscription does not necessarily include API credits.

## Run from source

```powershell
git clone https://github.com/naveen2728/aylo.git vocalsprout
cd vocalsprout
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python main.py
```

The first run downloads the Whisper `base.en` model unless a bundled model is present. API keys entered through the application are stored in Windows Credential Manager, not in the repository.

To start VOCALSPROUT from a built executable instead, run `dist\VOCALSPROUT.exe` (or install `release\VOCALSPROUT-3.1.1-Setup.exe`).

## Upgrading from AYLO

- Settings, history, Gmail configuration, the Gmail index, custom plugins and API keys are carried over automatically on first launch. Nothing in `%APPDATA%\Aylo` is deleted, so you can roll back.
- Generated screenshots, generated images and a cached development-mode speech model stay in the old `%APPDATA%\Aylo` folder; copy them across manually if you want them.
- The old environment variables `AYLO_CHECKOUT_URL`, `AYLO_MARKETING_URL`, `AYLO_ISCC`, `AYLO_SIGNTOOL` and `AYLO_CERT_SHA1` still work; the new names start with `VOCALSPROUT_`.
- Running the new installer on a machine with AYLO installed upgrades it in place and removes the old `Aylo.exe` and shortcuts. If you use portable builds, delete the old `Aylo.exe` yourself and do not run both at once (they share the same hotkeys).

## Main controls

- Hold `Right Shift` to dictate; release to paste.
- Hold `Ctrl+Space` to record an AI command; release to run it.
- Optional mouse workflow: map one mouse button to dictation and another to AI commands.
- Press `Backspace` while recording to cancel.
- Press `Escape` twice quickly to quit.
- Right-click the floating orb for settings, diagnostics, AI keys, Gmail actions, and realtime voice chat.

## Tests

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## Build a Windows executable

```powershell
.\.venv\Scripts\Activate.ps1
python build.py
```

The build downloads the speech model and creates `dist\VOCALSPROUT.exe`. Generated models, executables, installers, and local output are intentionally excluded from Git. See [README_BUILD.md](README_BUILD.md) for packaging details.

## Privacy

Basic transcription runs locally. Features backed by Groq, OpenAI, Pollinations, or Google send the content needed for that feature to the selected provider. Gmail sync stores a local searchable index under `%APPDATA%\VOCALSPROUT`. Review [PRIVACY.md](PRIVACY.md) before enabling cloud or Gmail features.

## Contributing

Contributions are welcome. Read [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md), and the [Code of Conduct](CODE_OF_CONDUCT.md) before opening a contribution.

## License

The project source is licensed under the [Apache License 2.0](LICENSE). Third-party packages and downloaded model files remain under their respective licenses; see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
