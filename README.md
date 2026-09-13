# 📖 ChapterFlow

A fast, lightweight, zero-dependency local web reader for study notes, document scans, books, and comics.

---

## 🚀 Quick Start & Commands

Run directly with Python (no `pip install` required):

```bash
# Read current directory on port 8000
python reader.py

# Read a specific folder (contains subdirectories or loose images)
python reader.py "D:/Manga/OnePiece"

# Custom port and network access for phone/tablet on local Wi-Fi
python reader.py "D:/Notes" -p 8080 --bind 0.0.0.0
```

### CLI Arguments

| Argument | Description | Default |
| :--- | :--- | :--- |
| `directory` or `-d, --dir` | Path to folder with chapters or loose images | Script directory |
| `-p, --port` | Port to run the server on | `8000` |
| `-b, --bind` | Network interface (`0.0.0.0` for LAN access) | `localhost` |
| `-h, --help` | Show usage options | — |

---

## 📁 Folder Structure

Place `reader.py` in the root folder or pass any path via CLI. ChapterFlow supports both **chapter subfolders** and **loose images**:

```text
NotesOrComics/
├── Chapter 01 - Intro/
│   ├── IMG_001.jpg
│   └── IMG_002.jpg
├── Chapter 02/
│   ├── page_01.png
│   └── page_02.png
├── loose_cover.jpg
├── reader.py
└── README.md
```

---

## ⌨️ Controls & Shortcuts

Toggle **Left-to-Right (Notes/Docs)** or **Right-to-Left (Manga)** reading in the sidebar.

| Action | Desktop (Mouse & Keyboard) | Touch / Mobile (LTR) | Touch / Mobile (RTL) |
| :--- | :--- | :--- | :--- |
| **Next Page** | `→` / Click Right Zone* | Tap right / Swipe left | Tap left / Swipe right |
| **Previous Page** | `←` / Click Left Zone* | Tap left / Swipe right | Tap right / Swipe left |
| **Scroll Down / Up** | `↓` / `↑` or `Space` / `PageDown` / `PageUp` | Drag vertically | Drag vertically |
| **Pan Image** | Click & Drag | Touch drag | Touch drag |
| **Zoom In / Out** | `+` / `-` or Toolbar `+` / `−` | Toolbar `+` / `−` | Toolbar `+` / `−` |
| **Zoom at Cursor** | `Ctrl` + Mouse Wheel | Pinch-to-zoom | Pinch-to-zoom |
| **Cycle View Mode** | `W` or Click Zoom Badge (`Fit S` / `Fit W` / `100%`) | Tap Zoom Badge | Tap Zoom Badge |
| **Reset Zoom** | `0` (Reset to Fit Screen) | Tap Zoom Badge | Tap Zoom Badge |
| **Maintain Zoom Lock** | `L` or Click Lock Button (`🔒`) | Tap Lock Button (`🔒`) | Tap Lock Button (`🔒`) |
| **First / Last Page** | `Home` / `End` | — | — |
| **Toggle Fullscreen** | `F` or Fullscreen button | Fullscreen button | Fullscreen button |
| **Toggle Sidebar / TOC** | Hover left edge or **Click Center 30%** | Tap center 30% | Tap center 30% |

*\*In Left-to-Right mode, clicking the right side advances and left side goes back. In Right-to-Left mode, clicking the left side advances.*

---

## ✨ Features

- **Zero Dependencies**: Pure Python standard library (`http.server`, `pathlib`, `json`).
- **Zoom Maintainer & Long-Page Scroll**:
  - **Fit Width (`Fit W`)**: Full-width continuous vertical scroll for tall phone notes, document scans, receipts, and webtoons.
  - **Fit Screen (`Fit S`)**: Standard contain view for book scans and comics.
  - **Maintain Zoom Lock (`🔒`)**: Keeps selected mode and zoom scale locked across page flips.
  - **Smart Continuity**: Resets scroll to top on next page, bottom on previous page.
- **Natural Sorting**: Handles numeric filenames (`IMG_2` before `IMG_10`), pins covers first, and puts epilogues last.
- **Collapsible Sidebar TOC**: Real-time reading position tracker with page names and numbers.
- **Image Preloading & HTTP Caching**: Prefetches nearby images for instant page flips.
- **URL Reading Progress**: Preserves reading progress in the URL (`?page=X`) for bookmarks and reloads.

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.
