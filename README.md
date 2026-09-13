# 📖 ChapterFlow

A fast, lightweight, zero-dependency local web reader for chaptered image folders — built for **phone camera study notes**, **lecture slides & whiteboards**, **document scans**, **sketchbooks**, and **comics**.

---

## 🎯 Use Cases

- 📝 **Lecture & Study Notes**: Flip seamlessly through phone photos of handwritten notebooks, whiteboard sessions, or textbook chapters organized by lecture or week (`Week 01/`, `Lecture 02 - Calculus/`).
- 📄 **Document & Book Scans**: Review receipts, manuals, recipes, or multi-page paper documents without needing bulky PDF software.
- 🎨 **Art & Design Progress**: Review sketchbooks, storyboards, and design iterations.
- 📚 **Manga & Comics**: Distraction-free, responsive reader with fullscreen mode.

---

## ✨ Features

- **Zero External Dependencies**: Built entirely with Python's standard library (`http.server`, `pathlib`, `json`, `re`, `urllib`). No `pip install` required.
- **Smart Natural Sorting**: Intelligently handles numeric sorting (`IMG_2` before `IMG_10`), pins covers (`[cover]` or `cover`) first, and puts epilogues last.
- **Distraction-Free Dark Mode**: Clean, edge-to-edge reading interface with image auto-scaling (`object-fit: contain`).
- **Collapsible Sidebar Table of Contents**: Organized chapter tree showing page numbers and names, with real-time tracking of your current reading position.
- **Unified 1-Click & Touch Gestures**:
  - Fullscreen mode with auto-hiding controls.
  - Multi-zone navigation: click/tap sides for page turns, center 30% to toggle controls.
  - Desktop left-edge mouse trigger to smoothly peek the sidebar.
  - Touch swipe gestures for tablets and phones.
- **URL Reading Progress**: Keeps your current page in the URL query (`?page=X`) so reloading or bookmarking always restores your position.

---

## 📁 Folder Structure

Place `reader.py` directly in the root folder, or point it to any folder on your computer:

```text
StudyNotes/ (or Comics/)
├── Lecture 01 - Introduction/
│   ├── IMG_001.jpg
│   ├── IMG_002.jpg
│   └── IMG_003.jpg
├── Lecture 02 - Data Structures/
│   ├── IMG_001.jpg
│   └── IMG_002.jpg
├── Chapter 03/
│   └── page_01.png
├── reader.py
├── README.md
├── LICENSE
└── .gitignore
```

---

## 🚀 Quick Start & CLI Options

Run ChapterFlow directly with Python:

```bash
# Basic usage (reads current/script directory on port 8000)
python reader.py

# Specify a custom directory containing your chapters
python reader.py "D:/Manga/OnePiece"

# Specify a custom port
python reader.py --port 8080

# Specify both folder and port
python reader.py "D:/Manga/OnePiece" -p 8080

# Enable access from phone/tablet on your local Wi-Fi network
python reader.py --bind 0.0.0.0
```

### CLI Arguments

| Argument | Description | Default |
| :--- | :--- | :--- |
| `directory` or `-d, --dir` | Path to folder containing chapter subdirectories | Script directory |
| `-p, --port` | Port to run the server on | `8000` |
| `-b, --bind` | Network interface to bind to (`0.0.0.0` for LAN) | `localhost` |
| `-h, --help` | Show help and usage options | — |

---

## ⌨️ Controls & Shortcuts

| Action | Desktop (Mouse & Keyboard) | Touch / Mobile |
| :--- | :--- | :--- |
| **Next Page** | `→` / `Space` / `PageDown` or **Click Left 35%** | Tap left zone / Swipe right (Manga RTL) |
| **Previous Page** | `←` / `PageUp` or **Click Right 35%** | Tap right zone / Swipe left |
| **Jump to First Page** | `Home` | — |
| **Jump to Last Page** | `End` | — |
| **Toggle Fullscreen** | `F` or Fullscreen button | Fullscreen button |
| **Toggle Sidebar / TOC** | Hover left edge or **Click Center 30%** | Tap screen center (middle 30%) |

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
