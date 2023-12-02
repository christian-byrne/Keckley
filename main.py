"""Script-level comment"""

import os
import subprocess
from frame_analysis.keyframe_extractor import Frames
from project_handler.project import Project
from config_utils.config import Config


def synchronous_shell_command(command):
    """Execute a shell command synchronously."""
    completed_process = None
    try:
        completed_process = subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as error:
        print(error)
    return completed_process


if __name__ == "__main__":
    DEV = True
    root = os.getcwd()
    project_name = input("Enter the project name: ")

    config = Config(root, DEV)
    project = Project(root, project_name, synchronous_shell_command)

    frames = Frames(project.masked_video_path)
    if project.new_project:
        project.extract_input_frames(
            fps=frames.get_fps(), verbose=config.get("verbose")
        )

    if DEV:
        print("Is this a new project?")
        print(project.new_project)
        print("Frames from cv2 frame analysis:")
        print("total frames: " + str(frames.get_frame_count()))
        print("fps: " + str(frames.get_fps()))
        print("Frames from ffmpeg decode:")
        print(
            len(os.listdir(os.path.join(project.project_path, "frames/original/raw")))
        )

    # project.extract_input_frames(
    #     fps=config.get("inputFPS"), verbose=config.get("verbose")
    # )
