from datetime import datetime
import os


class Log:
    def __init__(self, root, project_name):
        """Initialize the log object representing the log file for
        the current project on the current day. Each entry in the log
        file is a line of text prepended with time of writing.
        The log file is located at projects/{project_name}/log/{date}.txt
        """
        self.root = root
        self.project_name = project_name
        self.date_title = datetime.now().strftime("%d.%m.%Y")
        self.log_path = self.get_correct_log_path()
        if not os.path.exists(self.log_path):
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
            log_file.write("\n\n" + self.minute_time() + "\n")
            if isinstance(message, list):
                for line in message:
                    log_file.write(line)
            else:
                log_file.write(message)
