from PIL import Image
import os


class Blender:
    def __init__(self, config, frames, keyframes):
        self.config = config
        self.frames = frames
        self.keyframes = keyframes

    def blend(self):
        scale = (
            "upscaled" if self.config.get("upscaling")["original"]["enabled"] else "raw"
        )
        original_frames = os.listdir(
            self.config.get("directories")[f"frames_original_background_{scale}"]
        )
        original_frames = sorted(original_frames, key=lambda x: int(x.split(".")[0]))

        for keyframe in self.keyframes:
            alpha_output_path = f"{self.config.get('directories')['frames_output_alpha']}/{keyframe['keyframe_index']}.png"
            blend_target_indices = keyframe["keyframe_children_indices"]
            blend_target_indices.append(keyframe["frame_index_original"])
            blend_target_indices.sort()
            for index in blend_target_indices:
                blend_target_path = (
                    self.config.get("directories")[
                        f"frames_original_background_{scale}"
                    ]
                    + f"/{original_frames[index]}"
                )
                output_path = f"{self.config.get('directories')['frames_composite_all_raw']}/{original_frames[index]}"

                # Load images
                background = Image.open(blend_target_path)
                alpha_channel = Image.open(alpha_output_path)

                # Scale background to match alpha channel dimensions
                background = background.resize(alpha_channel.size, Image.ANTIALIAS)

                # Composite images using alpha channel
                result = Image.alpha_composite(
                    background.convert("RGBA"), alpha_channel
                )

                # Save result
                result.save(output_path)
