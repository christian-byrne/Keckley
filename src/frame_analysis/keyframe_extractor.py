import cv2
from pprint import pformat


class KeyFrames:
    """
    This class is responsible for analyzing the frames of the alpha video and determining which frames are keyframes.
    It also stores the keyframes and their children in a list of dictionaries.

    Keyframes are determined by comparing the color and motion differences between frames.
    The color difference is calculated by comparing the histograms of the grayscale versions of the frames.
    The motion difference is calculated by comparing the grayscale versions of the frames.

    The average color and motion differences are calculated and used, along with the user's weights, to determine the thresholds for determining keyframes.

    The thresholds are calculated by subtracting the minimum difference from the average difference and multiplying by the threshold weight. The combined threshold is the sum of the motion and color thresholds.

    Once the thresholds are calculated, the frames are analyzed again to determine keyframes.

    The first frame is set as a keyframe. Then, the color and motion differences between each frame and the previous KEYFRAME are calculated for each frame.
    If the combined difference is greater than the combined threshold, the frame is set as a keyframe.
    Otherwise, the frame is set as a child of the previous keyframe.

    Weights and thresholds are set in the config.json file.

    Attributes:
        config (dict): The project's config dictionary.
        log (Log): The project's log object.
        frames (list): A list of frame objects.
        keyframes (list): A list of pointers to frame objects in self.frames.
        all_color_diffs (list): A list of all color differences between frames.
        all_motion_diffs (list): A list of all motion differences between frames.
        min_color_diff (float): The minimum color difference between frames.
        max_color_diff (float): The maximum color difference between frames.
        average_color_diff (float): The average color difference between frames.
        min_motion_diff (float): The minimum motion difference between frames.
        max_motion_diff (float): The maximum motion difference between frames.
        average_motion_diff (float): The average motion difference between frames.
        calculated_motion_threshold (float): The calculated motion threshold for determining keyframes.
        calculated_color_threshold (float): The calculated color threshold for determining keyframes.
        combined_threshold (float): The combined threshold for determining keyframes.
    """

    def __init__(self, config, log):
        self.config = config
        self.log = log
        self.frames = []
        self.keyframes = []
        self.all_color_diffs = []
        self.all_motion_diffs = []

        self.analyze_frames()
        self.set_difference_measures()
        self.set_difference_thresholds()
        self.set_keyframes()

        self.log.write(
            [
                "fps:",
                self.get_fps(),
                "frame count:",
                self.get_frame_count(),
                "difference properties:",
                pformat(self.get_difference_properties()),
                "keyframe details:",
                pformat(self.get_keyframe_details()),
                "\nkeyframe original indices:",
                self.get_keyframe_original_indices(),
                "\n\nkeyframe visualization:",
                self.get_keyframe_vizualization(),
            ]
        )
        # Probably not necessary to print these objects
        if self.config.get("verbose"):
            self.log.write(
                [
                    "\nframe objects:",
                    pformat(self.get_frame_objects()),
                    "keyframe objects:",
                    pformat(self.get_keyframe_objects()),
                ]
            )

    def get_fps(self):
        return self.fps

    def get_frame_count(self):
        return len(self.frames)

    def get_frame_objects(self):
        return self.frames

    def get_keyframe_objects(self):
        return self.keyframes

    def get_keyframe_original_indices(self):
        return [frame["frame_index_original"] for frame in self.keyframes]

    def get_keyframe_details(self):
        return {
            "number of keyframes": len(self.keyframes),
            "ratio of keyframes to frames": len(self.keyframes) / len(self.frames),
            "average keyframe group size": len(self.frames) / len(self.keyframes),
            # + 1 to account for the keyframe itself
            "largest keyframe group": max(
                [len(x["keyframe_children_indices"]) for x in self.keyframes]
            )
            + 1,
            "smallest keyframe group": min(
                [len(x["keyframe_children_indices"]) for x in self.keyframes]
            )
            + 1,
        }

    def get_keyframe_vizualization(self, line_width=39):
        characters = []
        cur_width = 0
        for frame in self.frames:
            if frame["keyframe"]:
                characters.append("_X_")
            else:
                characters.append("___")
            cur_width += 3
            if cur_width >= line_width == 0:
                characters.append("\n")
                cur_width = 0

        return "".join(characters)

    def get_difference_properties(self):
        return {
            "min_color_diff": self.min_color_diff,
            "max_color_diff": self.max_color_diff,
            "average_color_diff": self.average_color_diff,
            "min_motion_diff": self.min_motion_diff,
            "max_motion_diff": self.max_motion_diff,
            "average_motion_diff": self.average_motion_diff,
            "calculated_motion_threshold": self.calculated_motion_threshold,
            "calculated_color_threshold": self.calculated_color_threshold,
            "combined_threshold": self.combined_threshold,
        }

    def set_difference_measures(self):
        self.min_color_diff = min(self.all_color_diffs)
        self.max_color_diff = max(self.all_color_diffs)
        self.average_color_diff = sum(self.all_color_diffs) / len(self.all_color_diffs)
        self.min_motion_diff = min(self.all_motion_diffs)
        self.max_motion_diff = max(self.all_motion_diffs)
        self.average_motion_diff = sum(self.all_motion_diffs) / len(
            self.all_motion_diffs
        )

    def set_difference_thresholds(self):
        # Placeholder algorithm (needs improving):
        # (average diff) -  (minimum diff) * (1 - threshold)
        self.calculated_motion_threshold = (
            self.average_motion_diff - self.min_motion_diff
        ) * (1 - self.config.get("keyframe_determination")["motion_threshold"])
        self.calculated_color_threshold = (
            self.average_color_diff - self.min_color_diff
        ) * (1 - self.config.get("keyframe_determination")["color_threshold"])
        self.combined_threshold = (
            self.calculated_motion_threshold + self.calculated_color_threshold
        )

    def calculate_color_difference(self, frame1, frame2):
        hist1 = cv2.calcHist(
            [cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)], [0], None, [256], [0, 256]
        )
        hist2 = cv2.calcHist(
            [cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)], [0], None, [256], [0, 256]
        )
        color_diff = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CHISQR)
        return color_diff

    def analyze_frames(self):
        video_capture = cv2.VideoCapture(self.config.get("alpha_vid"))
        frame_count = 0
        ret, prev_frame = video_capture.read()

        self.fps = video_capture.get(cv2.CAP_PROP_FPS)

        while True:
            ret, frame = video_capture.read()

            if not ret:
                break

            cur_frame = {"frame_index_original": frame_count, "cv2_frame_object": frame}
            frame_count += 1
            if frame_count > 1:
                gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gray_prev_frame = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
                motion_diff = cv2.absdiff(gray_frame, gray_prev_frame).sum()
                motion_diff = (
                    motion_diff
                    * self.config.get("keyframe_determination")["motion_weight"]
                )
                self.all_motion_diffs.append(motion_diff)
                cur_frame["motion_diff"] = motion_diff

                color_diff = self.calculate_color_difference(frame, prev_frame)
                color_diff = (
                    color_diff
                    * self.config.get("keyframe_determination")["color_weight"]
                )
                self.all_color_diffs.append(color_diff)
                cur_frame["color_diff"] = color_diff

                cur_frame["combined_score"] = motion_diff + color_diff
                self.frames.append(cur_frame)

            prev_frame = frame

        video_capture.release()
        cv2.destroyAllWindows()

    def set_keyframes(self):
        # Set first frame as keyframe
        first_frame = self.frames[0]
        first_frame.update(
            {
                "keyframe": True,
                "keyframe_children_indices": [],
                "keyframe_index": 0,
            }
        )
        self.keyframes.append(first_frame)

        for frame in self.frames[1:]:
            prev_keyframe = self.keyframes[-1]
            current_group_size = len(prev_keyframe["keyframe_children_indices"])

            gray_frame = cv2.cvtColor(frame["cv2_frame_object"], cv2.COLOR_BGR2GRAY)
            gray_prev_keyframe = cv2.cvtColor(
                prev_keyframe["cv2_frame_object"], cv2.COLOR_BGR2GRAY
            )
            motion_diff = cv2.absdiff(gray_frame, gray_prev_keyframe).sum()
            motion_diff = (
                motion_diff * self.config.get("keyframe_determination")["motion_weight"]
            )
            frame["keyframe_motion_diff"] = motion_diff

            color_diff = self.calculate_color_difference(
                frame["cv2_frame_object"], prev_keyframe["cv2_frame_object"]
            )
            color_diff = (
                color_diff * self.config.get("keyframe_determination")["color_weight"]
            )
            frame["keyframe_color_diff"] = color_diff

            frame["keyframe_combined_score"] = motion_diff + color_diff

            if (
                frame["keyframe_combined_score"] > self.combined_threshold
                or current_group_size
                > self.config.get("keyframe_determination")["max_keyframe_group_size"]
            ):
                frame["keyframe"] = True
                frame["keyframe_children_indices"] = []
                frame["keyframe_index"] = len(self.keyframes)
                self.keyframes.append(frame)
            else:
                frame["keyframe"] = False
                try:
                    self.keyframes[-1]["keyframe_children_indices"].append(
                        frame["frame_index_original"]
                    )
                except IndexError:
                    print(
                        "Frame "
                        + str(frame["frame_index_original"])
                        + " cannot be assigned a parent keyframe because there are no keyframes yet (i.e., this frame occurs before the first keyframe)."
                    )
