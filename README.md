# mysearch

A floating, glass-style quick search bar for Windows, built from scratch in Python.
Instead of opening File Explorer, press and search your files, folders, and images
from a translucent pill that floats on top of everything.

## Features

- **Live search** across your user folder as you type
- **Instant file preview** — image files show a thumbnail while you type
- **Keyboard driven** — Tab to autofill, Up/Down to pick a result, Enter to open
- **Glass UI** — rounded, translucent, always-on-top, with smooth open/close animation
- **Drag to move** using the handle bar, or Esc to close

## How it works

The app builds an index of filenames in the background on launch, then filters that
index in memory as you type, so results appear instantly. The interface is built with
Python's `tkinter`, using a transparent color key to create the rounded pill shape and
a canvas layer for the glass effect and animations.

## Built with

- Python 3
- tkinter (GUI)
- Pillow (image thumbnails)

## Running it

```
python finder.py
```

## Notes

A personal project built to learn desktop GUI development and how search indexing works.
<img width="591" height="390" alt="image" src="https://github.com/user-attachments/assets/9ae671d2-4c90-4a21-a48a-208c8fe1a69f" />
