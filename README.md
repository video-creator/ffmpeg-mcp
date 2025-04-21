# FFmpeg-MCP
Using ffmpeg command line to achieve an mcp server, can be very convenient, through the dialogue to achieve the local video search, tailoring, stitching, playback and other functions

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
  Two video overlay.
  background_video: backgroud video path
  overlay_video: front video path
  output_path: output video path
  position: relative location
  dx: x offset
  dy: y offset
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
