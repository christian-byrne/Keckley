"""Script-level comment"""

import os
import json
from datetime import datetime
import subprocess


class Config:
    def __init__(self, root, dev=False):
        """Initialize the config object."""
        self.dev = dev
        self.root = root
        self.config_folder = f"{self.root}/config"
        self.config_path = self.get_correct_config()
        self.config = self.load_config()

    def get_correct_config(self):
        """Return the correct config file based on the DEV flag."""
        if self.dev:
            return f"{self.config_folder}/dev-config.json"
        elif os.path.getsize("./config/user-profile-1.json") > 0:
            return f"{self.config_folder}/user-profile-1.json"
        else:
            return f"{self.config_folder}/defaults.json"

    def load_config(self):
        """Load the config file and return the config object."""
        with open(self.config_path) as config_file:
            config = json.load(config_file)
        return dict(config)

    def get(self, key):
        """Return the value of the key."""
        return self.config[key]


class Log:
    def __init__(self, root, project_name):
        """Initialize the log object."""
        self.root = root
        self.project_name = project_name
        self.date_title = datetime.now().strftime("%d.%m.%Y")
        self.log_path = self.get_correct_log_path()
        if not os.path.exists(self.log_path):
            with open(self.log_path, "w") as log_file:
                log_file.write("")
            self.write_to_log(
                [
                    "Log file for project: " + project_name + "\n",
                    "Creation date: " + self.date_title + "\n",
                    "Project path: "
                    + self.root
                    + "/projects/"
                    + self.project_name
                    + "\n",
                    "\n",
                ]
            )

    def minute_time(self):
        """Return the current time in the format HH:MM am/pm."""
        return datetime.now().strftime("%I:%M %p")

    def get_correct_log_path(self):
        """Return the correct log path."""
        return f"{self.root}/projects/{self.project_name}/log/{self.date_title}.txt"

    def write_to_log(self, message):
        """Write the message to the log file."""
        with open(self.log_path, "a") as log_file:
            log_file.write(self.minute_time() + "\n")
            if isinstance(message, list):
                for line in message:
                    log_file.write(line)
            else:
                log_file.write(message)


class Project:
    def __init__(self, root, project_name):
        """Initialize the project object."""
        self.root = root
        self.project_name = project_name
        self.project_path = self.get_correct_project_path()
        self.make_directories()
        self.log = Log(self.root, self.project_name)

        input_path_original = getUserInput("Enter the path to the original video: ")
        while not verify_local_path(input_path_original):
            print("The original video path does not exist.")
            input_path_original = getUserInput("Enter the path to the original video: ")
        input_path_masked = getUserInput("Enter the path to the masked video: ")
        while not verify_local_path(input_path_masked):
            print("The masked video path does not exist.")
            input_path_masked = getUserInput("Enter the path to the masked video: ")

        self.original_video_path, self.masked_video_path = self.copy_video_to_project(
            input_path_original, input_path_masked
        )

    def get_correct_project_path(self):
        """Return the correct project path."""
        return f"{self.root}/projects/{self.project_name}"

    def make_directories(self):
        """Create the project directories."""
        folders = [
            f"",
            f"/log",
            f"/frames",
            f"/frames/original",
            f"/frames/masked",
            f"/frames/output",
            f"/frames/original/raw",
            f"/frames/original/upscaled",
            f"/frames/masked/raw",
            f"/frames/masked/upscaled",
            f"/frames/output/raw",
            f"/frames/output/upscaled",
        ]
        for folder in folders:
            folder = self.project_path + folder
            if not os.path.exists(folder):
                os.mkdir(folder)

    def copy_video_to_project(self, original_video_path, masked_video_path):
        """Copy the original and masked videos to the project directory."""
        new_original_video_path = (
            f"{self.project_path}/{os.path.basename(original_video_path)}"
        )
        new_masked_video_path = (
            f"{self.project_path}/{os.path.basename(masked_video_path)}"
        )
        os.system(f"cp {original_video_path} {new_original_video_path}")
        os.system(f"cp {masked_video_path} {new_masked_video_path}")
        self.log.write_to_log(
            [
                "Original video path: " + new_original_video_path + "\n",
                "Copy of original video path: " + new_original_video_path + "\n",
                "Masked video path: " + new_masked_video_path + "\n",
                "Copy of masked video path: " + new_masked_video_path + "\n",
            ]
        )
        return new_original_video_path, new_masked_video_path

    def extract_input_frames(self, fps=10, verbose=False):
        """Extract the input frames from the original and masked videos."""
        system_calls = [
            f"ffmpeg -i {self.original_video_path} -vf fps={fps} {self.project_path}/frames/original/raw/%d.png",
            f"ffmpeg -i {self.masked_video_path} -vf fps={fps} {self.project_path}/frames/masked/raw/%d.png",
        ]
        for call in system_calls:
            self.log.write_to_log(f"System call: {call}")
            if verbose:
                print(f"System call: {call}")
            completed_process = synchronous_shell_command(call)
            self.log.write_to_log(f"Process stdout: {completed_process.stdout}")
            if verbose:
                print(f"{completed_process.stdout}")

    def stitch_output_frames(self, fps=10, verbose=False, raw=False):
        """Stitch the output frames together into a video."""
        system_call = f"ffmpeg -r {fps} -i {self.project_path}/frames/output/{'raw' if raw else 'upscaled'}/%d.png -vcodec libx264 -crf 25 -pix_fmt yuv420p {self.project_path}/output.mp4"
        self.log.write_to_log(f"System call: {system_call}")
        if verbose:
            print(f"System call: {system_call}")
        completed_process = synchronous_shell_command(system_call)
        self.log.write_to_log(f"Process stdout: {completed_process.stdout}")
        if verbose:
            print(f"{completed_process.stdout}")


def synchronous_shell_command(command):
    """Execute a shell command synchronously."""
    completed_process = None
    try:
        completed_process = subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as error:
        print(error)
    return completed_process


def getUserInput(prompt):
    """Prompt the user for input and return the result."""
    # ADD validation
    return input(prompt)


def verify_local_path(path):
    """Return True if the path exists, False otherwise."""
    # ADD validation
    return os.path.exists(path)


if __name__ == "__main__":
    DEV = True
    root = os.getcwd()

    config = Config(root, DEV)
    project_name = getUserInput("Enter the project name: ")
    project = Project(root, project_name)

    project.extract_input_frames(
        fps=config.get("inputFPS"), verbose=config.get("verbose")
    )

    # TODO Upscale input frames
    # TODO (potential) auto remove background before proceeding from this step, then add background back to final output image
    # TODO Auto segmentation / Mask creation (using segmentation AI or using a user-defined block of the image)
    # TODO Generate output frames with batch SD process
    # TODO Upscale output frames
    # TODO Generate output video with blending and video filter options
    # TODO upscale video with frame interpolation and video enhancement AI
    # TODO (potential) make comparison grid between original and output video

    # TODO interframe communication 
