https://github.com/upscayl/upscayl-ncnn

# Morph Frame

https://vulkan.lunarg.com/sdk/home


## Resources 

### Auto-Keyframe Exctraction
- https://github.com/keplerlab/katna

### Motion Detection
- https://github.com/zhearing/moving_target_segment
- https://github.com/WillBrennan/MotionDetector
- https://github.com/JakubVojvoda/motion-segmentation
#### Object
- https://github.com/anhphan2705/Object-Detection-Camera-Feed

### Frame Difference
- https://github.com/qbxlvnf11/frame-difference-SSIM/blob/main/Frame_difference_SSIM.ipynb
#### Structural Similarity 
- https://scikit-image.org/docs/stable/api/skimage.metrics.html#skimage.metrics.structural_similarity



## Process

- get FPS of input video
- extract every frame of input videos and put into associated folder
- KEYFRAME DETERMINATION ALGORITHM
    - Based on user input
        - lots of movement in the masked area -> relatively small keyframe group
        - lots of static objects in the masked area -> relatively large keyframe group    
- get keyframes from extracted frames and put into separate folders
- link keyframes of original video with their keyframe group
- run SD, specifying to create composite and put them in specific path
- blend composite with the keyframe groups (including keyframe itself)
    - blending parameters/mode determinatino algorithm
        - blending AI
- stich all blended frames together before or after upscaling

## TODO

- GUI user-correction process
    - delete inpaint composite+keyframe pairs that are out of place or bad in any way -> then delete the entire keyframe group and exclude from output
    - make multiple composite/keyframe blends for each keyframe and have selection process keyframe by keyframe where user selects with arrow keys