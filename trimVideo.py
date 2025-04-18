from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.tools import cuts
import os

CURDIR = "C:/Users/forev/Downloads/testing"
os.chdir(CURDIR)

def trim_video(input_path, output_path, start_time, end_time):
    """
    Trim a video between start_time and end_time.

    Parameters:
    - input_path (str): Path to the input video file.
    - output_path (str): Path where the trimmed video will be saved.
    - start_time (float): Start time in seconds.
    - end_time (float): End time in seconds.

    Returns:
    - None
    """
    try:
        with VideoFileClip(input_path) as video:
            print(video)
            
            trimmed = video.subclipped(start_time, end_time)
            trimmed.write_videofile(output_path, codec="libx264", audio_codec="aac")
            print(f"Trimmed video saved to {output_path}")
            
    except Exception as e:
        print(f"Error trimming video: {e}")
    
trim_video("input.mp4", "test.mp4", "00:00:01.100", "00:00:04.100")