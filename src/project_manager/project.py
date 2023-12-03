import os
import os.path
import shutil


class Project:
    def __init__(self, config, log, shell_command_handler):
        """Initialize the project object."""
        self.config = config
        self.shell_command_handler = shell_command_handler
        self.log = log

    def path(self):
        """Return the current path to this project."""
        return (
            self.config.get("projects_folder") + "/" + self.config.get("project_name")
        )

    def extract_input_frames(self, fps):
        """Extract the input frames from the original and masked videos."""
        system_calls = [
            f"ffmpeg -i {self.config.get('bg_vid')} -vf fps={fps} {self.config.get('directories')['frames_original_background_raw']}/%d.png",
            f"ffmpeg -i {self.config.get('alpha_vid')} -vf fps={fps} {self.config.get('directories')['frames_original_alpha_raw']}/%d.png",
            f"ffmpeg -i {self.config.get('alpha_white_vid')} -vf fps={fps} {self.config.get('directories')['frames_original_alpha_white_out']}/%d.png",
        ]
        for call in system_calls:
            self.log.write(["System call:", call])
            completed_process = self.shell_command_handler(call)
            self.log.write(["Process stdout:", completed_process.stdout.decode("utf-8")])

    def store_keyframes(self, keyframe_indices):
        if self.config.get("upscaling")["original"]["enabled"]:
            scale = "upscaled"
        else:
            scale = "raw"

        for i in range(
            len(
                os.listdir(
                    self.config.get("directories")[
                        f"frames_original_background_{scale}"
                    ]
                )
            )
        ):
            if i in keyframe_indices:
                shutil.copy(
                    self.config.get("directories")[
                        f"frames_original_background_{scale}"
                    ]
                    + f"/{i}.png",
                    f"{self.config.get('directories')['keyframes_original_background']}/{i}.png",
                )
                shutil.copy(
                    self.config.get("directories")[f"frames_original_alpha_white_out"]
                    + f"/{i}.png",
                    f"{self.config.get('directories')['keyframes_original_alpha_white_out']}/{i}.png",
                )

    def stitch_output_frames(self, fps=30, verbose=False, raw=False):
        """Stitch the output frames together into a video."""
        system_call = f"ffmpeg -r {fps} -i {self.project_path}/frames/output/{'raw' if raw else 'upscaled'}/%d.png -vcodec libx264 -crf 25 -pix_fmt yuv420p {self.project_path}/output.mp4"
        self.log.write(f"System call: {system_call}")
        if verbose:
            print(f"System call: {system_call}")
        completed_process = self.shell_command_handler(system_call)
        self.log.write(f"Process stdout: {completed_process.stdout}")
        if verbose:
            print(f"{completed_process.stdout}")
