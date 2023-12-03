from datetime import datetime
import os.path


class Log:
    def __init__(self, config):
        """Initialize the log object representing the log file for
        the current project on the current day. Each entry in the log
        file is a line of text prepended with time of writing.
        The log file is located at {projects_folder}/{project_name}/log
        """
        self.config = config
        self.verbose = config.get("verbose")
        self.date_title = datetime.now().strftime("%d.%m.%Y")
        if not os.path.exists(self.path()):
            self.write(
                [
                    "Log file for project: " + self.config.get("project_name"),
                    "Creation date: " + self.date_title,
                    "Project path: "
                    + self.config.get("projects_folder")
                    + self.config.get("project_name"),
                ]
            )

    def minute_time(self):
        """Return the current time in the format HH:MM am/pm."""
        return datetime.now().strftime("%I:%M %p")

    def path(self):
        """Return the correct path to this log file."""
        return f"{self.config.get('projects_folder')}/{self.config.get('project_name')}/log/{self.date_title}.txt"

    def write(self, message):
        """Write the message to the log file."""
        with open(self.path(), "a") as log_file:
            log_file.write("\n\n" + self.minute_time())
            if isinstance(message, list):
                for line in message:
                    log_file.write("\n" + str(line))
                    if self.verbose:
                        print(line)
            else:
                log_file.write("\n" + str(message))
                if self.verbose:
                    print(message)
