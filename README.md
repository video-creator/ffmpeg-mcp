# FFmpeg-MCP
Using ffmpeg command line to achieve an mcp server, can be very convenient, through the dialogue to achieve the local video search, tailoring, stitching, playback and other functions

<a href="https://glama.ai/mcp/servers/@video-creator/ffmpeg-mcp">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/@video-creator/ffmpeg-mcp/badge" alt="FFmpeg-Server MCP server" />
</a>

## Support Tools
The server implements the following tools: <br/>
- `find_video_path`
  The parameters are directory and file name, file name can be complete, or is not suffixed, recursive search in the directory, return the full path
- `get_video_info`
  The parameters are video path, return the video info, linkes duration/fps/codec/width/height.
- `clip_video`
  The parameter is the file path, start time, end time or duration, and returns the trimmed file path
- `concat_videos`
  The parameters are the list of files, the output path, and if the video elements in the list of files, such as width, height, frame rate, etc., are consistent, quick mode synthesis is automatically used
- `play_video`
  Play video/audio with ffplay, support many format, like mov/mp4/avi/mkv/3gp, video_path: video path speed: play rate loop: play count
- `overlay_video`
  Two video overlay. <br/>
  background_video: backgroud video path <br/>
  overlay_video: front video path <br/>
  output_path: output video path<br/>
  position: relative location<br/>
  dx: x offset<br/>
  dy: y offset<br/>
- `scale_video`
  Video scale. <br/>
  video_path: in video path <br/>
  width: out video width, -2 keep aspect <br/>
  height: out video height, -2 keep aspect <br/>
  output_path: output video path <br/>
- `extract_frames_from_video`
  Extract images from a video.<br/>
  Parameters: <br/>
  video_path (str): The path to the video.<br/>
  fps (int): Extract one frame every specified number of seconds. If set to 0, extract all frames; if set to 1, extract one frame per second.<br/>
  output_folder (str): The directory where the images will be saved.<br/>
  format (int): The format of the extracted images; 0: PNG, 1: JPG, 2: WEBP.<br/>
  total_frames (int): The maximum number of frames to extract. If set to 0, there is no limit<br/>
<br/>
More features are coming

## Installation procedure
1. Download project
```
git clone  https://github.com/video-creator/ffmpeg-mcp.git
cd ffmpeg-mcp
uv sync
```

2. Configuration in Cline
```
{
  "mcpServers": {
    "ffmpeg-mcp": {
      "autoApprove": [],
      "disabled": false,
      "timeout": 60,
      "command": "uv",
      "args": [
        "--directory",
        "/Users/xxx/Downloads/ffmpeg-mcp",
        "run",
        "ffmpeg-mcp"
      ],
      "transportType": "stdio"
    }
  }
}
```
Note: the value:`/Users/XXX/Downloads/ffmpeg` in args  need to replace the actual download ffmpeg-mcp directory

## Supported platforms
Currently, only macos platforms are supported, including ARM64 or x86_64