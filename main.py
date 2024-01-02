import torch

model = torch.hub.load("PeterL1n/RobustVideoMatting", "mobilenetv3").cpu() # or "resnet50"
convert_video = torch.hub.load("PeterL1n/RobustVideoMatting", "converter")

convert_video(
    model,                           # The loaded model, can be on any device (cpu or cuda).
    input_source='input.mp4',        # A video file or an image sequence directory.
    downsample_ratio=None,           # [Optional] If None, make downsampled max size be 512px.
    output_type='video',             # Choose "video" or "png_sequence"
    output_composition='com.mp4',    # File path if video; directory path if png sequence.
    # output_alpha="pha.mp4",          # [Optional] Output the raw alpha prediction.
    # output_foreground="fgr.mp4",     # [Optional] Output the raw foreground prediction.
    output_video_mbps=4,             # Output video mbps. Not needed for png sequence.
    seq_chunk=12,                    # Process n frames at once for better parallelism.
    num_workers=1,                   # Only for image sequence input. Reader threads.
    progress=True                    # Print conversion progress.
)