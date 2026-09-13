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
- **Flexible Folder Structure**: Automatically discovers chapters in subdirectories *or* loose images directly in the root directory.
- **Smart Natural Sorting**: Intelligently handles numeric sorting (`IMG_2` before `IMG_10`), pins covers (`[cover]` or `cover`) first, and puts epilogues last.
- **Zoom Level Maintainer & Vertical Scroll**:
  - **Fit to Width (`Fit W`)**: Automatically renders tall vertical pages (long phone notes, document scans, whiteboard photos, webtoon strips) at full readable width with natural vertical scrolling.
  - **Fit to Screen (`Fit S`)**: Standard contain view for book scans and comics.
  - **Zoom Maintainer (`🔒`)**: Remembers and locks your preferred zoom mode and scale factor across page flips.
  - **Smart Scroll Continuity**: Resets to the top when navigating forward, and smoothly arrives at the bottom when navigating backward.
  - **Zoom Controls Toolbar**: Sleek floating control widget directly above the fullscreen button (`[-] [Fit S / %] [+] [🔒]`).
  - **Drag-to-Pan & Wheel Zoom**: Smooth click-and-drag panning (with drag threshold so panning never triggers false page turns) and `Ctrl + Wheel` zoom.
  - **Instant Image Preloading & Caching**: Nearby images prefetch automatically for lag-free page turns.
- **Collapsible Sidebar Table of Contents**: Organized chapter tree showing page numbers and names, with real-time tracking of your current reading position.
- **Unified 1-Click & Touch Gestures**:
  - Fullscreen mode with auto-hiding controls.
  - Multi-zone navigation: click/tap sides for page turns, center 30% to toggle controls.
  - Desktop left-edge mouse trigger to smoothly peek the sidebar.
  - Touch swipe gestures for tablets and phones with vertical scrolling in fullscreen.
- **URL Reading Progress**: Keeps your current page in the URL query (`?page=X`) so reloading or bookmarking always restores your position.

---

## 📁 Folder Structure

Place `reader.py` directly in the root folder, or point it to any folder on your computer. ChapterFlow works with **chapter subdirectories** as well as **direct loose images**:

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
| `directory` or `-d, --dir` | Path to folder containing chapter subdirectories or loose images | Script directory |
| `-p, --port` | Port to run the server on | `8000` |
| `-b, --bind` | Network interface to bind to (`0.0.0.0` for LAN) | `localhost` |
| `-h, --help` | Show help and usage options | — |

---

## ⌨️ Controls & Shortcuts

ChapterFlow includes a **Reading Direction toggle** in the sidebar (saved automatically in browser storage):
- **Left to Right (Default)**: Optimized for study notes, textbooks, documents, and western reading.
- **Right to Left**: Optimized for Manga and Japanese right-to-left reading.

| Action | Desktop (Mouse & Keyboard) | Touch / Mobile (Left to Right) | Touch / Mobile (Right to Left) |
| :--- | :--- | :--- | :--- |
| **Next Page** | `→` / Click Next Zone* | Tap right zone / Swipe left | Tap left zone / Swipe right |
| **Previous Page** | `←` / Click Prev Zone* | Tap left zone / Swipe right | Tap right zone / Swipe left |
| **Scroll Down** | `↓` or `Space` / `PageDown` (turns page at bottom) | Swipe up / Drag down | Swipe up / Drag down |
| **Scroll Up** | `↑` or `PageUp` (turns page at top) | Swipe down / Drag up | Swipe down / Drag up |
| **Pan Image** | Click & Drag | Touch drag | Touch drag |
| **Zoom In / Out** | `+` / `-` or Zoom Toolbar Buttons (`+` / `−`) | Zoom Toolbar Buttons | Zoom Toolbar Buttons |
| **Zoom at Cursor** | `Ctrl` + Mouse Wheel | Pinch-to-zoom | Pinch-to-zoom |
| **Cycle View Mode** | `W` or Click Zoom Badge (`Fit S` / `Fit W` / `100%`) | Tap Zoom Badge | Tap Zoom Badge |
| **Reset Zoom** | `0` (Reset to Fit Screen) | Tap Zoom Badge | Tap Zoom Badge |
| **Maintain Zoom Across Pages** | `L` or Click Lock Button (`🔒`) | Tap Lock Button (`🔒`) | Tap Lock Button (`🔒`) |
| **Jump to First Page** | `Home` | — | — |
| **Jump to Last Page** | `End` | — | — |
| **Toggle Fullscreen** | `F` or Fullscreen button | Fullscreen button | Fullscreen button |
| **Toggle Sidebar / TOC** | Hover left edge or **Click Center 30%** | Tap screen center (middle 30%) | Tap screen center (middle 30%) |

*\*In Left to Right mode, clicking the right side advances and left side goes back. In Right to Left mode, clicking the left side advances.*

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
