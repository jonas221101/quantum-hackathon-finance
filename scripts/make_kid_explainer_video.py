from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "Quantum_Finance_Kid_Explainer.mp4"

SCENES = [
    (
        "The big question",
        "Imagine a treasure box for a giant retirement fund. Which three baskets should we use?",
        "We are helping a public retirement fund choose three industries for a small investment basket. "
        "The choices are everyday things like technology, healthcare, and utilities. We want a choice that "
        "can be explained to real people, not just a mysterious computer answer.",
    ),
    (
        "What is an industry?",
        "Six teams. Pick three.",
        "An industry is a big group of companies that do similar work. Our six teams are NoDur, Manuf, "
        "Enrgy, HiTec, Hlth, and Utils. NoDur means everyday goods, HiTec means technology, Hlth means "
        "healthcare, and Utils means services like power and water.",
    ),
    (
        "Do not put every egg in one basket",
        "Pick exactly 3 of 6. Give each one one third.",
        "Diversification is a grown-up word for not putting every egg in one basket. We choose exactly three "
        "industries and give each one the same share. There are only twenty possible groups of three, so a "
        "normal computer can check every group exactly.",
    ),
    (
        "Return and risk",
        "More reward can mean more wobble.",
        "Return is how much the basket grows. Risk is how much it wiggles up and down. A technology basket "
        "might grow faster, but it can wiggle more. We measure average growth, wobble, the worst month, "
        "and how often the basket loses more than the rule allows.",
    ),
    (
        "Three different people",
        "Growth, balanced, and risk-sensitive.",
        "Different people can want different things. A growth person is willing to accept more wobble. "
        "A risk-sensitive person cares much more about avoiding losses. A balanced person sits in the middle. "
        "The computer uses a different score for each person, like three different game rulebooks.",
    ),
    (
        "The honest answer",
        "Growth: SWITCH. Balanced: REVIEW. Risk-sensitive: KEEP.",
        "The exact checker gives three useful answers. Growth favors HiTec, Hlth, and Utils. Balanced likes "
        "that basket in normal conditions, but changes its mind during a technology stress test, so the "
        "committee should review it. Risk-sensitive keeps NoDur, Hlth, and Utils.",
    ),
    (
        "What is a qubit?",
        "A tiny quantum coin: 0, 1, or a mix until we look.",
        "A normal computer bit is like a light switch: off or on. A qubit is more like a spinning coin. "
        "Before we look, it can hold a mixture of possibilities. When we measure it, we get one answer. "
        "Quantum algorithms use the wave-like mixture and then measure many times.",
    ),
    (
        "QAOA is a guided guessing game",
        "Guess. Check the score. Turn the knobs. Try again.",
        "QAOA means Quantum Approximate Optimization Algorithm. Imagine a maze with twenty good doors and "
        "some silly doors. The circuit gives doors different chances, a classical computer turns two knobs, "
        "and we repeat the experiment. Better doors should become more likely.",
    ),
    (
        "Two quantum teams",
        "X mixer: penalties. Dicke + XY: rules built in.",
        "Our first quantum team uses penalties. If it picks four industries, it gets a big naughty-point "
        "penalty. Our second team starts with exactly three lights on and uses an XY mixer that keeps exactly "
        "three lights on. That is like building the game rule into the board instead of hoping players obey.",
    ),
    (
        "IBM Aer, honestly",
        "Real Qiskit circuits. Local IBM simulator. No speedup claim.",
        "We run real Qiskit circuits with IBM's local Qiskit Aer simulator. It acts like a pretend quantum "
        "machine on our computer. This is not an IBM cloud computer and not real quantum hardware. We compare "
        "the quantum guesses with the exact classical answer, so we can tell when a guess is right.",
    ),
    (
        "Stress tests and hindsight",
        "Change the weather. Then look at the future only afterward.",
        "We test what happens if technology earns a little less or industries move together more. We also keep "
        "2020 through 2024 hidden until after the decision. That is called holdout testing. It is like taking "
        "a test after studying, without peeking at the answer sheet.",
    ),
    (
        "The kid-sized takeaway",
        "Use quantum ideas carefully. Keep a grown-up answer key.",
        "The important result is not that quantum magic beats a small classical problem. It does not. The "
        "important result is a clear decision, visible rules, stress tests, and an answer we can audit. "
        "Growth switches, balanced reviews, and risk-sensitive keeps. A human committee remains responsible.",
    ),
]


def font(size: int, bold: bool = False):
    candidates = [
        r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def draw_scene(path: Path, index: int, title: str, headline: str) -> None:
    width, height = 1280, 720
    palette = [
        ("#102a43", "#f0b429"),
        ("#243b53", "#62b0e8"),
        ("#334e68", "#f28482"),
        ("#1f4e5f", "#7bdff2"),
    ]
    background, accent = palette[index % len(palette)]
    image = Image.new("RGB", (width, height), background)
    draw = ImageDraw.Draw(image)
    title_font = font(48, True)
    headline_font = font(38, True)
    body_font = font(25)
    small_font = font(22)

    draw.rounded_rectangle((70, 55, 1210, 665), radius=28, fill="#f7fafc")
    draw.rectangle((70, 55, 1210, 75), fill=accent)
    draw.text((110, 105), f"{index + 1:02d}  {title}", font=title_font, fill=background)
    draw.text((110, 190), headline, font=headline_font, fill="#243b53")

    if index == 0:
        draw.ellipse((870, 260, 1020, 410), fill="#f6bd60", outline=accent, width=6)
        draw.ellipse((1020, 260, 1170, 410), fill="#84a59d", outline=accent, width=6)
        draw.text((905, 315), "€", font=font(65, True), fill="#17324d")
        draw.text((1065, 315), "€", font=font(65, True), fill="#17324d")
    elif index in (1, 2):
        labels = ["NoDur", "Manuf", "Enrgy", "HiTec", "Hlth", "Utils"]
        for item, label in enumerate(labels):
            x = 850 + (item % 3) * 115
            y = 275 + (item // 3) * 105
            fill = accent if item in (0, 3, 4) else "#d9e2ec"
            draw.rounded_rectangle((x, y, x + 95, y + 70), 15, fill=fill)
            draw.text((x + 8, y + 23), label, font=small_font, fill=background)
    elif index == 3:
        for item, bar in enumerate((90, 145, 115, 180)):
            x = 875 + item * 65
            draw.rectangle((x, 450 - bar, x + 42, 450), fill=accent)
        draw.line((850, 450, 1160, 450), fill=background, width=4)
        draw.text((890, 475), "growth", font=small_font, fill=background)
    elif index in (4, 5):
        for item, label in enumerate(("GROWTH", "BALANCED", "CAREFUL")):
            y = 280 + item * 95
            draw.rounded_rectangle((850, y, 1140, y + 60), 18, fill=accent if item == index - 4 else "#d9e2ec")
            draw.text((875, y + 18), label, font=small_font, fill=background)
    elif index in (6, 7, 8, 9):
        for item in range(6):
            x = 850 + (item % 3) * 105
            y = 290 + (item // 3) * 105
            on = item < 3 if index == 8 else item % 2 == 0
            draw.ellipse((x, y, x + 58, y + 58), fill=accent if on else "#d9e2ec")
            draw.text((x + 20, y + 15), "1" if on else "0", font=small_font, fill=background)
    elif index == 10:
        draw.line((865, 455, 1150, 280), fill=accent, width=8)
        draw.line((865, 455, 1150, 455), fill="#d9e2ec", width=8)
        draw.text((900, 480), "study", font=small_font, fill=background)
        draw.text((1060, 245), "test", font=small_font, fill=background)
    else:
        for item, label in enumerate(("SWITCH", "REVIEW", "KEEP")):
            y = 270 + item * 95
            draw.rounded_rectangle((850, y, 1150, y + 62), 18, fill=accent if item == 1 else "#d9e2ec")
            draw.text((920, y + 18), label, font=small_font, fill=background)

    draw.text((110, 565), "Quantum Finance — kid-friendly explainer", font=small_font, fill="#52606d")
    draw.text((1100, 565), f"{index + 1}/{len(SCENES)}", font=small_font, fill="#52606d")
    image.save(path)


def make_audio(text: str, path: Path) -> None:
    escaped = text.replace("'", "''")
    command = (
        "Add-Type -AssemblyName System.Speech; "
        "$s=New-Object System.Speech.Synthesis.SpeechSynthesizer; "
        "$s.Rate=0; $s.Volume=100; "
        f"$s.SetOutputToWaveFile('{str(path).replace(chr(39), chr(39) * 2)}'); "
        f"$s.Speak('{escaped}'); $s.Dispose()"
    )
    subprocess.run(["powershell", "-NoProfile", "-Command", command], check=True)


def run() -> None:
    with tempfile.TemporaryDirectory(prefix="qhf-video-") as temp:
        work = Path(temp)
        clips: list[Path] = []
        for index, (title, headline, narration) in enumerate(SCENES):
            png = work / f"scene-{index:02d}.png"
            wav = work / f"scene-{index:02d}.wav"
            mp4 = work / f"scene-{index:02d}.mp4"
            draw_scene(png, index, title, headline)
            make_audio(narration, wav)
            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-loop",
                    "1",
                    "-i",
                    str(png),
                    "-i",
                    str(wav),
                    "-c:v",
                    "libx264",
                    "-tune",
                    "stillimage",
                    "-c:a",
                    "aac",
                    "-b:a",
                    "128k",
                    "-pix_fmt",
                    "yuv420p",
                    "-shortest",
                    str(mp4),
                ],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            clips.append(mp4)
        concat = work / "concat.txt"
        concat.write_text("".join(f"file '{clip}'\n" for clip in clips), encoding="utf-8")
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(concat),
                "-c",
                "copy",
                str(OUTPUT),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    print(OUTPUT)


if __name__ == "__main__":
    run()
