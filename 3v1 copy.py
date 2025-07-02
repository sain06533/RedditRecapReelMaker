import os
from moviepy.editor import (
    AudioFileClip,
    TextClip,
    VideoFileClip,
    CompositeVideoClip,
    concatenate_videoclips,
)
from TTS.api import TTS
import praw
import random
import string

# --------- Reddit Scraper ---------
def fetch_random_reddit_post(subreddit_name="AskReddit", post_limit=10, comment_limit=3):
    reddit = praw.Reddit(
        client_id="S6rZf3OjDvj3VXTyG7ODyA",
        client_secret="oIhkPBOKCF96it6mDBUCiAjIOH8DrA",
        user_agent="Ok_Insect_9059"
    )

    subreddit = reddit.subreddit(subreddit_name)
    posts = list(subreddit.hot(limit=post_limit))
    random_post = random.choice(posts)

    content = {
        "title": random_post.title,
        "comments": []
    }
    random_post.comments.replace_more(limit=0)
    for comment in random_post.comments[:comment_limit]:
        content["comments"].append(comment.body)
    return content

# --------- TTS Generator ---------
def text_to_audio(text, filename="output.wav"):
    tts = TTS(model_name="tts_models/en/jenny/jenny").to("cuda")
    tts.tts_to_file(text=text, file_path=filename)
    print(f"[AUDIO] Saved: {filename}")
    return filename

# --------- Subtitles ---------
def generate_subtitles(text, duration):
    words = text.split()
    word_duration = duration / len(words)
    subtitles = []

    for i, word in enumerate(words):
        start = i * word_duration
        end = start + word_duration
        clip = (
            TextClip(
                word,
                fontsize=70,
                color="white",
                font="Arial-Bold",
                size=(1000, None),
                method="caption",
                align="center",
            )
            .set_start(start)
            .set_end(end)
            .set_position(("center", 1600))
        )
        subtitles.append(clip)
    return subtitles

# --------- Video Creator ---------
def create_video(text, audio_path, background_video, output_path):
    audioclip = AudioFileClip(audio_path)

    bg_clip = VideoFileClip(background_video)
    loops_needed = int(audioclip.duration // bg_clip.duration) + 1
    bg_clip = concatenate_videoclips([bg_clip] * loops_needed)
    background = bg_clip.set_duration(audioclip.duration).resize(height=1920).crop(x_center=bg_clip.w / 2, width=1080)

    title_clip = (
        TextClip(
            text,
            fontsize=80,
            color="white",
            font="Arial-Bold",
            size=(1000, None),
            method="caption",
            align="center",
        )
        .set_duration(audioclip.duration)
        .set_position(("center", 100))
    )

    subtitles = generate_subtitles(text, audioclip.duration)
    final_clip = CompositeVideoClip([background, title_clip] + subtitles).set_audio(audioclip)

    try:
        final_clip.write_videofile(output_path, fps=24)
        print(f"[VIDEO] Saved: {output_path}")
    finally:
        final_clip.close()
        audioclip.close()
        bg_clip.close()

# --------- MAIN ---------
if __name__ == "__main__":
    post = fetch_random_reddit_post(subreddit_name="AskReddit", post_limit=10, comment_limit=3)

    combined_text = f"{post['title']}. "
    for idx, comment in enumerate(post['comments']):
        combined_text += f"Comment {idx + 1}: {comment}. "

    print(f"[TEXT] Generating for post: {post['title']}")

    # Output paths
    output_dir = os.path.abspath("./output")
    os.makedirs(output_dir, exist_ok=True)

    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    audio_file = os.path.join(output_dir, f"audio_{random_suffix}.wav")
    video_file = os.path.join(output_dir, f"reddit_recap_{random_suffix}.mp4")

    # Generate Audio
    text_to_audio(combined_text, filename=audio_file)

    # Create Video
    create_video(
        text=post['title'],
        audio_path=audio_file,
        background_video="bg.mp4",
        output_path=video_file,
    )
