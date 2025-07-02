import os
import random
from moviepy.editor import (
    AudioFileClip,
    TextClip,
    CompositeVideoClip,
    VideoFileClip,
    concatenate_videoclips
)
from TTS.api import TTS
import praw


# --------- Folder Setup ---------
OUTPUT_FOLDER = "output"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


# --------- Reddit Scraper ---------
def fetch_random_reddit_post(subreddit_name="AskReddit", comment_limit=3):
    reddit = praw.Reddit(
        client_id="S6rZf3OjDvj3VXTyG7ODyA",
        client_secret="oIhkPBOKCF96it6mDBUCiAjIOH8DrA",
        user_agent="Ok_Insect_9059"
    )

    subreddit = reddit.subreddit(subreddit_name)
    posts = list(subreddit.hot(limit=25))  # Fetch top 25 hot posts
    random_post = random.choice(posts)     # Randomly pick one

    content = {
        "title": random_post.title,
        "comments": []
    }

    random_post.comments.replace_more(limit=0)
    for comment in random_post.comments[:comment_limit]:
        content["comments"].append(comment.body)

    return content


# --------- TTS (Audio Generator) ---------
def text_to_audio(text, filename):
    tts = TTS(model_name="tts_models/en/jenny/jenny").to("cuda")
    tts.tts_to_file(text=text, file_path=filename)
    print(f"[AUDIO] Audio saved as {filename}")
    return filename


# --------- Word-Level Subtitle Generator ---------
def generate_subtitles(text, duration):
    words = text.split()
    word_duration = duration / len(words)

    subtitles = []

    for i, word in enumerate(words):
        start = i * word_duration
        end = start + word_duration

        txt = (TextClip(
            word,
            fontsize=70,
            color="white",
            font="Arial-Bold",
            size=(1000, None),
            method="caption",
            align="center"
        )
        .set_start(start)
        .set_end(end)
        .set_position(("center", 1600)))

        subtitles.append(txt)

    return subtitles


# --------- Video Generator ---------
def create_video(text, audio_path, background_video, output_path):
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"[ERROR] Audio file not found: {audio_path}")

    if not os.path.exists(background_video):
        raise FileNotFoundError(f"[ERROR] Background video not found: {background_video}")

    audioclip = AudioFileClip(audio_path)
    bg_clip = VideoFileClip(background_video)

    # Loop background if needed
    if bg_clip.duration < audioclip.duration:
        loops = int(audioclip.duration // bg_clip.duration) + 1
        bg_clip = concatenate_videoclips([bg_clip] * loops)

    background = bg_clip.set_duration(audioclip.duration)
    background = background.resize(height=1920).crop(x_center=background.w / 2, width=1080)
    print(f"[DEBUG] Full output path: {os.path.abspath(output_path)}")
    title_clip = (TextClip(
        text,
        fontsize=80,
        color="white",
        font="Arial-Bold",
        size=(1000, None),
        method="caption",
        align="center"
    )
    .set_duration(audioclip.duration)
    .set_position(("center", 100)))

    subtitles = generate_subtitles(text, audioclip.duration)

    final = CompositeVideoClip([background, title_clip] + subtitles)
    final = final.set_audio(audioclip)
    print(f"[DEBUG] Full output path: {os.path.abspath(output_path)}")

    print("[VIDEO] Rendering video...")

    try:
        final.write_videofile(
        output_path,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        verbose=True,
        logger="bar"
        )
    except Exception as e:
        print(f"[ERROR] Video rendering failed: {e}")
    finally:
        final.close()
        bg_clip.close()
        audioclip.close()



# --------- Main Pipeline ---------
if __name__ == "__main__":
    post = fetch_random_reddit_post(subreddit_name="AskReddit", comment_limit=3)

    combined_text = f"{post['title']}. "
    for idx, comment in enumerate(post['comments']):
        combined_text += f"Comment {idx + 1}: {comment}. "

    print(f"[TEXT] Processing: {combined_text}")

    audiofile = os.path.join(OUTPUT_FOLDER, "output.wav")
    video_output = os.path.join(OUTPUT_FOLDER, "reddit_recap.mp4")

    text_to_audio(combined_text, filename=audiofile)

    create_video(
        text=post["title"],
        audio_path=audiofile,
        background_video="bg.mp4",
        output_path=video_output
    )
