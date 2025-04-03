import ffmpeg_mcp.ffmpeg as ffmpeg
import ffmpeg_mcp.utils as utils
import os
from typing import List


def clip_video_ffmpeg(video_path, start = None, end = None, duration=None, output_path = None, time_out = 30):
    """
    智能视频剪辑函数
    
    参数：
    video_path : str - 源视频文件路径
    start : int/float/str - 开始时间（支持秒数、MM:SS、HH:MM:SS格式,默认为视频开头）
    end : int/float/str - 结束时间（同上，默认为视频结尾）
    duration:  int/float/str - 裁剪时长，end和duration必须有一个
    output_path: str - 裁剪后视频输出路径，如果不传入，会有一个默认的输出路径
    time_out: int - 命令行执行超时时间，默认为30s
    返回：
    error - 错误码
    str - ffmpeg执行过程中所有日志
    str - 生成的剪辑文件路径
    示例：
    clip_video("input.mp4", "00:01:30", "02:30")
    """
    try:
        base, ext = os.path.splitext(video_path)
        if (output_path == None):
            output_path = f"{base}_clip{ext}"
        cmd = f"-i {video_path} "
        if (start != None):
            start_sec = utils.convert_to_seconds(start)
            cmd = f"{cmd} -ss {start_sec}"
        if (end == None and duration is not None):
            end = start_sec + utils.convert_to_seconds(duration)
        if (end != None):
            end_sec = utils.convert_to_seconds(end) 
            cmd = f"{cmd} -to {end_sec}"
        cmd = f"{cmd} -y {output_path}"
        print(cmd)
        status_code, log = ffmpeg.run_ffmpeg(cmd, timeout=time_out)
        print(log)
        return {status_code, log, output_path}
    except Exception as e:
        print(f"剪辑失败: {str(e)}")
        return {-1, str(e), ""}
    
    


def concat_videos(input_files: List[str], output_path: str = None, 
                      fast: bool = True):
    """
    使用FFmpeg拼接多个视频文件
    
    参数:
    input_files (List[str]): 输入视频文件路径列表
    output_path (str): 合并后的输出文件路径
    fast (bool): 拼接方法，可选值："True"（默认，要求所有视频必须具有相同的编码格式、分辨率、帧率等参数）| "False(当不确定合并的视频编码格式、分辨率、帧率等参数是否相同的情况下，这个参数应该是False)"
    
    返回:
    None
    
    注意:
    1. 当fast=True时，要求所有视频必须具有相同的编码格式、分辨率、帧率等参数
    2. 推荐视频文件使用相同编码参数，避免拼接失败
    3. 输出文件格式由output_path后缀决定（如.mp4/.mkv）
    """
    if (output_path is None):
        base, ext = os.path.splitext(input_files[0])
        output_path = f"{base}_clip.mp4"
    # 检查输入文件是否存在
    for file in input_files:
        if not os.path.exists(file):
            raise FileNotFoundError(f"输入文件 {file} 不存在")
    if fast == True:
        try:
            # 创建临时文件列表
            temp_list_file = utils.create_temp_file()
            with open(temp_list_file, "w", encoding="utf-8") as f:
                for file in input_files:
                    abs_path = os.path.abspath(file)
                    if os.name == 'nt':
                        f.write(f"file '{abs_path}'\n")
                    else:
                        f.write(f"file '{abs_path}'\n")
            
            # 构建FFmpeg命令
            cmd = f"-f concat -safe 0 -i {temp_list_file} -c copy -y {output_path}"
            return ffmpeg.run_ffmpeg(cmd)
        finally:
            # 清理临时文件
            if os.path.exists(temp_list_file):
                os.remove(temp_list_file)

    elif fast == False:
        inputs = []
        filter_str = ""
        
        # 构建输入参数和滤镜表达式
        for i, file in enumerate(input_files):
            inputs.extend(["-i", file])
            filter_str += f"[{i}:v:0][{i}:a:0]"
        
        filter_str += f"concat=n={len(input_files)}:v=1:a=1[outv][outa]"
        inputs_str = " ".join(inputs)
        cmd = f" {inputs_str} -lavfi '{filter_str}' -map '[outv]' -map '[outa]' -y {output_path}"
        return ffmpeg.run_ffmpeg(cmd)
    

def get_video_info(video_path: str):
    cmd = f" -v error -show_streams -of json -i {video_path}"
    return ffmpeg.run_ffprobe(cmd, timeout=60)
        