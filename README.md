# 📖 ChapterFlow

A fast, lightweight, and zero-dependency local web reader tailored for manga, comics, and webtoons organized into chapter folders.

---

## ✨ Features

- **Zero External Dependencies**: Built entirely with Python's standard library (`http.server`, `pathlib`, `json`, `re`, `urllib`). No `pip install` required.
- **Smart Natural Sorting**: Intelligently handles numeric sorting (`page 2` before `page 10`), pins covers (`[cover]` or `cover`) first, and puts epilogues last.
- **Distraction-Free Dark Mode**: Clean, edge-to-edge reading interface with image auto-scaling (`object-fit: contain`).
- **Collapsible Sidebar Table of Contents**: Organized chapter tree showing page numbers and names, with real-time tracking of your current reading position.
- **Manga-Friendly Touch & Gesture Controls**:
  - Fullscreen mode with auto-hiding controls.
  - Multi-zone touch interaction: outer zones for page turns, center 30% to reveal controls.
  - Desktop left-edge mouse trigger to smoothly peek the sidebar.
  - Swipe left/right gestures on mobile devices.
- **URL Reading Progress**: Keeps your current page in the URL query (`?page=X`) so reloading or bookmarking always restores your position.

---

## 📁 Folder Structure

Place `reader.py` directly in the folder containing your chapters or volumes:

```text
ChapterFlow/
├── Chapter 01/
│   ├── [cover].jpg
│   ├── 01.jpg
│   ├── 02.jpg
│   └── 03.jpg
├── Chapter 02/
│   ├── 01.jpg
│   └── 02.jpg
├── Epilogue/
│   └── 01.jpg
├── reader.py
├── README.md
├── LICENSE
└── .gitignore
```

---

## 🚀 Quick Start

1. **Start the server**:
   ```bash
   python reader.py
   ```

2. **Open your browser**:
   Navigate to:
   ```text
   http://localhost:8000
   ```

---

## ⌨️ Controls & Shortcuts

| Action | Desktop / Keyboard | Touch / Mobile |
| :--- | :--- | :--- |
| **Next Page** | `→` / `Space` / `PageDown` | Tap left zone / Swipe right (Manga RTL) |
| **Previous Page** | `←` / `PageUp` | Tap right zone / Swipe left |
| **Jump to First Page** | `Home` | — |
| **Jump to Last Page** | `End` | — |
| **Toggle Fullscreen** | `F` or Fullscreen button | Fullscreen button |
| **Toggle Sidebar / TOC** | Hover left screen edge | Tap screen center (middle 30%) |

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
