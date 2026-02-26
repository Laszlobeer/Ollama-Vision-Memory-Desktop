#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 LOCAL AI ASSISTANT - EXPANDED MIND ARCHIVE + SYSTEM PROMPT EDITOR
Features:
- PDF knowledge extraction and indexing
- Image storage with vision descriptions
- Audio file storage with transcription support (optional)
- System Prompt Editor Window (dedicated)
- Save/Load system prompts
- Multiple preset templates
"""

import sys
import os
import json
import time
import base64
import shutil
import hashlib
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QTextEdit, 
                             QComboBox, QMessageBox, QGroupBox, QStatusBar, 
                             QSplitter, QFrame, QProgressBar, QTabWidget, 
                             QSpinBox, QFileDialog, QTreeWidget, QTreeWidgetItem,
                             QDialog, QDialogButtonBox, QListWidget, QGridLayout)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QObject, QFileInfo
from PyQt5.QtGui import QPixmap, QImage, QFont, QIcon

import cv2
import numpy as np
import requests

# PDF Support (optional)
try:
    import pdfplumber
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

# ==============================================================================
# CONFIGURATION & PATHS
# ==============================================================================
BASE_DIR = Path(__file__).parent
ARCHIVE_DIR = BASE_DIR / "mind_archive"

ARCHIVE_SUBDIRS = {
    'chat': ARCHIVE_DIR / "chat",
    'pdf': ARCHIVE_DIR / "pdf",
    'images': ARCHIVE_DIR / "images",
    'audio': ARCHIVE_DIR / "audio",
    'text': ARCHIVE_DIR / "text",
    'vision': ARCHIVE_DIR / "vision",
    'index': ARCHIVE_DIR / "index",
    'prompts': ARCHIVE_DIR / "prompts"  # NEW: System prompts storage
}

OLLAMA_URL = "http://localhost:11434"

# System Prompt File
SYSTEM_PROMPT_FILE = ARCHIVE_SUBDIRS['prompts'] / "system_prompt.txt"

# Create all directories
for dir_path in ARCHIVE_SUBDIRS.values():
    dir_path.mkdir(parents=True, exist_ok=True)

# Default System Prompt
DEFAULT_SYSTEM_PROMPT = """You are a helpful, intelligent AI assistant with access to a comprehensive memory archive.

CAPABILITIES:
- You can see through a camera and analyze visual information
- You have access to stored knowledge from PDFs, documents, and past conversations
- You can remember and reference previous interactions
- You provide accurate, thoughtful, and helpful responses

BEHAVIOR:
- Be concise but thorough in your responses
- Reference your memory archive when relevant
- Acknowledge what you can see when vision is active
- Be honest about limitations
- Ask clarifying questions when needed

PERSONALITY:
- Friendly and approachable
- Professional but conversational
- Curious and engaged
- Respectful and considerate"""

# Preset System Prompts
PRESET_PROMPTS = {
    "🤖 Default Assistant": DEFAULT_SYSTEM_PROMPT,
    
    "🎓 Research Assistant": """You are an expert research assistant with access to academic knowledge.

CAPABILITIES:
- Analyze complex topics and explain them clearly
- Reference stored research papers and documents
- Provide citations and sources when possible
- Help with literature reviews and summaries

BEHAVIOR:
- Be precise and accurate
- Distinguish between facts and opinions
- Acknowledge uncertainty when present
- Provide balanced perspectives""",

    "💼 Professional Advisor": """You are a professional business advisor with extensive experience.

CAPABILITIES:
- Provide strategic business advice
- Analyze market trends and opportunities
- Help with decision-making processes
- Reference business documents and reports

BEHAVIOR:
- Be professional and direct
- Focus on actionable insights
- Consider risks and opportunities
- Maintain confidentiality""",

    "🎨 Creative Companion": """You are a creative AI companion for artistic endeavors.

CAPABILITIES:
- Generate creative ideas and concepts
- Provide feedback on creative work
- Help with brainstorming sessions
- Reference creative archives and inspiration

BEHAVIOR:
- Be imaginative and inspiring
- Encourage experimentation
- Provide constructive feedback
- Celebrate creativity""",

    "🔧 Technical Expert": """You are a technical expert specializing in software and systems.

CAPABILITIES:
- Debug and solve technical problems
- Explain complex technical concepts
- Provide code examples and solutions
- Reference technical documentation

BEHAVIOR:
- Be precise and detailed
- Provide step-by-step solutions
- Explain the 'why' behind solutions
- Consider security and best practices""",

    "🧘 Mindful Companion": """You are a mindful, supportive AI companion focused on wellbeing.

CAPABILITIES:
- Provide emotional support and encouragement
- Help with reflection and self-awareness
- Reference wellness resources and practices
- Maintain a calm, supportive presence

BEHAVIOR:
- Be empathetic and patient
- Listen actively and respond thoughtfully
- Encourage positive practices
- Respect boundaries""",

    "📚 Learning Tutor": """You are an expert tutor dedicated to helping students learn.

CAPABILITIES:
- Explain concepts at appropriate levels
- Provide practice problems and solutions
- Track learning progress
- Reference educational materials

BEHAVIOR:
- Be patient and encouraging
- Adapt to learning style
- Check understanding frequently
- Celebrate progress""",

    "🌍 Language Partner": """You are a multilingual language learning partner.

CAPABILITIES:
- Help practice conversation in multiple languages
- Correct grammar and pronunciation
- Provide cultural context
- Reference language learning materials

BEHAVIOR:
- Be encouraging and patient
- Provide corrections gently
- Mix languages appropriately
- Make learning fun"""
}

# ==============================================================================
# ENHANCED DARK STYLESHEET
# ==============================================================================
DARK_STYLE = """
QMainWindow { background-color: #1e1e1e; color: #e0e0e0; }
QWidget { background-color: #252526; color: #e0e0e0; font-family: 'Consolas', monospace; }
QGroupBox { border: 1px solid #3e3e42; border-radius: 5px; margin-top: 10px; font-weight: bold; padding-top: 10px; }
QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; color: #007acc; }
QComboBox, QLineEdit, QTextEdit, QSpinBox { background-color: #333333; border: 1px solid #3e3e42; border-radius: 4px; padding: 5px; color: #fff; }
QPushButton { background-color: #007acc; color: white; border: none; padding: 8px; border-radius: 4px; font-weight: bold; }
QPushButton:hover { background-color: #005f9e; }
QPushButton:pressed { background-color: #004d80; }
QPushButton:disabled { background-color: #3e3e42; color: #888; }
QPushButton:checked { background-color: #00aa00; }
QStatusBar { background-color: #007acc; color: white; }
QProgressBar { border: 1px solid #3e3e42; border-radius: 3px; text-align: center; color: white; }
QProgressBar::chunk { background-color: #007acc; }
QTabWidget::pane { border: 1px solid #3e3e42; }
QTabBar::tab { background: #333; padding: 8px 16px; }
QTabBar::tab:selected { background: #007acc; }
QTabBar::tab:hover { background: #444; }
QTreeWidget { background-color: #333333; border: 1px solid #3e3e42; }
QTreeWidget::item { padding: 4px; }
QTreeWidget::item:selected { background-color: #007acc; }
QTreeWidget::item:hover { background-color: #3e3e42; }
QListWidget { background-color: #333333; border: 1px solid #3e3e42; }
QListWidget::item:selected { background-color: #007acc; }
QListWidget::item:hover { background-color: #3e3e42; }
QDialog { background-color: #252526; }

QScrollBar:vertical { background: #2e2e2e; width: 12px; border-radius: 6px; }
QScrollBar::handle:vertical { background: #555; border-radius: 5px; min-height: 20px; }
QScrollBar::handle:vertical:hover { background: #777; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { border: none; background: none; }

QScrollBar:horizontal { background: #2e2e2e; height: 12px; border-radius: 6px; }
QScrollBar::handle:horizontal { background: #555; border-radius: 5px; min-width: 20px; }
QScrollBar::handle:horizontal:hover { background: #777; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { border: none; background: none; }

QMenu { background-color: #333; border: 1px solid #555; }
QMenu::item { padding: 5px 20px; color: #eee; }
QMenu::item:selected { background-color: #007acc; }
QMenu::item:disabled { color: #666; }

QToolTip { background-color: #333; color: #eee; border: 1px solid #555; }

QHeaderView::section { background-color: #3c3c3c; color: #eee; padding: 4px; border: 1px solid #555; }
"""

# ==============================================================================
# SYSTEM PROMPT MANAGER
# ==============================================================================

class SystemPromptManager:
    """Manages system prompt storage and loading."""
    
    def __init__(self):
        self.current_prompt = self.load_prompt()
    
    def load_prompt(self) -> str:
        """Load system prompt from file."""
        try:
            if SYSTEM_PROMPT_FILE.exists():
                with open(SYSTEM_PROMPT_FILE, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception as e:
            print(f"Prompt load error: {e}")
        return DEFAULT_SYSTEM_PROMPT
    
    def save_prompt(self, prompt: str) -> bool:
        """Save system prompt to file."""
        try:
            with open(SYSTEM_PROMPT_FILE, 'w', encoding='utf-8') as f:
                f.write(prompt)
            self.current_prompt = prompt
            return True
        except Exception as e:
            print(f"Prompt save error: {e}")
            return False
    
    def reset_to_default(self) -> str:
        """Reset to default prompt."""
        self.save_prompt(DEFAULT_SYSTEM_PROMPT)
        return DEFAULT_SYSTEM_PROMPT
    
    def get_current(self) -> str:
        """Get current system prompt."""
        return self.current_prompt
    
    def set_current(self, prompt: str):
        """Set current prompt (without saving)."""
        self.current_prompt = prompt

# Global prompt manager
prompt_manager = SystemPromptManager()

# ==============================================================================
# SYSTEM PROMPT EDITOR DIALOG
# ==============================================================================

class SystemPromptEditorDialog(QDialog):
    """Dedicated window for editing system prompt."""
    
    prompt_changed = pyqtSignal(str)  # Signal emitted when prompt is saved
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("⚙️ System Prompt Editor")
        self.setMinimumSize(900, 700)
        self.setStyleSheet(DARK_STYLE)
        
        self.init_ui()
        self.load_current_prompt()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("⚙️ SYSTEM PROMPT EDITOR")
        header.setStyleSheet("font-size: 16pt; font-weight: bold; color: #007acc;")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        info = QLabel("Define the AI's core personality, behavior, and capabilities. This prompt is sent with every request.")
        info.setStyleSheet("color: #888;")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Preset Selection
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel("📋 Load Preset:"))
        self.cb_presets = QComboBox()
        self.cb_presets.addItems(list(PRESET_PROMPTS.keys()))
        self.cb_presets.currentTextChanged.connect(self.load_preset)
        self.cb_presets.setMinimumWidth(250)
        preset_layout.addWidget(self.cb_presets)
        
        self.btn_load_preset = QPushButton("Load")
        self.btn_load_preset.clicked.connect(self.load_preset)
        preset_layout.addWidget(self.btn_load_preset)
        
        preset_layout.addStretch()
        layout.addLayout(preset_layout)
        
        # Prompt Editor
        layout.addWidget(QLabel("📝 System Prompt:"))
        self.txt_prompt = QTextEdit()
        self.txt_prompt.setPlaceholderText("Enter your custom system prompt here...")
        self.txt_prompt.setFont(QFont("Consolas", 10))
        layout.addWidget(self.txt_prompt)
        
        # Character count
        self.lbl_char_count = QLabel("Characters: 0")
        self.lbl_char_count.setStyleSheet("color: #888;")
        layout.addWidget(self.lbl_char_count)
        
        # Connect text change
        self.txt_prompt.textChanged.connect(self.update_char_count)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.btn_save = QPushButton("💾 Save Prompt")
        self.btn_save.clicked.connect(self.save_prompt)
        self.btn_save.setStyleSheet("background-color: #00aa00;")
        btn_layout.addWidget(self.btn_save)
        
        self.btn_reset = QPushButton("🔄 Reset to Default")
        self.btn_reset.clicked.connect(self.reset_prompt)
        btn_layout.addWidget(self.btn_reset)
        
        self.btn_copy = QPushButton("📋 Copy to Clipboard")
        self.btn_copy.clicked.connect(self.copy_to_clipboard)
        btn_layout.addWidget(self.btn_copy)
        
        btn_layout.addStretch()
        
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)
        
        layout.addLayout(btn_layout)
        
        # Initial char count
        self.update_char_count()

    def load_current_prompt(self):
        """Load current prompt into editor."""
        prompt = prompt_manager.get_current()
        self.txt_prompt.setPlainText(prompt)
        self.update_char_count()

    def load_preset(self):
        """Load selected preset."""
        preset_name = self.cb_presets.currentText()
        if preset_name in PRESET_PROMPTS:
            prompt = PRESET_PROMPTS[preset_name]
            self.txt_prompt.setPlainText(prompt)
            self.update_char_count()

    def save_prompt(self):
        """Save prompt to file."""
        prompt = self.txt_prompt.toPlainText()
        if not prompt.strip():
            QMessageBox.warning(self, "Empty Prompt", "System prompt cannot be empty!")
            return
        
        success = prompt_manager.save_prompt(prompt)
        if success:
            QMessageBox.information(self, "Saved", "✅ System prompt saved successfully!\n\nThe new prompt will be used for all future AI requests.")
            self.prompt_changed.emit(prompt)
            self.accept()
        else:
            QMessageBox.critical(self, "Save Error", "Failed to save system prompt.")

    def reset_prompt(self):
        """Reset to default prompt."""
        reply = QMessageBox.question(self, "Reset Prompt", 
                                     "Reset to default system prompt?\n\nThis will overwrite your current custom prompt.",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            prompt = prompt_manager.reset_to_default()
            self.txt_prompt.setPlainText(prompt)
            self.update_char_count()

    def copy_to_clipboard(self):
        """Copy prompt to clipboard."""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.txt_prompt.toPlainText())
        QMessageBox.information(self, "Copied", "✅ System prompt copied to clipboard!")

    def update_char_count(self):
        """Update character count display."""
        count = len(self.txt_prompt.toPlainText())
        self.lbl_char_count.setText(f"Characters: {count:,}")
        
        # Color based on length
        if count < 100:
            self.lbl_char_count.setStyleSheet("color: #ff5555;")
        elif count < 500:
            self.lbl_char_count.setStyleSheet("color: #ffaa00;")
        else:
            self.lbl_char_count.setStyleSheet("color: #00ff00;")

# ==============================================================================
# IMAGE UTILS
# ==============================================================================

def encode_frame_to_base64(frame: np.ndarray, quality: int = 80) -> Optional[str]:
    try:
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        success, buffer = cv2.imencode('.jpg', rgb_frame, [cv2.IMWRITE_JPEG_QUALITY, quality])
        if not success:
            return None
        return base64.b64encode(buffer).decode('utf-8')
    except Exception as e:
        print(f"Encoding error: {e}")
        return None

def save_image_to_archive(image_base64: str, description: str = "") -> Optional[Path]:
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        img_hash = hashlib.md5(image_base64.encode()).hexdigest()[:8]
        filename = f"img_{timestamp}_{img_hash}.jpg"
        filepath = ARCHIVE_SUBDIRS['images'] / filename
        
        img_data = base64.b64decode(image_base64)
        with open(filepath, 'wb') as f:
            f.write(img_data)
        
        meta = {
            'filename': filename,
            'timestamp': timestamp,
            'description': description,
            'hash': img_hash,
            'path': str(filepath)
        }
        meta_path = ARCHIVE_SUBDIRS['images'] / f"{filename}.meta.json"
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(meta, f, indent=2)
        
        index_entry = {
            'type': 'image',
            'path': str(filepath),
            'description': description,
            'timestamp': timestamp,
            'keywords': description.lower().split()
        }
        append_to_index(index_entry)
        
        return filepath
    except Exception as e:
        print(f"Image save error: {e}")
        return None

# ==============================================================================
# PDF PROCESSING
# ==============================================================================

def extract_pdf_text(pdf_path: Path) -> str:
    if not PDF_SUPPORT:
        return "PDF support not available. Install: pip install pdfplumber"
    
    try:
        text_content = []
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text:
                    text_content.append(f"[Page {i+1}]\n{text}")
        return "\n\n".join(text_content)
    except Exception as e:
        return f"Error extracting PDF: {str(e)}"

def process_pdf_to_archive(pdf_path: Path) -> Dict:
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"pdf_{timestamp}_{pdf_path.stem}.pdf"
        archive_path = ARCHIVE_SUBDIRS['pdf'] / filename
        shutil.copy2(pdf_path, archive_path)
        
        text_content = extract_pdf_text(archive_path)
        
        text_path = ARCHIVE_SUBDIRS['text'] / f"{filename}.txt"
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write(f"Source: {filename}\n")
            f.write(f"Extracted: {datetime.now().isoformat()}\n\n")
            f.write(text_content)
        
        index_entry = {
            'type': 'pdf',
            'path': str(archive_path),
            'text_path': str(text_path),
            'filename': filename,
            'timestamp': timestamp,
            'content_preview': text_content[:500],
            'keywords': text_content.lower().split()[:100]
        }
        append_to_index(index_entry)
        
        return {
            'success': True,
            'path': str(archive_path),
            'text_length': len(text_content),
            'message': f"PDF processed: {len(text_content)} chars extracted"
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

# ==============================================================================
# AUDIO PROCESSING (OPTIONAL - KEPT FOR ARCHIVE BUT TTS/STT REMOVED)
# ==============================================================================

def save_audio_to_archive(audio_data: bytes, filename: str = "") -> Optional[Path]:
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if not filename:
            filename = f"audio_{timestamp}.wav"
        else:
            filename = f"audio_{timestamp}_{filename}"
        
        filepath = ARCHIVE_SUBDIRS['audio'] / filename
        with open(filepath, 'wb') as f:
            f.write(audio_data)
        
        index_entry = {
            'type': 'audio',
            'path': str(filepath),
            'filename': filename,
            'timestamp': timestamp,
            'transcription': '',
            'keywords': []
        }
        append_to_index(index_entry)
        
        return filepath
    except Exception as e:
        print(f"Audio save error: {e}")
        return None

def transcribe_audio(audio_path: Path, whisper_model: str = "base") -> str:
    try:
        import whisper
        model = whisper.load_model(whisper_model)
        result = model.transcribe(str(audio_path))
        transcription = result['text']
        
        update_audio_index(audio_path, transcription)
        
        text_path = ARCHIVE_SUBDIRS['text'] / f"{audio_path.stem}.txt"
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write(f"Audio: {audio_path.name}\n")
            f.write(f"Transcribed: {datetime.now().isoformat()}\n\n")
            f.write(transcription)
        
        return transcription
    except Exception as e:
        return f"Transcription error: {str(e)}"

def update_audio_index(audio_path: Path, transcription: str):
    index_file = ARCHIVE_SUBDIRS['index'] / "audio_index.json"
    index_data = []
    
    if index_file.exists():
        try:
            with open(index_file, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
        except:
            index_data = []
    
    for entry in index_data:
        if entry.get('path') == str(audio_path):
            entry['transcription'] = transcription
            entry['keywords'] = transcription.lower().split()
            break
    
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, indent=2)

# ==============================================================================
# MEMORY ARCHIVE SYSTEM
# ==============================================================================

class MemoryArchive:
    def __init__(self):
        self.dir = ARCHIVE_DIR
        self.latest_vision = ""
        self.index_cache = []
        self._load_index()
    
    def _load_index(self):
        index_file = ARCHIVE_SUBDIRS['index'] / "master_index.json"
        try:
            if index_file.exists():
                with open(index_file, 'r', encoding='utf-8') as f:
                    self.index_cache = json.load(f)
        except Exception as e:
            print(f"Index load error: {e}")
            self.index_cache = []
    
    def _save_index(self):
        index_file = ARCHIVE_SUBDIRS['index'] / "master_index.json"
        try:
            with open(index_file, 'w', encoding='utf-8') as f:
                json.dump(self.index_cache, f, indent=2)
        except Exception as e:
            print(f"Index save error: {e}")
    
    def save_thought(self, role: str, text: str):
        ts = datetime.now().isoformat()
        
        chat_file = ARCHIVE_SUBDIRS['chat'] / f"chat_{datetime.now().strftime('%Y%m%d')}.json"
        log_entry = {"timestamp": ts, "role": role, "content": text}
        try:
            with open(chat_file, "a", encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            print(f"Chat save error: {e}")
        
        kb_file = ARCHIVE_SUBDIRS['text'] / "knowledge_base.txt"
        try:
            with open(kb_file, "a", encoding='utf-8') as f:
                f.write(f"[{ts}] {role}: {text}\n")
        except Exception as e:
            print(f"KB save error: {e}")
        
        index_entry = {
            'type': 'chat',
            'role': role,
            'content': text,
            'timestamp': ts,
            'keywords': text.lower().split()
        }
        append_to_index(index_entry)

    def set_latest_vision(self, description: str):
        self.latest_vision = description
        ts = datetime.now().isoformat()
        
        vision_file = ARCHIVE_SUBDIRS['vision'] / f"vision_{datetime.now().strftime('%Y%m%d')}.json"
        vision_entry = {"timestamp": ts, "description": description}
        try:
            with open(vision_file, "a", encoding='utf-8') as f:
                f.write(json.dumps(vision_entry) + "\n")
        except Exception as e:
            print(f"Vision save error: {e}")
        
        index_entry = {
            'type': 'vision',
            'description': description,
            'timestamp': ts,
            'keywords': description.lower().split()
        }
        append_to_index(index_entry)

    def get_latest_vision(self) -> str:
        return self.latest_vision

    def search_memory(self, query: str, limit: int = 10) -> str:
        if not query.strip():
            return ""
        
        results = []
        query_words = query.lower().split()
        query_words = [w for w in query_words if len(w) > 2]
        
        for entry in self.index_cache:
            score = 0
            keywords = entry.get('keywords', [])
            
            for word in query_words:
                if word in keywords:
                    score += 1
                elif any(word in kw for kw in keywords):
                    score += 0.5
            
            if score > 0:
                results.append((score, entry))
        
        results.sort(key=lambda x: x[0], reverse=True)
        
        formatted = []
        for score, entry in results[:limit]:
            entry_type = entry.get('type', 'unknown')
            timestamp = entry.get('timestamp', '')
            
            if entry_type == 'chat':
                content = entry.get('content', '')[:200]
                formatted.append(f"[{entry_type}] {timestamp[:16]}: {content}...")
            elif entry_type == 'vision':
                content = entry.get('description', '')[:200]
                formatted.append(f"[👁️ Vision] {timestamp[:16]}: {content}...")
            elif entry_type == 'pdf':
                content = entry.get('content_preview', '')[:200]
                formatted.append(f"[📄 PDF] {entry.get('filename', '')}: {content}...")
            elif entry_type == 'audio':
                content = entry.get('transcription', '')[:200]
                formatted.append(f"[🎤 Audio] {entry.get('filename', '')}: {content}...")
            elif entry_type == 'image':
                content = entry.get('description', '')[:200]
                formatted.append(f"[🖼️ Image] {timestamp[:16]}: {content}...")
        
        if formatted:
            return "\n\n".join(formatted)
        else:
            return "No relevant memory found."

    def get_archive_stats(self) -> Dict:
        stats = {
            'chat_files': 0,
            'pdf_files': 0,
            'image_files': 0,
            'audio_files': 0,
            'text_files': 0,
            'vision_entries': 0,
            'total_index_entries': len(self.index_cache)
        }
        
        try:
            stats['chat_files'] = len(list(ARCHIVE_SUBDIRS['chat'].glob("*.json")))
            stats['pdf_files'] = len(list(ARCHIVE_SUBDIRS['pdf'].glob("*.pdf")))
            stats['image_files'] = len(list(ARCHIVE_SUBDIRS['images'].glob("*.jpg")))
            stats['audio_files'] = len(list(ARCHIVE_SUBDIRS['audio'].glob("*")))
            stats['text_files'] = len(list(ARCHIVE_SUBDIRS['text'].glob("*.txt")))
            
            vision_file = ARCHIVE_SUBDIRS['vision'] / f"vision_{datetime.now().strftime('%Y%m%d')}.json"
            if vision_file.exists():
                with open(vision_file, 'r') as f:
                    stats['vision_entries'] = sum(1 for _ in f)
        except Exception as e:
            print(f"Stats error: {e}")
        
        return stats

    def get_file_path(self) -> str:
        return str(ARCHIVE_DIR.resolve())

    def browse_archive(self) -> Dict[str, List[str]]:
        files = {
            'chat': [],
            'pdf': [],
            'images': [],
            'audio': [],
            'text': [],
            'vision': []
        }
        
        for key, dir_path in ARCHIVE_SUBDIRS.items():
            if key == 'index' or key == 'prompts':
                continue
            try:
                files[key] = [f.name for f in dir_path.iterdir() if f.is_file()]
            except:
                files[key] = []
        
        return files

# ==============================================================================
# INDEX MANAGEMENT
# ==============================================================================

def append_to_index(entry: Dict):
    index_file = ARCHIVE_SUBDIRS['index'] / "master_index.json"
    index_data = []
    
    if index_file.exists():
        try:
            with open(index_file, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
        except:
            index_data = []
    
    index_data.append(entry)
    
    if len(index_data) > 1000:
        index_data = index_data[-1000:]
    
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, indent=2)

# ==============================================================================
# HARDWARE SCANNER (NO TTS/STT)
# ==============================================================================

class HardwareScannerThread(QThread):
    scan_complete = pyqtSignal(dict)
    scan_progress = pyqtSignal(str)
    scan_error = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._abort = False

    def run(self):
        results = {
            'all_models': ['Scanning...'],
            'cameras': ['Scanning...']
        }

        try:
            self.scan_progress.emit("📡 Connecting to Ollama...")
            try:
                resp = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
                if resp.status_code == 200:
                    models = resp.json().get('models', [])
                    all_models = [m['name'] for m in models]
                    results['all_models'] = all_models if all_models else ['⚠️ No Models']
                    self.scan_progress.emit(f"✅ Found {len(all_models)} models")
                else:
                    results['all_models'] = ['❌ Ollama Offline']
            except Exception as e:
                results['all_models'] = ['❌ Ollama Offline']
                self.scan_progress.emit(f"⚠️ {str(e)}")

            self.scan_progress.emit("📷 Scanning cameras...")
            cams = []
            for i in range(5):
                if self._abort:
                    break
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    cams.append(f"📹 Camera {i}")
                    cap.release()
                time.sleep(0.1)
            results['cameras'] = cams if cams else ['⚠️ No Camera']

            self.scan_progress.emit("✅ Scan complete!")
            self.scan_complete.emit(results)
        except Exception as e:
            self.scan_error.emit(str(e))
            self.scan_complete.emit(results)

    def abort(self):
        self._abort = True

# ==============================================================================
# CAMERA WORKER
# ==============================================================================

class CameraWorker(QThread):
    frame_signal = pyqtSignal(QImage)
    status_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)

    def __init__(self, cam_index: int = 0):
        super().__init__()
        self.cam_index = cam_index
        self._abort = False
        self.cap: Optional[cv2.VideoCapture] = None

    def run(self):
        try:
            self.cap = cv2.VideoCapture(self.cam_index)
            if not self.cap.isOpened():
                self.error_signal.emit(f"Cannot open camera {self.cam_index}")
                return

            while not self._abort:
                ret, frame = self.cap.read()
                if ret:
                    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    h, w, ch = rgb.shape
                    qimg = QImage(rgb.data, w, h, w * ch, QImage.Format_RGB888)
                    self.frame_signal.emit(qimg)
                    self.status_signal.emit(f"👁️ Seeing: Camera {self.cam_index}")
                time.sleep(0.03)
        except Exception as e:
            self.error_signal.emit(str(e))
        finally:
            if self.cap:
                self.cap.release()

    def abort(self):
        self._abort = True
        if self.cap:
            self.cap.release()

# ==============================================================================
# VISION WORKER
# ==============================================================================

class VisionAnalysisWorker(QThread):
    analysis_complete = pyqtSignal(str)
    analysis_error = pyqtSignal(str)
    status_signal = pyqtSignal(str)
    debug_signal = pyqtSignal(str)

    def __init__(self, image_base64: str, vision_model: str, auto_scan: bool = False):
        super().__init__()
        self.image_base64 = image_base64
        self.vision_model = vision_model
        self.auto_scan = auto_scan
        self._abort = False

    def run(self):
        try:
            if self.auto_scan:
                self.status_signal.emit("👁️ Auto-scan: Analyzing...")
            else:
                self.status_signal.emit("👁️ Vision: Analyzing image...")
            
            self.debug_signal.emit(f"🔍 Image size: {len(self.image_base64)} chars")
            
            prompt = "Describe what you see in this image in detail. List objects, people, colors, text, actions, and setting."
            if self.auto_scan:
                prompt = "Briefly describe what you see. Focus on changes or notable elements. Keep it under 100 words."
            
            payload = {
                "model": self.vision_model,
                "prompt": prompt,
                "images": [self.image_base64],
                "stream": False,
                "options": {"temperature": 0.3}
            }
            
            self.debug_signal.emit(f"🔍 Model: {self.vision_model}")

            resp = requests.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=120)
            self.debug_signal.emit(f"🔍 Response: {resp.status_code}")
            
            if resp.status_code == 200:
                desc = resp.json().get('response', 'No description.')
                if self.auto_scan:
                    self.status_signal.emit("✅ Auto-scan complete")
                else:
                    self.status_signal.emit("✅ Vision: Analysis complete")
                self.analysis_complete.emit(desc)
            else:
                self.analysis_error.emit(f"Ollama {resp.status_code}: {resp.text[:200]}")
        except Exception as e:
            self.analysis_error.emit(f"Error: {str(e)}")
            self.debug_signal.emit(f"❌ Exception: {str(e)}")

    def abort(self):
        self._abort = True

# ==============================================================================
# BRAIN WORKER (WITH SYSTEM PROMPT)
# ==============================================================================

class BrainResponseWorker(QThread):
    response_complete = pyqtSignal(str)
    response_error = pyqtSignal(str)
    status_signal = pyqtSignal(str)

    def __init__(self, user_input: str, vision_desc: str, mind_model: str, 
                 memory_ctx: str, custom_thought: str, latest_vision: str = "",
                 system_prompt: str = ""):
        super().__init__()
        self.user_input = user_input
        self.vision_desc = vision_desc
        self.mind_model = mind_model
        self.memory_ctx = memory_ctx
        self.custom_thought = custom_thought
        self.latest_vision = latest_vision
        self.system_prompt = system_prompt
        self._abort = False

    def run(self):
        try:
            self.status_signal.emit("🧠 Brain: Processing...")
            
            # Use system prompt from manager
            sys_prompt = self.system_prompt if self.system_prompt else prompt_manager.get_current()
            
            prompt = f"""{sys_prompt}

📁 ARCHIVE MEMORY:
{self.memory_ctx}

👁️ LATEST VISION SCAN:
{self.latest_vision if self.latest_vision else "No current visual input."}

👁️ SPECIFIC IMAGE ANALYSIS:
{self.vision_desc if self.vision_desc else "No specific image analysis."}

🧠 CURRENT SESSION INSTRUCTIONS:
{self.custom_thought if self.custom_thought else "Respond helpfully using all available context."}

User: {self.user_input}"""

            payload = {
                "model": self.mind_model,
                "prompt": prompt,
                "stream": False
            }

            resp = requests.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=120)
            
            if resp.status_code == 200:
                response = resp.json().get('response', 'No response.')
                self.status_signal.emit("✅ Brain: Response ready")
                self.response_complete.emit(response)
            else:
                self.response_error.emit(f"Ollama {resp.status_code}")
        except Exception as e:
            self.response_error.emit(f"Error: {str(e)}")

    def abort(self):
        self._abort = True

# ==============================================================================
# ARCHIVE BROWSER DIALOG
# ==============================================================================

class ArchiveBrowserDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📁 Mind Archive Browser")
        self.setMinimumSize(800, 600)
        self.setStyleSheet(DARK_STYLE)
        
        layout = QVBoxLayout(self)
        
        self.lbl_stats = QLabel("Loading stats...")
        self.lbl_stats.setStyleSheet("color: #007acc; font-weight: bold;")
        layout.addWidget(self.lbl_stats)
        
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["📁 Archive Contents", "Type", "Size"])
        layout.addWidget(self.tree)
        
        btn_layout = QHBoxLayout()
        
        self.btn_add_pdf = QPushButton("📄 Add PDF")
        self.btn_add_pdf.clicked.connect(self.add_pdf)
        btn_layout.addWidget(self.btn_add_pdf)
        
        self.btn_refresh = QPushButton("🔄 Refresh")
        self.btn_refresh.clicked.connect(self.load_archive)
        btn_layout.addWidget(self.btn_refresh)
        
        self.btn_close = QPushButton("Close")
        self.btn_close.clicked.connect(self.accept)
        btn_layout.addWidget(self.btn_close)
        
        layout.addLayout(btn_layout)
        
        self.load_archive()

    def load_archive(self):
        self.tree.clear()
        
        memory = MemoryArchive()
        stats = memory.get_archive_stats()
        files = memory.browse_archive()
        
        self.lbl_stats.setText(
            f"📊 Archive: {stats['chat_files']} chats | "
            f"{stats['pdf_files']} PDFs | {stats['image_files']} images | "
            f"{stats['audio_files']} audio | {stats['text_files']} text | "
            f"{stats['total_index_entries']} indexed"
        )
        
        categories = {
            '💬 Chat': ('chat', files['chat']),
            '📄 PDFs': ('pdf', files['pdf']),
            '🖼️ Images': ('images', files['images']),
            '🎤 Audio': ('audio', files['audio']),
            '📝 Text': ('text', files['text']),
            '👁️ Vision': ('vision', files['vision'])
        }
        
        for cat_name, (key, file_list) in categories.items():
            cat_item = QTreeWidgetItem(self.tree)
            cat_item.setText(0, f"{cat_name} ({len(file_list)})")
            cat_item.setExpanded(True)
            
            for filename in file_list[:50]:
                file_item = QTreeWidgetItem(cat_item)
                file_item.setText(0, filename)
                
                if filename.endswith('.pdf'):
                    file_item.setText(1, "PDF")
                elif filename.endswith(('.jpg', '.png')):
                    file_item.setText(1, "Image")
                elif filename.endswith(('.wav', '.mp3')):
                    file_item.setText(1, "Audio")
                elif filename.endswith('.txt'):
                    file_item.setText(1, "Text")
                elif filename.endswith('.json'):
                    file_item.setText(1, "JSON")
                else:
                    file_item.setText(1, "Other")
                
                try:
                    file_path = ARCHIVE_SUBDIRS[key] / filename
                    size = file_path.stat().st_size
                    file_item.setText(2, f"{size/1024:.1f} KB")
                except:
                    file_item.setText(2, "N/A")

    def add_pdf(self):
        if not PDF_SUPPORT:
            QMessageBox.warning(self, "PDF Support Missing", 
                               "Install pdfplumber: pip install pdfplumber")
            return
        
        files, _ = QFileDialog.getOpenFileNames(self, "Select PDFs", "", "PDF Files (*.pdf)")
        if files:
            for pdf_path in files:
                result = process_pdf_to_archive(Path(pdf_path))
                if result['success']:
                    QMessageBox.information(self, "PDF Added", result['message'])
                else:
                    QMessageBox.warning(self, "PDF Error", result.get('error', 'Unknown error'))
            
            self.load_archive()

# ==============================================================================
# MAIN GUI (NO TTS/STT)
# ==============================================================================

class LocalAIAssistant(QMainWindow):
    def __init__(self):
        super().__init__()
        self.memory = MemoryArchive()
        self.camera_thread: Optional[CameraWorker] = None
        self.scanner_thread: Optional[HardwareScannerThread] = None
        self.vision_worker: Optional[VisionAnalysisWorker] = None
        self.brain_worker: Optional[BrainResponseWorker] = None
        self.current_frame_b64: Optional[str] = None
        self.vision_mode_enabled = False
        self.auto_scan_interval = 5
        self.vision_timer: Optional[QTimer] = None
        self.is_scanning = False
        self.is_brain_busy = False  # Flag to prevent multiple sends
        
        self.ui_update_queue = []
        
        self.init_ui()
        self.start_hardware_scan()

    def init_ui(self):
        self.setWindowTitle("🤖 LOCAL AI - Mind Archive + System Prompt")
        self.setStyleSheet(DARK_STYLE)
        self.setGeometry(100, 100, 1600, 1000)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        # Header
        header = QGroupBox("🤖 LOCAL AI ASSISTANT | Mind Archive + System Prompt Editor")
        main_layout.addWidget(header)

        # Progress
        self.scan_progress = QProgressBar()
        self.scan_progress.setRange(0, 0)
        self.scan_status = QLabel("🔄 Initializing...")
        progress_layout = QHBoxLayout()
        progress_layout.addWidget(self.scan_status)
        progress_layout.addWidget(self.scan_progress)
        main_layout.addLayout(progress_layout)

        # Config Bar
        config = QFrame()
        config_layout = QHBoxLayout()
        config.setLayout(config_layout)
        
        def combo(label: str, items: list, w=180):
            l = QLabel(label)
            c = QComboBox()
            c.addItems(items)
            c.setMinimumWidth(w)
            return l, c

        self.lbl_v, self.cb_vision = combo("👁️ Vision:", ["Wait..."])
        self.lbl_m, self.cb_mind = combo("🧠 Brain:", ["Wait..."])
        self.lbl_c, self.cb_cam = combo("📷 Camera:", ["Wait..."])

        for w in [self.lbl_v, self.cb_vision, self.lbl_m, self.cb_mind, 
                  self.lbl_c, self.cb_cam]:
            config_layout.addWidget(w)

        # Vision Toggle
        self.btn_vision = QPushButton("👁️ Vision: OFF")
        self.btn_vision.setCheckable(True)
        self.btn_vision.clicked.connect(self.toggle_vision)
        self.btn_vision.setEnabled(False)
        config_layout.addWidget(self.btn_vision)

        # Scan Interval
        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel("⏱️ Auto-scan:"))
        self.spin_interval = QSpinBox()
        self.spin_interval.setRange(1, 60)
        self.spin_interval.setValue(5)
        self.spin_interval.setSuffix("s")
        self.spin_interval.setMinimumWidth(60)
        self.spin_interval.valueChanged.connect(self.update_scan_interval)
        interval_layout.addWidget(self.spin_interval)
        config_layout.addLayout(interval_layout)

        # System Prompt Button
        self.btn_sysprompt = QPushButton("⚙️ System Prompt")
        self.btn_sysprompt.clicked.connect(self.open_system_prompt_editor)
        self.btn_sysprompt.setStyleSheet("background-color: #aa00aa;")
        config_layout.addWidget(self.btn_sysprompt)

        # Archive Browser
        self.btn_archive = QPushButton("📁 Archive")
        self.btn_archive.clicked.connect(self.open_archive_browser)
        config_layout.addWidget(self.btn_archive)

        # Refresh
        self.btn_refresh = QPushButton("🔄 Refresh")
        self.btn_refresh.clicked.connect(self.start_hardware_scan)
        config_layout.addWidget(self.btn_refresh)

        main_layout.addWidget(config)

        # Main Splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left: Vision + Archive Stats
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        self.lbl_feed = QLabel("Camera Feed")
        self.lbl_feed.setAlignment(Qt.AlignCenter)
        self.lbl_feed.setMinimumSize(320, 240)
        self.lbl_feed.setStyleSheet("background: #000; border: 1px solid #555;")
        left_layout.addWidget(self.lbl_feed)
        
        # Camera status and manual analyze button
        cam_status_layout = QHBoxLayout()
        self.lbl_seeing = QLabel("⏸️ Seeing: Waiting...")
        self.lbl_seeing.setStyleSheet("color: #ffaa00; font-weight: bold;")
        cam_status_layout.addWidget(self.lbl_seeing)
        
        self.btn_analyze = QPushButton("📸 Analyze Now")
        self.btn_analyze.clicked.connect(self.test_vision)
        self.btn_analyze.setEnabled(False)
        self.btn_analyze.setToolTip("Manually analyze the current camera frame")
        cam_status_layout.addWidget(self.btn_analyze)
        left_layout.addLayout(cam_status_layout)
        
        self.lbl_vstatus = QLabel("👁️ Vision: OFF")
        self.lbl_vstatus.setStyleSheet("color: #f55; font-weight: bold;")
        left_layout.addWidget(self.lbl_vstatus)
        
        self.lbl_timer = QLabel("⏱️ Next scan: --")
        self.lbl_timer.setStyleSheet("color: #888;")
        left_layout.addWidget(self.lbl_timer)
        
        left_layout.addWidget(QLabel("📝 Latest Vision:"))
        self.txt_vision = QTextEdit()
        self.txt_vision.setReadOnly(True)
        self.txt_vision.setMaximumHeight(80)
        left_layout.addWidget(self.txt_vision)
        
        # System Prompt Preview
        left_layout.addWidget(QLabel("⚙️ System Prompt:"))
        self.txt_sysprompt_preview = QTextEdit()
        self.txt_sysprompt_preview.setReadOnly(True)
        self.txt_sysprompt_preview.setMaximumHeight(60)
        self.txt_sysprompt_preview.setPlaceholderText("Click 'System Prompt' to edit...")
        left_layout.addWidget(self.txt_sysprompt_preview)
        
        # Archive Stats
        left_layout.addWidget(QLabel("📊 Archive Stats:"))
        self.txt_stats = QTextEdit()
        self.txt_stats.setReadOnly(True)
        self.txt_stats.setMaximumHeight(100)
        left_layout.addWidget(self.txt_stats)
        
        # Debug Tab
        tabs = QTabWidget()
        debug_tab = QWidget()
        debug_layout = QVBoxLayout(debug_tab)
        self.txt_debug = QTextEdit()
        self.txt_debug.setReadOnly(True)
        self.txt_debug.setStyleSheet("font-size: 10pt;")
        debug_layout.addWidget(self.txt_debug)
        tabs.addTab(debug_tab, "🔍 Debug")
        left_layout.addWidget(tabs)
        
        splitter.addWidget(left_panel)

        # Right: Chat
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        self.chat = QTextEdit()
        self.chat.setReadOnly(True)
        right_layout.addWidget(self.chat)
        
        self.thought_editor = QTextEdit()
        self.thought_editor.setPlaceholderText("Edit session instructions...")
        self.thought_editor.setMaximumHeight(60)
        right_layout.addWidget(QLabel("🧠 Session Instructions:"))
        right_layout.addWidget(self.thought_editor)
        
        input_layout = QHBoxLayout()
        self.user_input = QTextEdit()
        self.user_input.setMaximumHeight(60)
        
        self.btn_send = QPushButton("📤 SEND")
        self.btn_send.clicked.connect(self.send_message)
        self.btn_send.setEnabled(False)
        
        input_layout.addWidget(self.user_input)
        input_layout.addWidget(self.btn_send)
        right_layout.addLayout(input_layout)
        
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        main_layout.addWidget(splitter)

        # Status Bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.lbl_think = QLabel("🧠 Idle")
        self.lbl_mem = QLabel(f"📁 {self.memory.get_file_path()}")
        self.lbl_archive = QLabel("Archive: 0 entries")
        self.lbl_sysprompt = QLabel("⚙️ Prompt: Default")
        self.status.addPermanentWidget(self.lbl_sysprompt)
        self.status.addPermanentWidget(self.lbl_archive)
        self.status.addPermanentWidget(self.lbl_mem)
        self.status.addPermanentWidget(self.lbl_think)

        # Timers
        self.vision_timer = QTimer()
        self.vision_timer.timeout.connect(self.auto_vision_scan)
        
        self.ui_timer = QTimer()
        self.ui_timer.timeout.connect(self.process_ui_updates)
        self.ui_timer.start(100)
        
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self.update_archive_stats)
        self.stats_timer.start(5000)
        
        # Update system prompt preview
        self.update_system_prompt_preview()

    def queue_ui_update(self, func, *args):
        self.ui_update_queue.append((func, args))

    def process_ui_updates(self):
        while self.ui_update_queue:
            try:
                func, args = self.ui_update_queue.pop(0)
                func(*args)
            except Exception as e:
                print(f"UI update error: {e}")

    def log_debug(self, msg: str):
        self.queue_ui_update(self._log_debug_impl, msg)

    def _log_debug_impl(self, msg: str):
        ts = datetime.now().strftime("%H:%M:%S")
        self.txt_debug.append(f"[{ts}] {msg}")
        self.txt_debug.verticalScrollBar().setValue(self.txt_debug.verticalScrollBar().maximum())

    def update_archive_stats(self):
        stats = self.memory.get_archive_stats()
        stats_text = (
            f"💬 Chat: {stats['chat_files']}\n"
            f"📄 PDF: {stats['pdf_files']}\n"
            f"🖼️ Images: {stats['image_files']}\n"
            f"🎤 Audio: {stats['audio_files']}\n"
            f"📝 Text: {stats['text_files']}\n"
            f"📊 Indexed: {stats['total_index_entries']}"
        )
        self.txt_stats.setText(stats_text)
        self.lbl_archive.setText(f"📊 Archive: {stats['total_index_entries']} entries")

    def update_system_prompt_preview(self):
        """Update system prompt preview display."""
        prompt = prompt_manager.get_current()
        preview = prompt[:200].replace('\n', ' ') + "..." if len(prompt) > 200 else prompt
        self.txt_sysprompt_preview.setText(preview)
        
        # Update status bar
        prompt_name = "Custom"
        for name, p in PRESET_PROMPTS.items():
            if p == prompt:
                prompt_name = name.split()[0]  # Get emoji + first word
                break
        self.lbl_sysprompt.setText(f"⚙️ Prompt: {prompt_name}")

    def update_scan_interval(self, value: int):
        self.auto_scan_interval = value
        self.log_debug(f"⏱️ Interval: {value}s")
        if self.vision_mode_enabled and self.vision_timer.isActive():
            self.vision_timer.setInterval(value * 1000)

    def start_hardware_scan(self):
        self.btn_refresh.setEnabled(False)
        self.scan_progress.setVisible(True)
        self.scan_status.setText("🔄 Scanning...")
        
        if self.scanner_thread and self.scanner_thread.isRunning():
            self.scanner_thread.abort()
            self.scanner_thread.wait(2000)
        
        self.scanner_thread = HardwareScannerThread()
        self.scanner_thread.scan_complete.connect(self.on_scan_done)
        self.scanner_thread.scan_progress.connect(self.scan_status.setText)
        self.scanner_thread.scan_error.connect(self.log_debug)
        self.scanner_thread.start()

    def on_scan_done(self, results: dict):
        self.scan_progress.setVisible(False)
        self.btn_refresh.setEnabled(True)
        self.scan_status.setText("✅ Ready")
        
        models = results['all_models']
        self.cb_vision.clear(); self.cb_vision.addItems(models)
        self.cb_mind.clear(); self.cb_mind.addItems(models)
        self.cb_cam.clear(); self.cb_cam.addItems(results['cameras'])
        
        self.btn_send.setEnabled(True)
        self.btn_vision.setEnabled(True)
        self.btn_analyze.setEnabled(True)  # Enable manual analyze button
        
        count = len([m for m in models if "❌" not in m and "Wait" not in m])
        self.lbl_archive.setText(f"📦 Models: {count}")
        self.log_debug(f"📋 Models: {', '.join(models[:5])}{'...' if len(models)>5 else ''}")
        
        cams = results['cameras']
        if cams and "No Camera" not in cams[0]:
            QTimer.singleShot(300, self.start_camera)
        
        self.update_archive_stats()
        self.update_system_prompt_preview()

    def toggle_vision(self):
        self.vision_mode_enabled = self.btn_vision.isChecked()
        
        if self.vision_mode_enabled:
            self.btn_vision.setText("👁️ Vision: ON")
            self.lbl_vstatus.setText("👁️ Vision: ON (Auto-scan)")
            self.lbl_vstatus.setStyleSheet("color: #0f0; font-weight: bold;")
            self.vision_timer.setInterval(self.auto_scan_interval * 1000)
            self.vision_timer.start()
            self.log_debug(f"✅ Vision ON - {self.auto_scan_interval}s")
            self.chat.append("<b style='color:#0f0'>👁️ Vision Mode: ON</b>")
        else:
            self.btn_vision.setText("👁️ Vision: OFF")
            self.lbl_vstatus.setText("👁️ Vision: OFF")
            self.lbl_vstatus.setStyleSheet("color: #f55; font-weight: bold;")
            self.vision_timer.stop()
            self.lbl_timer.setText("⏱️ Next scan: --")
            self.txt_vision.clear()
            self.log_debug("⏹️ Vision OFF")
            self.chat.append("<b style='color:#f55'>👁️ Vision Mode: OFF</b>")

    def start_camera(self):
        if self.camera_thread and self.camera_thread.isRunning():
            self.camera_thread.abort()
            self.camera_thread.wait(2000)
        
        cam_text = self.cb_cam.currentText()
        if "No Camera" in cam_text or "Wait" in cam_text:
            self.lbl_seeing.setText("⏸️ No camera")
            return
        
        try:
            idx = int(cam_text.split()[-1])
        except:
            idx = 0
        
        self.camera_thread = CameraWorker(idx)
        self.camera_thread.frame_signal.connect(self.on_camera_frame)
        self.camera_thread.status_signal.connect(self.lbl_seeing.setText)
        self.camera_thread.error_signal.connect(self.log_debug)
        self.camera_thread.start()
        self.log_debug(f"📷 Camera {idx} started")

    def on_camera_frame(self, qimg: QImage):
        self.lbl_feed.setPixmap(QPixmap.fromImage(qimg).scaled(
            self.lbl_feed.size(), Qt.KeepAspectRatio))
        
        if self.vision_mode_enabled:
            try:
                rgb = qimg.convertToFormat(QImage.Format_RGB888)
                ptr = rgb.constBits()
                ptr.setsize(qimg.byteCount())
                frame = np.array(ptr).reshape(qimg.height(), qimg.width(), 3)
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                self.current_frame_b64 = encode_frame_to_base64(frame)
            except Exception as e:
                self.log_debug(f"❌ Encode: {e}")

    def auto_vision_scan(self):
        if self.is_scanning:
            return
        
        if not self.current_frame_b64:
            return
        
        vision_model = self.cb_vision.currentText()
        if "Offline" in vision_model or "Wait" in vision_model:
            return
        
        self.is_scanning = True
        self.log_debug(f"🔄 Auto-scan")
        
        self.vision_worker = VisionAnalysisWorker(self.current_frame_b64, vision_model, auto_scan=True)
        self.vision_worker.analysis_complete.connect(self.on_auto_scan_complete)
        self.vision_worker.analysis_error.connect(self.on_auto_scan_error)
        self.vision_worker.debug_signal.connect(self.log_debug)
        self.vision_worker.start()

    def on_auto_scan_complete(self, description: str):
        self.is_scanning = False
        self.txt_vision.setText(description)
        self.memory.set_latest_vision(description)
        
        if self.current_frame_b64:
            save_image_to_archive(self.current_frame_b64, description)
        
        ts = datetime.now().strftime("%H:%M:%S")
        self.lbl_timer.setText(f"⏱️ Next: {self.auto_scan_interval}s")
        
        self.chat.append(f"<b style='color:#fa0'>👁️ [{ts}] Sees:</b> {description[:150]}...")
        self.log_debug(f"✅ Scan: {description[:50]}...")
        self.update_archive_stats()

    def on_auto_scan_error(self, error: str):
        self.is_scanning = False
        self.txt_vision.setText(f"❌ {error}")
        self.lbl_timer.setText("⏱️ Next: --")
        self.log_debug(f"❌ Scan error: {error}")

    def open_archive_browser(self):
        dialog = ArchiveBrowserDialog(self)
        dialog.exec_()
        self.update_archive_stats()

    def open_system_prompt_editor(self):
        """Open system prompt editor dialog."""
        dialog = SystemPromptEditorDialog(self)
        dialog.prompt_changed.connect(self.on_system_prompt_changed)
        dialog.exec_()

    def on_system_prompt_changed(self, prompt: str):
        """Handle system prompt change."""
        self.update_system_prompt_preview()
        self.log_debug(f"⚙️ System prompt updated ({len(prompt)} chars)")
        self.chat.append(f"<b style='color:#aa00aa'>⚙️ System prompt updated!</b>")

    def test_vision(self):
        if self.is_scanning:
            QMessageBox.information(self, "Busy", "Vision analysis already in progress.")
            return
        if not self.current_frame_b64:
            QMessageBox.warning(self, "No Image", "No camera frame available.")
            return
        
        vision_model = self.cb_vision.currentText()
        if "Offline" in vision_model or "Wait" in vision_model:
            QMessageBox.warning(self, "No Model", "Select a vision model.")
            return
        
        self.log_debug(f"🧪 Manual analysis with {vision_model}")
        self.txt_vision.setText("⏳ Analyzing...")
        self.lbl_think.setText("🧪 Analyzing...")
        
        self.vision_worker = VisionAnalysisWorker(self.current_frame_b64, vision_model, auto_scan=False)
        self.vision_worker.analysis_complete.connect(self.on_test_complete)
        self.vision_worker.analysis_error.connect(self.on_test_error)
        self.vision_worker.start()

    def on_test_complete(self, desc: str):
        self.txt_vision.setText(desc)
        self.lbl_think.setText("✅ Done")
        self.log_debug(f"✅ Manual analysis: {desc[:100]}...")
        # Optionally save to archive
        if self.current_frame_b64:
            save_image_to_archive(self.current_frame_b64, desc)

    def on_test_error(self, error: str):
        self.txt_vision.setText(f"❌ {error}")
        self.lbl_think.setText("❌ Failed")
        self.log_debug(f"❌ Manual analysis: {error}")

    def send_message(self):
        if self.is_brain_busy:
            QMessageBox.information(self, "Busy", "Please wait for the current response to complete.")
            return
        
        text = self.user_input.toPlainText().strip()
        if not text:
            return
        
        self.chat.append(f"<b style='color:#7af'>👤 You:</b> {text}")
        self.user_input.clear()
        self.memory.save_thought("User", text)
        
        ctx = self.memory.search_memory(text)
        custom = self.thought_editor.toPlainText().strip()
        mind_model = self.cb_mind.currentText()
        latest_vision = self.memory.get_latest_vision()
        system_prompt = prompt_manager.get_current()
        
        if "Offline" in mind_model or "Wait" in mind_model:
            self.chat.append("<b style='color:red'>⚠️ Select Brain model</b>")
            return
        
        self.is_brain_busy = True
        self.btn_send.setEnabled(False)
        self.lbl_think.setText("🧠 Processing...")
        
        vision_desc = latest_vision if self.vision_mode_enabled else ""
        
        self.brain_worker = BrainResponseWorker(
            text, vision_desc, mind_model, ctx, custom, latest_vision, system_prompt
        )
        self.brain_worker.response_complete.connect(self._on_brain_response)
        self.brain_worker.response_error.connect(self._on_brain_error)
        self.brain_worker.status_signal.connect(self.lbl_think.setText)
        self.brain_worker.start()

    def _on_brain_response(self, response: str):
        self.chat.append(f"<b style='color:#0f0'>🧠 AI:</b> {response}")
        self.memory.save_thought("AI", response)
        self.lbl_mem.setText(f"📁 Updated {datetime.now().strftime('%H:%M')}")
        self.lbl_think.setText("⏸️ Idle")
        self.update_archive_stats()
        self.is_brain_busy = False
        self.btn_send.setEnabled(True)

    def _on_brain_error(self, error: str):
        self.chat.append(f"<b style='color:red'>❌ Error:</b> {error}")
        self.lbl_think.setText("⚠️ Error")
        self.log_debug(f"❌ Brain: {error}")
        self.is_brain_busy = False
        self.btn_send.setEnabled(True)

    def closeEvent(self, event):
        if self.vision_timer and self.vision_timer.isActive():
            self.vision_timer.stop()
        if self.ui_timer and self.ui_timer.isActive():
            self.ui_timer.stop()
        if self.stats_timer and self.stats_timer.isActive():
            self.stats_timer.stop()
        
        if self.camera_thread and self.camera_thread.isRunning():
            self.camera_thread.abort()
            self.camera_thread.wait(3000)
        if self.scanner_thread and self.scanner_thread.isRunning():
            self.scanner_thread.abort()
            self.scanner_thread.wait(3000)
        if self.vision_worker and self.vision_worker.isRunning():
            self.vision_worker.abort()
            self.vision_worker.wait(3000)
        if self.brain_worker and self.brain_worker.isRunning():
            self.brain_worker.abort()
            self.brain_worker.wait(3000)
        
        event.accept()

# ==============================================================================
# ENTRY
# ==============================================================================

if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    app = QApplication(sys.argv)
    app.setFont(QFont("Consolas", 10))
    window = LocalAIAssistant()
    window.show()
    sys.exit(app.exec_())