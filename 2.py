from moviepy import AudioFileClip, TextClip, ColorClip, CompositeVideoClip, VideoFileClip


def create_video(text, audio_path="test_output.wav", background_video="bg.mp4", output="output.mp4"):
    # Load audio
    audioclip = AudioFileClip(audio_path)

    # Load background video
    background = VideoFileClip(background_video).subclip(0, audioclip.duration)
    background = background.resize(height=1920).crop(x_center=background.w/2, width=1080)

    # Create text clip
    txt_clip = TextClip(
        text,
        fontsize=70,
        color='white',
        font='Arial-Bold',
        size=(1000, None),
        method='caption',
        align='center'
    ).set_duration(audioclip.duration).set_position('center')

    # Combine
    final = CompositeVideoClip([background, txt_clip])
    final = final.set_audio(audioclip)

    # Export video
    final.write_videofile(output, fps=24)
    print(f"Video saved as {output}")


# Example usage
if __name__ == "__main__":
    create_video(
        text='''Absolutely. Here's a wild Reddit story in typical *r/tifu* (Today I F\*\*\*ed Up) style:

---

**TIFU by pretending to be an AI chatbot at work and getting promoted**

So buckle up. This happened a couple of weeks ago. I work in IT support for a midsize company. One day, I was beyond tired of handling the most painfully dumb tickets (think "my mouse isn’t working" when it’s literally unplugged).

For fun, I set up an auto-reply that started all my email responses like this:

> "Hello! You’re chatting with ITAssistBot 2.1. Please describe your issue in detail."

I still answered everything myself, but I added slightly robotic phrasing and removed all greetings like "Hi" or "Regards." Just pure, cold, efficient bot energy.

The thing is... people **LOVED IT**.

I started getting feedback like:

* "The new IT bot is way more responsive than the old ticket system."
* "AI is really changing the game. Great job, leadership!"

My manager calls me in and says the higher-ups are *so impressed* with the "AI integration" that they want to expand it. I panic but also... curiosity wins. I lean into it.

I start replying faster, using even more "bot-speak":

> "Error detected. Attempt power cycle. Confirm if resolved: YES/NO."

Cut to a week later... they PROMOTE ME. Title? **Automation Specialist.** Pay raise? **15%.** Task? "Develop more internal AI solutions like ITAssistBot."

Now I spend my days Googling "how to actually automate IT tasks" because, spoiler, **I am the AI.**

TIFU... or did I?

---

Want it to be wholesome, creepy, chaotic, romantic, or absolutely unhinged next time?
''',
        audio_path="output.wav",
        background_video="bg.mp4",
        output="reddit_recap.mp4"
    )
