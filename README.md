# Vauxite Vortex

Full-colour Python 3 neon radial colour-gate arcade for ElbowOS.

Ore motes spiral into a three-colour iris (azure, amber, magenta). Rotate the iris so each mote crosses its matching arc. Streaks raise the payout. A mismatch cracks a life.

This is an original arcade toy. It is not a Nintendo ROM, not an emulator, and it does not use trademarked characters.

## Play

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 vauxite_vortex.py --play
```

Left / Right rotate the iris. Space boosts spin. R restarts.

## Record a 9:16 reel

```bash
python3 vauxite_vortex.py
```

Writes `VAUXITE_VORTEX_ElbowOS.mp4` (1080x1920, 15s, 30fps, libx264 yuv420p). Needs ffmpeg on PATH. Headless recording uses SDL's dummy video driver.

## Links

- Featured account: https://x.com/ElbowOS
- Drive reel: https://drive.google.com/file/d/1GdsI21TBi7UocofNGTO1QWrAGsq0r02S/view?usp=drivesdk
