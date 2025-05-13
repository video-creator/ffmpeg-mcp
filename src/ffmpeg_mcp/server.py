# server.py
import os
import sys
cur_path=os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, cur_path+"/..")
from typing import List
from mcp.server.fastmcp import FastMCP
import ffmpeg_mcp.cut_video as cut_video



# Create an MCP server
mcp = FastMCP("ffmpeg-mcp")

# Add an addition tool
@mcp.tool()
def find_video_path(root_path, video_name):
    """
    可以查找视频文件路径，查找文件路径，递归查找精确匹配文件名的视频文件路径（支持带或不带扩展名）
    参数：
    root_path - 要搜索的根目录
    video_name - 视频文件名（可以带扩展名，但会忽略扩展名匹配）
    返回：
    首个匹配的视频文件完整路径，找不到时返回空字符串
    """
    VIDEO_EXTS = {'.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm', '.ts'}
    target_stem, target_ext = os.path.splitext(video_name)
    if target_ext.lower() not in VIDEO_EXTS:
        target_stem = f"{target_stem}{target_ext}"
        target_ext = ""

    for root, dirs, files in os.walk(root_path):
        for file in files:
            stem, ext = os.path.splitext(file)
            if stem.lower() == target_stem.lower():
                if (not target_ext or ext.lower() in VIDEO_EXTS):
                    return os.path.join(root, file)
    return ""

@mcp.tool()
def clip_video(video_path, start=None, end=None,duration = None, output_path=None,time_out=300):
    """
    智能视频剪辑函数
    
    参数：
    video_path : str - 源视频文件路径
    start : int/float/str - 开始时间（支持秒数、MM:SS、HH:MM:SS格式,默认为视频开头,如果不传该参数，或者该参数为负数，从视频结尾往前剪辑）
    end : int/float/str - 结束时间（同上，默认为视频结尾）
    duration:  int/float/str - 裁剪时长，end和duration必须有一个
    output_path: str - 裁剪后视频输出路径，如果不传入，会有一个默认的输出路径
    time_out: int - 命令行执行超时时间，默认为300s
    返回：
    error - 错误码
    str - ffmpeg执行过程中所有日志
    str - 生成的剪辑文件路径
    示例：
    clip_video("input.mp4", "00:01:30", "02:30")
    """
    return cut_video.clip_video_ffmpeg(video_path,start=start,end=end,duration=duration, output_path=output_path,time_out=time_out)   

@mcp.tool()
def concat_videos(input_files: List[str], output_path: str = None, 
                      fast: bool = True):
    """
    使用FFmpeg拼接多个视频文件
    
    参数:
    input_files (List[str]): 输入视频文件路径列表
    output_path (str): 合并后的输出文件路径,如果不传入，会一个默认的输出路径
    fast (bool): 拼接方法，可选值："True"（默认，要求所有视频必须具有相同的编码格式、分辨率、帧率等参数）| "False(当不确定合并的视频编码格式、分辨率、帧率等参数是否相同的情况下，这个参数应该是False)"
    
    返回:
    执行日志
    
    注意:
    1. 当fast=True时，要求所有视频必须具有相同的编码格式、分辨率、帧率等参数
    2. 推荐视频文件使用相同编码参数，避免拼接失败
    3. 输出文件格式由output_path后缀决定（如.mp4/.mkv）
    """
    return cut_video.concat_videos(input_files,output_path,fast)

@mcp.tool()
def get_video_info(video_path: str):
    """
    获取视频信息，包括时长，帧率，codec等
    
    参数:
    video_path (str): 输入视频文件路径
    返回:
    视频详细信息
    """
    return cut_video.get_video_info(video_path)

@mcp.tool()
def play_video(video_path, speed = 1, loop = 1):
    """
    使用 ffplay 播放视频文件，支持mkv,mp4,mov,avi,3gp等等

    参数：
    video_path(str) - 视频文件的路径。
    speed(float) - 浮点型,播放速率,建议0.5-2之间。
    loop(int) - 整形,是否循环播放,1:不循环,播放后就退出,0: 循环播放。
    """
    return cut_video.video_play(video_path,speed=speed,loop=loop)


@mcp.tool()
def overlay_video(background_video, overlay_video, output_path: str = None, position: int = 1,  dx = 0, dy = 0):
    """
    两个视频叠加，注意不是拼接长度，而是画中画效果

    参数：
    background_video(str) - 背景视频文件的路径。
    overlay_video(str) - 前景视频文件路径。
    output_path(str) - 输出路径
    position(enum) - 相对位置，TopLeft=1: 左上角,TopCenter=2: 上居中, TopRight=3: 右上角 RightCenter=4: 右居中 BottomRight=5: 右下角 BottomCenter=6: 下居中 BottomLeft=7: 左下角 LeftCenter=8: 左居中 Center=9: 居中
    dx(int) - 整形,前景视频坐标x偏移值
    dy(int) - 整形,前景视频坐标y偏移值
    """
    return cut_video.overlay_video(background_video, overlay_video, output_path,position, dx, dy)
       
@mcp.tool()   
def scale_video(video_path, width, height,output_path: str = None):
    """
    视频缩放

    参数：
    width(int) - 目标宽度。
    height(int) - 目标高度。
    output_path(str) - 输出路径
    """ 
    return cut_video.scale_video(video_path, width, height, output_path)

@mcp.tool()   
def extract_frames_from_video(video_path,fps=0, output_folder=None, format=0, total_frames=0):
    """
    提取视频中的图像。

    参数：
    video_path(str) - 视频路径。
    fps(int) - 每多少秒抽一帧，如果传0，代表全部都抽,传1，代表每一秒抽1帧。
    output_folder(str) - 把图片输出到哪个目录
    format(int) - 抽取的图片格式，0：代表png 1:jpg 2:webp
    total_frames(int) - 最多抽取多少张，0代表不限制
    """ 
    return cut_video.extract_frames_from_video(video_path, fps, output_folder, format, total_frames)

def main():
    print("Server running")
    mcp.run(transport='stdio')
if __name__ == "__main__":
    main()