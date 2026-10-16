# Cue

A simple line-by-line text narration tool for recording tutorials.

This little tool was vibe-coded to help me record tutorials for [Panel Master](https://github.com/SuckDuck/PanelMaster_public).

## Installation

```bash
python -m venv env
source env/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
python cue.py < sample.json
```

A sample script is included in the repository.

Press `D` to play the current line and advance through the tutorial. The key can be changed in `cue.py`.