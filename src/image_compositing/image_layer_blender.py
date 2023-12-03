import os


class Blender:
    def __init__(self, frames, keyframes, composites_path, outputs_path):
        self.frames = frames
        self.keyframes = keyframes
        self.composites_path = composites_path
        self.outputs_path = outputs_path

    def blend(self):
        original_frames = os.listdir(f"{self.frames}/original/raw")
        original_frames = sorted(original_frames, key=lambda x: int(x.split(".")[0]))

        for keyframe in self.keyframes:
            composite_path = f"{self.composites_path}/{keyframe['keyframe_index']}.png"
            blend_target_indices = keyframe["keyframe_children_indices"]
            blend_target_indices.append(keyframe["frame_index_original"])
            blend_target_indices.sort()
            for index in blend_target_indices:
                frame_path = f"{self.frames}/original/raw/{original_frames[index]}"
                output_path = f"{self.outputs_path}/{original_frames[index]}"

                # !! TODO: Below still needs testing
                # TODO: use passed in shell command handler for cross-OS compatibility
                os.system(f"ffmpeg -i {frame_path} -i {composite_path} -filter_complex \"[1:v]format=rgba,colorchannelmixer=aa=0.5[fg];[0:v][fg]overlay=0:0:format=auto\" {output_path}")
                
