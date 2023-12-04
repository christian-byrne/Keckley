# Morph Frame

Test project to automate the process of inpainting a video. For example, change an actor's age from old to young or change a person's clothes from lame to stylish -- without changing any other portion of the video.


1. segment a video into masked area (area to be inpainted/changed) and non-masked area (area to stay the same) ![pic](wiki/morph-frame-wiki-mask_video_example.mp4)


1. extract every frame from the original video and the version of the video wherein the non-masked area is made transparent ![frame grid](./wiki/deniro-frames-grid.jpg) ![alpha-frame grid](./wiki/deniro-alpha_frames-grid.jpg)
1. determine keyframes based on relative motion/color changes in the MASKED AREA ![keyframe extraction](./wiki/wiki-extract_keyframes.png)
2. run diffusion model on alpha layers of keyframes with low denoising 
1. manually select the best output for each keyframe (assuming multiple batches were run for each keyframe)
3. composite the selected outputs with the original frames from their associated keyframe-groups
1. upscale the composite frames with selected upscaling models. Layer multiple upscaling outputs with varying opacity or re-segment and upscale by segment, changing model accordingly
1. delete any frames with motion or color differences far above average with previous or next frame (which may occur because of bad diffusinon results or oversized keyframe groups). interpolate generated (or simply blended) frames to compensate. not necessary if interframe communication implemented
1. optionally, user can manually create alpha layers for specific keyframe-groups which had bad results in the automation process and then subsitute them into the provided folders
1. reconstruct the video with the composite frames, slightly lowering speed and blending frames near keyframes
1. generate and interpolate frames to improve motion
1. enhance or filter video

---

<details>
  <summary>
  
  ## process
  
  </summary>
  
### Extract Frames
- accept (1) a video and (2) the same video but masked for inpainting (3) the masked version but all non-transparent masked regions are turned completely white
    - If not using auto-segmentation for mask generation, the easiest method is to use some automated motion tracking component of a video editing software
    - the second option is to create a transparency mask in an offline video editor like Premiere Pro then animate the mask's path by keyframe (in Premiere Pro, create the mask then slide the mouse wheel and change the mask's path as you go)
    - these methods are 10x faster than manually creating masks and make inpainting a video actually possible in a short amount of time
- get FPS of input video
- optionally, based on config, extract every frame of video -> upscale based on config models, tiling, etc. -> re-construct video
- optionally, frame interpolation on input video before mask is created/applied
- extract and store every frame of both videos
- If white-mask version is not supplied AND video format contains alpha (e.g.,12-bit codec + alpha channel - ProRes 4444 + alpha encoding), make separate copies of masked-video frames and apply filter such that the inpainted area is turned completely white (the transparent area ouutside the mask is black)

### Determine Keyframes
- determine keyframes based on the frames of the alpha video using algorithm with optional user preferences (use the alpha video because differences in inpainted area are what's important -- i.e., if the overall scene is changing a lot but the inpainted area is not, there's no reason to set a keyframe, because we are not changing anything outside of the inpainted area)
    - Default algorithm
        - calculates color difference and motion difference
        - frames that exceed average color difference and motion difference (plus or minus weights) are designated as keyframes
    - User input sliders
        - movement in masked area slider
            - more movement -> smaller keyframe group -> difference threshold weights lowered
            - static objects / less movement -> larger keyframe group -> difference threshold weights highered
        - inpainting model and prompt's tendency to converge
            - more determinstic -> more keyframes creates less punishment (i.e., interframe differences not associated with organic movement/change present in original video) ->  smaller keyframe groups
            - less determinstic -> larger keyframe groups -> higher difference thresholds for keyframe
    - (optional) pre-trained keyframe extraction models
    - (optional) keyframe extraction librariers/plug-ins
- get keyframes from (1) the original video and (2) the WHITE mask video
- put these keyframe pairs put into separate folders

### Inpaint Keyframe Alpha Layers
- run SD on the original-keyframe / WHITE-masked-keyframe pairs
    - specify in SD interface options to create composites only 
    - store composites in folder

### Select/Discriminate Outputs
- (POTENTIAL) GUI user-correction process
    - delete inpaint composite+keyframe pairs that are out of place or bad in any way -> then delete the entire associated keyframe group and exclude from output
        - a few spare seconds of choppiness (frame drops) might be a better outcome than having a few keyframes with very jarring/disconnected inpainted sections
    - make multiple composite/keyframe blends for each keyframe and have selection process keyframe by keyframe where user selects with arrow keys which composite to use in the final blended output

### Composite Inpainted Alpha Layers with Keyframe Groups
- blend inpainted alpha layers with the keyframe groups (including keyframe itself) of the original video
    - blending parameters/mode determinatino algorithm
- optionally, based on config, upscale the blended frames based on config's models, tiling, etc.

### Blend Frames 
- stich all blended frames together
    - frame-blending type and options from config
    - output FPS from config
    - video filter options from config

### Video Enhancement
- optionally, video enhancement models
- optionally, frame interpolation

### Output Package
- display or point to output video
- optionally, a comparison grid video is created by placing original, non-upscaled output, and output videos in tiles of a grid
</details>



<details>
  <summary>

  ## todo

  </summary>

### URGENT
- set SD configs
    - ensure composite saving is on
- auto start SD

### LESS URGENT
- prepend CLIP interrogation
- ID hashes
- shutil over `cp` shell cmd

### OPTIONAL FEATURES
- Automate segmentation / Mask creation process (using segmentation AI or using a user-defined block of the image) preceeding rest of process
- interframe communication
- OpenCV and FFmpeg are creating slightly different numbers of frames in their respective decoding processes. One solution may be to use the same frame-comparison tools already present in the code to find the correct "shift" to apply to the arrays such that they are matched, and then cut off the trailing/leading frames from the longer array (or just put them in the last/first keyframe groups respectively)
  
</details>



<details>
  <summary>
  
  ## resources

  </summary>

### Auto-Keyframe Extraction
- https://github.com/keplerlab/katna

### Motion Detection
- https://github.com/zhearing/moving_target_segment
- https://github.com/WillBrennan/MotionDetector
- https://github.com/JakubVojvoda/motion-segmentation
##### Object
- https://github.com/anhphan2705/Object-Detection-Camera-Feed

### Frame Difference
- https://github.com/qbxlvnf11/frame-difference-SSIM/blob/main/Frame_difference_SSIM.ipynb
##### Structural Similarity 
- https://scikit-image.org/docs/stable/api/skimage.metrics.html#skimage.metrics.structural_similarity

### Upscaling CLIs/interfaces
- https://github.com/upscayl/upscayl-ncnn

### Stable Diffusion Interfaces
- 

### CLIP


</details>


## citation