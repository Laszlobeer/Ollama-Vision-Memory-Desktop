# 🤖 Ollama Vision Memory Desktop

> **Local AI Assistant with Persistent Memory, Computer Vision & Customizable Prompts**

![logo](logo.png)


[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![PyQt5](https://img.shields.io/badge/PyQt-5.15+-green.svg)](https://www.riverbankcomputing.com/software/pyqt/)
[![Ollama](https://img.shields.io/badge/Ollama-Compatible-orange.svg)](https://ollama.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A powerful **offline-first desktop application** that transforms your local Ollama models into an intelligent assistant with **long-term memory**, **real-time vision capabilities**, and **fully customizable behavior**. Built with PyQt5 for a smooth, native GUI experience.

---

## ✨ Features

### 🧠 Intelligent Chat
- **Local AI Backend**: Connects to your self-hosted Ollama instance (`localhost:11434`)
- **Multi-Model Support**: Switch between vision and text models on the fly
- **Session Instructions**: Add temporary context to guide individual conversations

### 👁️ Computer Vision
- **Live Camera Feed**: Real-time webcam display within the application
- **Image Analysis**: Send frames to vision-capable models (LLaVA, BakLLaVA, etc.)
- **Auto-Scan Mode**: Configurable interval for automatic environment analysis
- **Manual Analysis**: One-click image description on demand

### 📚 Mind Archive (Persistent Memory)
- **Automatic Indexing**: All chats, vision logs, and documents are saved locally
- **PDF Knowledge Extraction**: Upload PDFs; text is extracted and indexed for semantic search
- **Contextual Retrieval**: AI automatically searches your archive for relevant past information
- **Multi-Format Support**: Stores images, audio, text, chat logs, and vision descriptions

### ⚙️ System Prompt Editor
- **Dedicated Editor Window**: Full-featured UI for crafting your AI's personality
- **Preset Templates**: Quick-load personas (Research Assistant, Creative Companion, Technical Expert, etc.)
- **Persistent Storage**: Prompts saved to `mind_archive/prompts/system_prompt.txt`
- **Live Preview**: See your current prompt in the main UI

### 🎨 User Experience
- **Dark Mode UI**: Modern, eye-friendly interface with custom Qt stylesheet
- **Archive Browser**: Visual file explorer for managing stored knowledge
- **Hardware Detection**: Auto-scans for available Ollama models and webcams
- **Debug Panel**: Real-time logging for troubleshooting

---



---

## 📋 Requirements

### Software
- **Python 3.8+**
- **Ollama** installed and running (`ollama serve`)
- **Git** (for cloning)

### Python Dependencies
```bash
PyQt5>=5.15
opencv-python>=4.5
requests>=2.28
numpy>=1.21
pdfplumber>=0.7  # Optional: for PDF text extraction
# whisper  # Optional: for audio transcription (uncomment if needed)
```

### Recommended Ollama Models
```bash
# Text/Chat Models
ollama pull llama3.2
ollama pull mistral
ollama pull gemma2

# Vision Models
ollama pull llava
ollama pull bakllava
ollama pull llava-llama3
```

---

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/Laszlobeer/Ollama-Vision-Memory-Desktop.git
cd Ollama-Vision-Memory-Desktop
```

### 2. Create Virtual Environment (Recommended)
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
# Or manually:
pip install PyQt5 opencv-python requests numpy pdfplumber
```

### 4. Start Ollama
Ensure Ollama is running in the background:
```bash
ollama serve
```

### 5. Launch the Application
```bash
python deepseek_python_20260226_fdd99b.py
# Or rename to main.py and run:
python main.py
```

---

## 🎮 Usage Guide

### First Launch
1. The app will auto-scan for available **Ollama models** and **webcams**
2. Select your preferred **Vision Model** and **Brain Model** from the dropdowns
3. Choose your camera source if vision is needed

### Basic Chat
1. Type your message in the input box at the bottom-right
2. Add optional **Session Instructions** for context
3. Click **SEND** or press `Ctrl+Enter`

### Enable Vision
1. Toggle the **👁️ Vision: OFF** button to enable
2. Set **Auto-scan interval** (1-60 seconds)
3. Watch the AI describe your environment in real-time
4. Click **📸 Analyze Now** for instant manual analysis

### Manage Your Memory
- **📁 Archive Button**: Browse, search, and add PDFs to your knowledge base
- All interactions are automatically saved to `./mind_archive/`
- The AI will reference relevant past information when answering questions

### Customize Your AI
1. Click **⚙️ System Prompt** to open the editor
2. Choose a preset or write your own instructions
3. Click **💾 Save Prompt** to apply changes globally
4. Changes take effect immediately for new messages

---

## 📁 Project Structure

```
Ollama-Vision-Memory-Desktop/
├── main.py  # Main application file
├── requirements.txt                      # Python dependencies
├── README.md                            # This file
├── LICENSE                              # MIT License
│
└── mind_archive/                        # Auto-generated data directory
    ├── chat/           # Daily JSON chat logs
    ├── pdf/            # Stored PDF documents
    ├── images/         # Captured frames + metadata
    ├── audio/          # Audio recordings (optional)
    ├── text/           # Extracted text from PDFs/audio
    ├── vision/         # Vision analysis logs
    ├── index/          # Master search index (JSON)
    └── prompts/        # System prompt storage
        └── system_prompt.txt
```

---

## ⚙️ Configuration

### Environment Variables (Optional)
```bash
# Override default Ollama URL
export OLLAMA_URL="http://192.168.1.100:11434"

# Customize archive location
export ARCHIVE_DIR="/path/to/custom/archive"
```

### Key Settings in Code
| Setting | Default | Description |
|---------|---------|-------------|
| `OLLAMA_URL` | `http://localhost:11434` | Ollama API endpoint |
| `ARCHIVE_DIR` | `./mind_archive` | Local storage path |
| `DEFAULT_SYSTEM_PROMPT` | *(see code)* | Base AI personality |
| `auto_scan_interval` | `5` seconds | Vision auto-analysis frequency |

---

## 🔧 Troubleshooting

### ❌ "Ollama Offline" Error
```bash
# Verify Ollama is running:
ollama list

# Check firewall/port access:
curl http://localhost:11434/api/tags
```

### ❌ Camera Not Detected
```bash
# Test camera with OpenCV:
python -c "import cv2; cap = cv2.VideoCapture(0); print(cap.isOpened())"

# Linux: Ensure user has camera permissions
# macOS: Grant camera access in System Settings > Privacy
```

### ❌ PDF Extraction Fails
```bash
# Install optional dependency:
pip install pdfplumber

# Verify PDF is not password-protected or scanned-image-only
```

### ❌ High Memory Usage
- Reduce `auto_scan_interval` or disable vision when not needed
- Close unused applications; local LLMs are resource-intensive
- Consider using smaller models (e.g., `llama3.2:1b` vs `llama3.2:7b`)

---



## 📄 License

Distributed under the **MIT License**. See `LICENSE` for more information.

```
MIT License

Copyright (c) 2026 Laszlobeer

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

---

## 🙏 Acknowledgments

- [Ollama](https://ollama.com/) – For making local LLMs accessible
- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) – For the robust GUI framework
- [OpenCV](https://opencv.org/) – For computer vision capabilities
- The open-source community for models like LLaVA, Llama, and Mistral

---

> **💡 Pro Tip**: This app is designed for **privacy-first** use. All data stays on your machine—no cloud APIs, no telemetry, no surprises.

**🔗 GitHub**: [Laszlobeer/Ollama-Vision-Memory-Desktop](https://github.com/Laszlobeer/Ollama-Vision-Memory-Desktop)
