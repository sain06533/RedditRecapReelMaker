from moviepy.editor import TextClip, CompositeVideoClip

clip = TextClip("Hello, Rio!", fontsize=80, color='white', size=(1080, 1920))
clip = clip.set_duration(5)

output = "test_output.mp4"

clip.write_videofile(output, fps=24)
