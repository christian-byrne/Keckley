import subprocess


def stitch_output_frames(self, fps=10, verbose=True):
    """Stitch the output frames together into a video."""
    project_path = input("Enter the path to the image directory: ")
    system_call = f"ffmpeg -r {fps} -i {project_path}/%d.png -vcodec libx264 -crf 25 -pix_fmt yuv420p {project_path}/output.mp4"
    self.log.write_to_log(f"System call: {system_call}")
    if verbose:
        print(f"System call: {system_call}")
    completed_process = synchronous_shell_command(system_call)
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
