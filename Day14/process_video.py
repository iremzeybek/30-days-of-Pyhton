from moviepy import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip
from moviepy.video.fx import FadeIn, FadeOut


# ================================
# SETTINGS
# ================================
INPUT_VIDEO = "input_video.mp4"
MUSIC_FILE = "background_music.mp3"
OUTPUT_VIDEO = "final_output.mp4"

TITLE_TEXT = "Automated Video Processing with Python"
WATERMARK_TEXT = "© Irem Zeybek"

TRIM_START = 0      # seconds
TRIM_END = 10       # seconds


# ================================
# LOAD VIDEO
# ================================
video = VideoFileClip(INPUT_VIDEO)

# Trim the video
video = video.subclipped(TRIM_START, TRIM_END)

# Resize to 720p while keeping aspect ratio
video = video.resized(height=720)


# ================================
# TITLE CLIP
# ================================
title = TextClip(
    text=TITLE_TEXT,
    font_size=50,
    color="white",
    duration=3
)

title = title.with_position(("center", "center"))


# ================================
# WATERMARK
# ================================
watermark = TextClip(
    text=WATERMARK_TEXT,
    font_size=24,
    color="white",
    duration=video.duration
)

watermark = watermark.with_position(("right", "bottom"))


# ================================
# BACKGROUND MUSIC
# ================================
music = AudioFileClip(MUSIC_FILE)

# Match music duration to video duration
music = music.subclipped(0, min(music.duration, video.duration))

# Lower music volume
music = music.with_volume_scaled(0.2)

# Replace video audio with music
video = video.with_audio(music)


# ================================
# COMBINE EVERYTHING
# ================================
final = CompositeVideoClip(
    [video, title, watermark],
    size=video.size
)

# Add fade effects
final = FadeIn(final, duration=1)
final = FadeOut(final, duration=1)


# ================================
# EXPORT VIDEO
# ================================
final.write_videofile(
    OUTPUT_VIDEO,
    codec="libx264",
    audio_codec="aac",
    fps=24
)

print("Video processing complete! Saved as:", OUTPUT_VIDEO)
