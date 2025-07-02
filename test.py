from moviepy.editor import (
    AudioFileClip,
    TextClip,
    CompositeVideoClip,
    VideoFileClip,
    concatenate_videoclips
)
from TTS.api import TTS
import praw
import os
import time
from datetime import datetime

output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
os.makedirs(output_dir, exist_ok=True)

# Optional: For unique filenames
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

# --------- Reddit Scraper ---------
def fetch_reddit_content(subreddit_name="AskReddit", post_limit=1, comment_limit=3):
    reddit = praw.Reddit(
        client_id="S6rZf3OjDvj3VXTyG7ODyA",
        client_secret="oIhkPBOKCF96it6mDBUCiAjIOH8DrA",
        user_agent="Ok_Insect_9059"
    )

    subreddit = reddit.subreddit(subreddit_name)
    posts = []

    for post in subreddit.hot(limit=post_limit * 5):  # Fetch more to avoid pinned/repeated
        if not post.stickied and not post.over_18:
            content = {
                "title": post.title,
                "comments": []
            }
            post.comments.replace_more(limit=0)
            for comment in post.comments[:comment_limit]:
                content["comments"].append(comment.body)
            posts.append(content)
            if len(posts) >= post_limit:
                break

    return posts


# --------- TTS (Audio Generator) ---------
def text_to_audio(text, filename="output.wav"):
    output_dir = os.path.abspath("output")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, filename)

    tts = TTS(model_name="tts_models/en/jenny/jenny").to("cuda")
    tts.tts_to_file(
        text=text,
        file_path=output_path
    )
    print(f"[AUDIO] Audio saved as {output_path}")
    return output_path


# --------- Word-Level Subtitle Generator ---------
def generate_subtitles(text, duration):
    words = text.split()
    word_count = len(words)
    word_duration = duration / word_count

    subtitles = []

    for i, word in enumerate(words):
        start_time = i * word_duration
        end_time = start_time + word_duration

        txt_clip = (
            TextClip(
                word,
                fontsize=70,
                color="white",
                font="Arial-Bold",
                size=(1000, None),
                method="caption",
                align="center",
            )
            .set_start(start_time)
            .set_end(end_time)
            .set_position(("center", 1600))  # Bottom-ish
        )
        subtitles.append(txt_clip)

    return subtitles


# --------- Video Generator ---------
def create_video(text, audio_path="output.wav", background_video="bg.mp4", output_filename=f"reddit_recap_{timestamp}.mp4"):
    output_path = os.path.join(output_dir, output_filename)

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, output_filename)

    audioclip = AudioFileClip(audio_path)

    # Background video
    bg_clip = VideoFileClip(background_video)

    if bg_clip.duration < audioclip.duration:
        loops = int(audioclip.duration // bg_clip.duration) + 1
        bg_clip = concatenate_videoclips([bg_clip] * loops)

    background = bg_clip.set_duration(audioclip.duration)
    background = background.resize(height=1920).crop(x_center=background.w / 2, width=1080)

    # Title at top
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

    # Subtitles word by word
    subtitles = generate_subtitles(text, audioclip.duration)

    # Combine all layers
    final = CompositeVideoClip([background, title_clip] + subtitles)
    final = final.set_audio(audioclip)

    try:
        print(f"[DEBUG] Full output path: {output_path}")
        final.write_videofile(
            output_path,
            fps=24,
            codec="libx264",
            audio_codec="aac",
            temp_audiofile=os.path.join(output_dir, f"temp-audio-{timestamp}.m4a"),
            remove_temp=True,
            verbose=True,
            logger="bar"
        )
        print(f"[VIDEO] Video saved as {output_path}")

    except Exception as e:
        print(f"[ERROR] Video export failed: {e}")
        raise e

    return output_path


# --------- Main Pipeline ---------
if __name__ == "__main__":
    timestamp = str(int(time.time()))
    output_dir = os.path.abspath("output")
    os.makedirs(output_dir, exist_ok=True)

    posts = fetch_reddit_content(subreddit_name="AskReddit", post_limit=1, comment_limit=3)

    for post in posts:
        combined_text = f"{post['title']}. "
        for idx, comment in enumerate(post['comments']):
            combined_text += f"Comment {idx + 1}: {comment}. "

        print(f"[TEXT] Processing: {combined_text}")

        # Generate audio
        audiofile = text_to_audio(combined_text, filename=f"output_{timestamp}.wav")

        # Create video
        create_video(
            text=post["title"],
            audio_path=audiofile,
            background_video="bg.mp4",
            output_filename=f"reddit_recap_{timestamp}.mp4"
        )
