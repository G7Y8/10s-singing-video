import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
DIST.mkdir(exist_ok=True)

LYRICS = "跟我一起唱，快乐在飞扬！"
OUTPUT = DIST / "10s-singing-video.mp4"
VOICE_WAV = DIST / "voice.wav"
MUSIC_WAV = DIST / "music.wav"
FINAL_AUDIO = DIST / "final_audio.wav"


def run(cmd):
    print("RUN:", " ".join(cmd))
    subprocess.run(cmd, check=True)


def build_voice():
    candidates = [
        ["espeak-ng", "-v", "zh", "-s", "165", "-w", str(VOICE_WAV), LYRICS],
        ["espeak-ng", "-v", "zh+f3", "-s", "165", "-w", str(VOICE_WAV), LYRICS],
        ["espeak-ng", "-v", "en-us", "-s", "165", "-w", str(VOICE_WAV), "Let's sing together, happiness is soaring!"]
    ]
    last_error = None
    for cmd in candidates:
        try:
            run(cmd)
            return
        except Exception as exc:
            last_error = exc
            if VOICE_WAV.exists():
                VOICE_WAV.unlink()
    raise last_error


def build_music():
    run([
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", "sine=frequency=220:duration=10",
        "-f", "lavfi",
        "-i", "sine=frequency=330:duration=10",
        "-filter_complex", "[0:a][1:a]amix=inputs=2:duration=longest:dropout_transition=0",
        "-ar", "44100",
        "-ac", "2",
        str(MUSIC_WAV),
    ])


def mix_audio():
    run([
        "ffmpeg", "-y",
        "-i", str(MUSIC_WAV),
        "-i", str(VOICE_WAV),
        "-filter_complex", "[0:a][1:a]amix=inputs=2:duration=longest:dropout_transition=0",
        "-ar", "44100",
        "-ac", "2",
        str(FINAL_AUDIO),
    ])


def build_video():
    text_main = "跟我一起唱"
    text_sub = "快乐在飞扬！"
    run([
        "ffmpeg",
        "-y",
        "-f", "lavfi",
        "-i", "color=c=#0b1020:s=1280x720:d=10",
        "-i", str(FINAL_AUDIO),
        "-vf",
        (
            "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
            f"text='{text_main}':fontcolor=white:fontsize=54:x=(w-text_w)/2:y=h/2-70,"
            f"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
            f"text='{text_sub}':fontcolor=#7dd3fc:fontsize=50:x=(w-text_w)/2:y=h/2+30,"
            "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
            "text='10s Singing Video':fontcolor=white:fontsize=24:x=80:y=h-80:alpha=0.85"
        ),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-shortest",
        str(OUTPUT),
    ])


def main():
    build_voice()
    build_music()
    mix_audio()
    build_video()
    print(f"Video generated at {OUTPUT}")


if __name__ == "__main__":
    main()
