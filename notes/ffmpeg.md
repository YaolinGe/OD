# Common code to be used to generate mp4 from png files
`ffmpeg -framerate 50 -i P_%03d.png -c:v libx264 -profile:v high -crf 20 -pix_fmt yuv420p output.mp4` -> No GPU acceleration
`ffmpeg -framerate 50 -i P_%03d.png -c:v h264_nvenc -profile:v high -cq 20 -pix_fmt yuv420p output.mp4` -> GPU acceleration
