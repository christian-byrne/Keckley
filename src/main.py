"""Script-level comment"""

import os
import os.path
import shutil
import subprocess
import json
from frame_analysis.keyframe_extractor import KeyFrames
from project_manager.project import Project
from config_utils.config import Config
from image_compositing.image_layer_blender import Blender
from log_utils.log import Log


def synchronous_shell_command(command):
    """Execute a shell command synchronously."""
    completed_process = None
    try:
        completed_process = subprocess.run(
            command, shell=True, check=True, stdout=subprocess.PIPE
        )
    except subprocess.CalledProcessError as error:
        print(error)
    return completed_process


def create_proj_folders(path_dict, proj_root):
    """Create the folder structure from the paths in the path_dict."""
    for path in path_dict.values():
        os.makedirs(path.replace("$project_root$", proj_root), exist_ok=True)


def verify_path(prompt):
    """Verify that the path exists."""
    path = input(prompt)
    while not os.path.exists(path):
        print("The path does not exist.")
        path = input(prompt)
    return path


def create_new_proj(projects_folder, project_name, config):
    print("Creating new project at: " + f"{projects_folder}/{project_name}")
    create_proj_folders(config["directories"], f"{projects_folder}/{project_name}")
    config["project_name"] = project_name
    config["projects_folder"] = projects_folder
    for key, value in config["directories"].items():
        config["directories"][key] = value.replace(
            "$project_root$", f"{projects_folder}/{project_name}"
        )

    bg_vid, alpha_vid, alpha_white_vid = (
        verify_path("Enter the path to the background video: "),
        verify_path("Enter the path to the alpha video: "),
        verify_path("Enter the path to the alpha white video: "),
    )
    shutil.copy(bg_vid, config["directories"]["input_videos"] + "/background.mp4")
    shutil.copy(alpha_vid, config["directories"]["input_videos"] + "/alpha.mp4")
    shutil.copy(
        alpha_white_vid, config["directories"]["input_videos"] + "/alpha_white.mp4"
    )
    config["bg_vid"] = config["directories"]["input_videos"] + "/background.mp4"
    config["alpha_vid"] = config["directories"]["input_videos"] + "/alpha.mp4"
    config["alpha_white_vid"] = (
        config["directories"]["input_videos"] + "/alpha_white.mp4"
    )
    json.dump(
        config, open(f"{projects_folder}/{project_name}/config.json", "w"), indent=4
    )


if __name__ == "__main__":
    DEV = True
    new_project = False
    root = os.getcwd()  # Therefore, launcher must be run from the root directory
    project_name = input("Enter the project name: ")
    config = json.load(open(f"{root}/config/config.json"))
    projects_folder = config["projects_folder"].replace("$root$", root)
    if not os.path.exists(f"{projects_folder}/{project_name}"):
        create_new_proj(projects_folder, project_name, config)
        new_project = True

    proj_config = Config(f"{projects_folder}/{project_name}/config.json")
    proj_log = Log(proj_config)
    project = Project(proj_config, proj_log, synchronous_shell_command)
    frames = KeyFrames(proj_config, proj_log)
    keyframe_indices = frames.get_keyframe_original_indices()
    if new_project:
        project.extract_input_frames(frames.get_fps())
        project.store_keyframes(keyframe_indices)

    # !! DO SD here

    if DEV:
        print("cv2 frame analysis:")
        print("total frames: " + str(frames.get_frame_count()))
        print("fps: " + str(frames.get_fps()))
        print("ffmpeg decode:")
        print(
            "total frames"
            + str(
                len(
                    os.listdir(
                        proj_config.get("directories")["frames_original_background_raw"]
                    )
                )
            )
        )

    if input("Do you want to blend the frames? (y/n): ") == "y":
        blender = Blender(
            proj_config, frames.get_frame_objects(), frames.get_keyframe_objects()
        )
        blender.blend()
