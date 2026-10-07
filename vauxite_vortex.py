#!/usr/bin/env python3
"""Vauxite Vortex — neon radial colour-gate arcade for ElbowOS. Python 3 + pygame.

Steer a three-colour iris so inbound ore motes cross a matching arc.
Left / Right rotate. Space boosts spin. R restarts.
"""
import math, os, random, subprocess, sys

RECORD = "--play" not in sys.argv
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
if RECORD:
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

W, H, FPS, SECS = 1080, 1920, 30, 15
OUT = os.environ.get("ELBOWOS_MP4", "VAUXITE_VORTEX_ElbowOS.mp4")
TITLE, HANDLE = "VAUXITE VORTEX", "x.com/ElbowOS"
CX, CY, GATE = 540, 980, 310
COLS = [(48, 232, 255), (255, 168, 42), (255, 64, 188)]
NAMES = ("AZURE", "AMBER", "MAGENTA")
INK, DEEP = (236, 244, 255), (7, 5, 20)


def wrap(a):
    return (a + math.pi) % (2 * math.pi) - math.pi


class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        flags = 0 if not RECORD else pygame.HIDDEN
        try:
            self.screen = pygame.display.set_mode((W, H), flags)
        except pygame.error:
            os.environ["SDL_VIDEODRIVER"] = "dummy"
            pygame.display.quit()
            pygame.display.init()
            self.screen = pygame.display.set_mode((W, H), pygame.HIDDEN)
        pygame.display.set_caption(TITLE)
        self.font = pygame.font.SysFont("arial", 64, bold=True)
        self.mid = pygame.font.SysFont("arial", 36, bold=True)
        self.small = pygame.font.SysFont("arial", 28, bold=True)
        self.reset()

    def reset(self):
        self.t = 0
        self.score = 0
        self.streak = 0
        self.best = 0
        self.lives = 3
        self.gate = 0.4
        self.spin = 0.0
        self.motes = []
        self.sparks = []
        self.pops = []
        self.flash = 0
        self.spawn = 0
        self.rng = random.Random(7 if RECORD else None)

    def spawn_mote(self):
        ang = self.rng.random() * math.tau
        col = self.rng.randrange(3)
        self.motes.append({
            "r": 760 + self.rng.random() * 40,
            "a": ang,
            "c": col,
            "dr": 2.6 + self.rng.random() * 1.4 + min(self.t, 400) * 0.004,
            "da": (0.012 if self.rng.random() < 0.5 else -0.012) * (0.7 + self.rng.random()),
            "hit": False,
        })

    def segment_at(self, ang):
        rel = (ang - self.gate) % math.tau
        return int(rel / (math.tau / 3)) % 3

    def auto(self):
        soon = [m for m in self.motes if GATE - 8 < m["r"] < GATE + 220]
        soon.sort(key=lambda m: m["r"])
        if not soon:
            self.spin *= 0.9
            self.gate += 0.01
            return
        m = soon[0]
        # put colour segment centre on the mote
        target = m["a"] - m["c"] * (math.tau / 3) - (math.tau / 6)
        err = wrap(target - self.gate)
        self.spin = max(-0.085, min(0.085, err * 0.35))
        self.gate += self.spin

    def step(self, keys=None):
        self.t += 1
        self.flash = max(0, self.flash - 1)
        if RECORD or keys is None:
            self.auto()
        else:
            if keys[pygame.K_LEFT]:
                self.gate -= 0.055
            if keys[pygame.K_RIGHT]:
                self.gate += 0.055
            if keys[pygame.K_SPACE]:
                self.gate += 0.09
        self.spawn -= 1
        if self.spawn <= 0 and len(self.motes) < 9:
            self.spawn_mote()
            self.spawn = max(14, 28 - self.t // 80)
        kept = []
        for m in self.motes:
            m["r"] -= m["dr"]
            m["a"] += m["da"]
            if not m["hit"] and m["r"] <= GATE:
                m["hit"] = True
                ok = self.segment_at(m["a"]) == m["c"]
                if ok:
                    self.streak += 1
                    self.best = max(self.best, self.streak)
                    gain = 100 + 25 * min(self.streak, 8)
                    self.score += gain
                    self.pops.append([m["a"], GATE, f"+{gain}", 22, COLS[m["c"]]])
                    for i in range(12):
                        self.sparks.append([
                            CX + math.cos(m["a"]) * GATE,
                            CY + math.sin(m["a"]) * GATE,
                            math.cos(m["a"] + i) * (3 + i % 4),
                            math.sin(m["a"] + i) * (3 + i % 4),
                            16, COLS[m["c"]],
                        ])
                else:
                    self.streak = 0
                    self.lives -= 1
                    self.flash = 8
                    if self.lives <= 0:
                        self.lives = 3
                        self.score = max(0, self.score - 200)
            if m["r"] > 70:
                kept.append(m)
        self.motes = kept
        self.sparks = [s for s in self.sparks if s[4] > 0]
        for s in self.sparks:
            s[0] += s[2]
            s[1] += s[3]
            s[4] -= 1
        self.pops = [p for p in self.pops if p[3] > 0]
        for p in self.pops:
            p[3] -= 1

    def draw(self, surf):
        surf.fill(DEEP)
        # indigo well + spiral arms
        for i, rad in enumerate(range(820, 40, -70)):
            shade = 14 + (i % 3) * 6
            pygame.draw.circle(surf, (shade, 10 + i, 36 + i * 2), (CX, CY), rad, 2)
        for arm in range(6):
            pts = []
            a0 = self.t * 0.01 + arm * math.tau / 6
            for k in range(18):
                rr = 120 + k * 36
                aa = a0 + k * 0.18
                pts.append((CX + math.cos(aa) * rr, CY + math.sin(aa) * rr))
            if len(pts) > 1:
                pygame.draw.lines(surf, (28, 22, 58), False, pts, 2)
        # colour iris
        for i in range(3):
            a0 = self.gate + i * math.tau / 3
            rect = pygame.Rect(CX - GATE, CY - GATE, GATE * 2, GATE * 2)
            pygame.draw.arc(surf, COLS[i], rect, -a0 - math.tau / 3 + 0.06, -a0 - 0.06, 22)
            mid = a0 + math.tau / 6
            lx, ly = CX + math.cos(mid) * (GATE + 36), CY + math.sin(mid) * (GATE + 36)
            lab = self.small.render(NAMES[i][:3], True, COLS[i])
            surf.blit(lab, lab.get_rect(center=(lx, ly)))
        pygame.draw.circle(surf, (18, 40, 70), (CX, CY), 92)
        pygame.draw.circle(surf, (80, 230, 255), (CX, CY), 92, 3)
        core = self.mid.render("VAUX", True, INK)
        surf.blit(core, core.get_rect(center=(CX, CY)))
        for m in self.motes:
            x = CX + math.cos(m["a"]) * m["r"]
            y = CY + math.sin(m["a"]) * m["r"]
            col = COLS[m["c"]]
            pygame.draw.circle(surf, col, (int(x), int(y)), 16)
            pygame.draw.circle(surf, (255, 255, 255), (int(x), int(y)), 6)
        for s in self.sparks:
            pygame.draw.circle(surf, s[5], (int(s[0]), int(s[1])), max(2, s[4] // 3))
        for p in self.pops:
            x = CX + math.cos(p[0]) * p[1]
            y = CY + math.sin(p[0]) * p[1] - (22 - p[3]) * 2
            lab = self.small.render(p[2], True, p[4])
            surf.blit(lab, lab.get_rect(center=(x, y)))
        if self.flash:
            veil = pygame.Surface((W, H), pygame.SRCALPHA)
            veil.fill((255, 40, 80, 70))
            surf.blit(veil, (0, 0))
        title = self.font.render(TITLE, True, (120, 240, 255))
        surf.blit(title, title.get_rect(center=(W // 2, 120)))
        sc = self.font.render(f"SCORE {self.score}", True, (255, 210, 90))
        surf.blit(sc, sc.get_rect(center=(W // 2, 210)))
        st = self.mid.render(f"STREAK {self.streak}   LIVES {self.lives}", True, INK)
        surf.blit(st, st.get_rect(center=(W // 2, 280)))
        handle = self.mid.render(HANDLE, True, (255, 90, 190))
        surf.blit(handle, handle.get_rect(center=(W // 2, H - 90)))
        hint = self.small.render("MATCH THE ARC  ·  LEFT / RIGHT", True, (170, 190, 220))
        surf.blit(hint, hint.get_rect(center=(W // 2, H - 160)))

    def play(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    running = False
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_r:
                    self.reset()
            self.step(pygame.key.get_pressed())
            self.draw(self.screen)
            pygame.display.flip()
            clock.tick(FPS)
        pygame.quit()

    def record(self):
        dest = os.path.dirname(OUT)
        if dest:
            os.makedirs(dest, exist_ok=True)
        cmd = [
            "ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
            "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
            "-movflags", "+faststart", "-an", OUT,
        ]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        frames = FPS * SECS
        try:
            for _ in range(frames):
                self.step()
                self.draw(self.screen)
                raw = pygame.image.tobytes(self.screen, "RGB")
                proc.stdin.write(raw)
        finally:
            proc.stdin.close()
        err = proc.stderr.read().decode("utf-8", "ignore")
        rc = proc.wait()
        if rc != 0:
            raise SystemExit(f"ffmpeg failed ({rc}):\n{err[-1200:]}")
        print("wrote", OUT, "frames", frames)
        pygame.quit()


def main():
    g = Game()
    if RECORD:
        g.record()
    else:
        g.play()


if __name__ == "__main__":
    main()
