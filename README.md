# TranScriber
# 🎙️ Audio Recorder and Transcriber

This Python script records audio from a selected input device, saves it as a WAV file, and transcribes it using OpenAI's Whisper model. It supports listing and selecting audio input devices via the command line, with error handling and logging for debugging.

---

## 📑 Table of Contents
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
  - [Step 1: List Audio Devices](#step-1-list-audio-devices)
  - [Step 2: Modify the Script (Optional)](#step-2-modify-the-script-optional)
  - [Step 3: Run the Script](#step-3-run-the-script)
  - [Step 4: Select Input Device via Command Line (Optional)](#step-4-select-input-device-via-command-line-optional)
- [Example Output](#example-output)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Notes](#notes)
- [License](#license)

---

## 🚀 Features
- Lists available audio input devices.
- Records audio from a selected or default input device.
- Saves recordings as WAV files in a `data` directory.
- Transcribes audio using Whisper (`small` or `tiny` model).
- Saves transcriptions as text files.
- Option to keep or delete audio after transcription.
- Supports VB-Audio Virtual Cable for virtual input.
- Graceful handling of interruptions (e.g., `Ctrl+C`).

---

## 📦 Requirements

### Python Version
- Python 3.8 or higher

### Dependencies
- `pyaudio` – Audio recording
- `wave` – WAV handling (standard library)
- `whisper` – Audio transcription
- `pathlib`, `logging` – Standard library

---

## 🔧 Installation

### 1. Install Python
- Download Python 3.8+ from [python.org](https://www.python.org/downloads/).
- Ensure `pip` is installed and added to your system `PATH`.

### 2. Install Dependencies
```bash
pip install pyaudio
pip install git+https://github.com/openai/whisper.git
