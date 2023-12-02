import os
from logger.log import Log
import os.path


class Project:
    def __init__(self, root, project_name, shell_command_handler):
        """Initialize the project object."""
        self.root = root
        self.project_name = project_name
        self.shell_command_handler = shell_command_handler
        self.project_path = self.get_correct_project_path()
        self.new_project = not os.path.exists(self.project_path)
        self.make_directories()
        # directories must be made before creating log
        self.log = Log(root, project_name)

        # If the project does not exist, copy the user-input videos to the
        # project and set the video paths.
        # If the project does exist, set the video paths.
        if self.new_project:
            input_path_original = input("Enter the path to the original video: ")
            while not os.path.exists(input_path_original):
                print("The original video path does not exist.")
                input_path_original = input("Enter the path to the original video: ")
            input_path_masked = input("Enter the path to the masked video: ")
            while not os.path.exists(input_path_masked):
                print("The masked video path does not exist.")
                input_path_masked = input("Enter the path to the masked video: ")

            (
                self.original_video_path,
                self.masked_video_path,
                self.masked_white_video_path,
            ) = self.copy_video_to_project(input_path_original, input_path_masked)
        else:
            project_files = os.listdir(self.project_path)
            for file in project_files:
                without_ext = os.path.splitext(file)[0]
                if without_ext.endswith("-original"):
                    self.original_video_path = f"{self.project_path}/{file}"
                elif without_ext.endswith("-masked_color"):
                    self.masked_video_path = f"{self.project_path}/{file}"
                elif without_ext.endswith("-masked_white"):
                    self.masked_white_video_path = f"{self.project_path}/{file}"

            self.log.write_to_log("Re-Opened project: " + self.project_name + "\n")

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
            f"/frames/masked-white",
            f"/frames/output",
            f"/frames/original/raw",
            f"/frames/original/upscaled",
            f"/frames/masked/raw",
            f"/frames/masked/upscaled",
            f"/frames/masked-white/raw",
            f"/frames/masked-white/upscaled",
            f"/frames/output/raw",
            f"/frames/output/upscaled",
        ]
        for folder in folders:
            folder = self.project_path + folder
            if not os.path.exists(folder):
                os.mkdir(folder)

    def copy_video_to_project(self, original_video_path, masked_video_path):
        """Copy the original and masked videos to the project directory."""
        original_without_ext = ".".join(
            os.path.basename(original_video_path).split(".")[:-1]
        )
        original_ext = os.path.basename(original_video_path).split(".")[-1]
        masked_without_ext = ".".join(
            os.path.basename(masked_video_path).split(".")[:-1]
        )
        masked_ext = os.path.basename(masked_video_path).split(".")[-1]
        new_original_video_path = (
            f"{self.project_path}/{original_without_ext}-original.{original_ext}"
        )
        new_masked_video_path = (
            f"{self.project_path}/{masked_without_ext}-masked_color.{masked_ext}"
        )
        new_white_masked_video_path = (
            f"{self.project_path}/{masked_without_ext}-masked_white.{masked_ext}"
        )
        # TODO: use system call handler instead of os.system for other OS
        os.system(f"cp {original_video_path} {new_original_video_path}")
        os.system(f"cp {masked_video_path} {new_masked_video_path}")
        os.system(f"cp {masked_video_path} {new_white_masked_video_path}")
        self.log.write_to_log(
            [
                "Original video path: " + new_original_video_path + "\n",
                "Copy of original video path: " + new_original_video_path + "\n",
                "Masked video path: " + new_masked_video_path + "\n",
                "Copy of masked video path: " + new_masked_video_path + "\n",
                "Copy of white masked video path: "
                + new_white_masked_video_path
                + "\n",
            ]
        )
        return (
            new_original_video_path,
            new_masked_video_path,
            new_white_masked_video_path,
        )

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
            completed_process = self.shell_command_handler(call)
            self.log.write_to_log(f"Process stdout: {completed_process.stdout}")
            if verbose:
                print(f"{completed_process.stdout}")

    def stitch_output_frames(self, fps=10, verbose=False, raw=False):
        """Stitch the output frames together into a video."""
        system_call = f"ffmpeg -r {fps} -i {self.project_path}/frames/output/{'raw' if raw else 'upscaled'}/%d.png -vcodec libx264 -crf 25 -pix_fmt yuv420p {self.project_path}/output.mp4"
        self.log.write_to_log(f"System call: {system_call}")
        if verbose:
            print(f"System call: {system_call}")
        completed_process = self.shell_command_handler(system_call)
        self.log.write_to_log(f"Process stdout: {completed_process.stdout}")
        if verbose:
            print(f"{completed_process.stdout}")
