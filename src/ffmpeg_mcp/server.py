# server.py
import os
from typing import List
from mcp.server.fastmcp import FastMCP
import ffmpeg_mcp.cut_video as cut_video
# Create an MCP server
mcp = FastMCP("ffmpeg-mcp")

def is_none_or_empty(s):
    return s is None or s == ""

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
    try:
        VIDEO_EXTS = {'.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm', '.ts'}
        target_stem, target_ext = os.path.splitext(video_name)  # 关键修改：提取主文件名
        if target_ext and target_ext.lower() not in VIDEO_EXTS:
            target_stem = f"{target_stem}{target_ext}"
            target_ext = ""
        for entry in os.listdir(root_path):
            current_path = os.path.join(root_path, entry)
            if os.path.isfile(current_path):
                stem, ext = os.path.splitext(entry)
                print(f"--------{stem}")
                if stem.lower() == target_stem.lower():
                    if (is_none_or_empty(target_ext) and is_none_or_empty(ext)):
                        return current_path
                    if (not is_none_or_empty(target_ext) and not is_none_or_empty(ext)):
                        if (ext.lower() == target_ext.lower()):
                            return current_path
                    if (is_none_or_empty(target_ext) and not is_none_or_empty(ext)):
                        if (ext.lower() in VIDEO_EXTS):
                            return current_path
                    if (not is_none_or_empty(target_ext) and is_none_or_empty(ext)):
                        return current_path
                    
            elif os.path.isdir(current_path):
            # 递归搜索子目录
                result = find_video_path(current_path, video_name)
                if result:
                    return result
        return ""
    except Exception as e:
        print(f"find_video_path 发生异常{str(e)}")
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


def main():
    print("Server running")
    mcp.run(transport='stdio')
if __name__ == "__main__":
    main()