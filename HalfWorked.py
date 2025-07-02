from moviepy.editor import (
    AudioFileClip,
    TextClip,
    ColorClip,
    CompositeVideoClip,
    VideoFileClip,
    concatenate_videoclips
)
from TTS.api import TTS
import praw
import os


# --------- Reddit Scraper ---------
def fetch_reddit_content(subreddit_name="AskReddit", post_limit=1, comment_limit=3):
    reddit = praw.Reddit(
        client_id="S6rZf3OjDvj3VXTyG7ODyA",
        client_secret="oIhkPBOKCF96it6mDBUCiAjIOH8DrA",
        user_agent="Ok_Insect_9059"
    )

    subreddit = reddit.subreddit(subreddit_name)
    posts = []

    for post in subreddit.hot(limit=post_limit):
        content = {
            "title": post.title,
            "comments": []
        }
        post.comments.replace_more(limit=0)
        for comment in post.comments[:comment_limit]:
            content["comments"].append(comment.body)
        posts.append(content)
    return posts


# --------- TTS (Audio Generator) ---------
def text_to_audio(text, filename="output.wav"):
    tts = TTS(model_name="tts_models/en/jenny/jenny").to("cuda")

    tts.tts_to_file(
        text=text,
        file_path=filename
    )
    print(f"[AUDIO] Audio saved as {filename}")
    return filename


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
            .set_position(("center", 1600))  # Lower part of the screen
        )
        subtitles.append(txt_clip)

    return subtitles


# --------- Video Generator ---------
def create_video(text, audio_path="output.wav", background_video="bg.mp4", output="output.mp4"):
    # Load audio
    audioclip = AudioFileClip(audio_path)

    # Load background video and loop it if it's shorter
    # Load background video
    bg_clip = VideoFileClip(background_video)
    
    # Loop background if shorter than audio
    if bg_clip.duration < audioclip.duration:
        loops = int(audioclip.duration // bg_clip.duration) + 1
        bg_clip = concatenate_videoclips([bg_clip] * loops)
    
    # Force the exact duration to match audio
    background = bg_clip.set_duration(audioclip.duration)
    
    # Resize and crop for vertical 1080x1920
    background = background.resize(height=1920).crop(x_center=background.w / 2, width=1080)
    
    # Title as permanent top text
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
        .set_position(("center", 100))  # Top
    )

    # Generate word-by-word subtitles
    subtitles = generate_subtitles(text, audioclip.duration)

    # Combine
    final = CompositeVideoClip([background, title_clip] + subtitles)
    final = final.set_audio(audioclip)

    # Export video
    final.write_videofile(output, fps=24)
    print(f"[VIDEO] Video saved as {output}")


# --------- Main Pipeline ---------
if __name__ == "__main__":
    posts = fetch_reddit_content(subreddit_name="AskReddit", post_limit=1, comment_limit=3)
    for post in posts:
        combined_text = f"{post['title']}. "
        for idx, comment in enumerate(post['comments']):
            combined_text += f"Comment {idx + 1}: {comment}. "

        print(f"[TEXT] Processing: {combined_text}")

        # Generate audio
        audiofile = text_to_audio(combined_text, filename="output.wav")

        # Create video
        create_video(
            text=post["title"],  # Only post title as fixed text
            audio_path=audiofile,
            background_video="bg.mp4",
            output="reddit_recap.mp4"
        )
