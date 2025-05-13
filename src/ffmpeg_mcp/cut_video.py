import ffmpeg_mcp.ffmpeg as ffmpeg
import ffmpeg_mcp.utils as utils
import os
from typing import List
from enum import Enum

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
        fmt_ctx = ffmpeg.media_format_ctx(input_files[0])
        if fmt_ctx is None:
            return -1, f"{input_files[0]} 视频解析失败！！"
        map = ""
        if len(fmt_ctx.video_streams) > 0: ## 视频+音频
            width = fmt_ctx.video_streams[0].width
            height = fmt_ctx.video_streams[0].height
            aspect = float(width)/float(height)
            for i, file in enumerate(input_files):
                inputs.extend(["-i", file])
                if i == 0:
                    filter_str += f"[{i}:v]setsar=1[{i}v];"
                if i > 0:
                    tmp_fmt_ctx = ffmpeg.media_format_ctx(file)
                    if (tmp_fmt_ctx is None):
                        return -1, f"{input_files[i]} 视频解析失败！！"
                    if len(tmp_fmt_ctx.video_streams) == 0:
                        return -1, f"{input_files[i]} 不包含视频流！！"
                    tmp_width = tmp_fmt_ctx.video_streams[0].width
                    tmp_height = tmp_fmt_ctx.video_streams[0].height
                    tmp_aspect = float(tmp_width)/float(tmp_height) 
                    if tmp_width == width and tmp_height == height:
                        filter_str += f"[{i}:v]setsar=1[{i}v];"
                    elif tmp_aspect == aspect:
                        filter_str += f"[{i}:v]scale={width}:{height},setsar=1[{i}v];"
                    elif abs(tmp_aspect-aspect) < 0.15: #使用increase
                        filter_str += f"[{i}:v]scale={width}:{height}:force_original_aspect_ratio=increase,setsar=1,crop=x=(iw-{width})/2:y=({height}-ih)/2:w={width}:h={height},setsar=1[{i}v];"
                    else:
                        filter_str += f"[{i}:v]scale={width}:{height}:force_original_aspect_ratio=decrease,setsar=1,pad={width}:{height}:({width}-iw)/2:({height}-ih)/2,setsar=1[{i}v];"  
            for i, file in enumerate(input_files):
                if len(fmt_ctx.audio_streams) > 0:
                    filter_str += f"[{i}v][{i}:a]"
                else:
                    filter_str += f"[{i}v]"
            a = 0
            map = " -map '[outv]' "
            out = "[outv]"
            if len(fmt_ctx.audio_streams) > 0:
                a = 1
                map = " -map '[outv]' -map '[outa]' "
                out = "[outv][outa]"
            filter_str += f"concat=n={len(input_files)}:v=1:a={a}{out}"
        elif len(fmt_ctx.audio_streams) > 0: # 音频
            for i, file in enumerate(input_files):
                inputs.extend(["-i", file])
                filter_str += f"[{i}:a]"
            filter_str += f"concat=n={len(input_files)}:a=1:v=0[outa]"
            map = " -map '[outa]' "
            
        if len(filter_str) == 0:
            return -1, f"{input_files[0]} 视频中不包含任何音视频流！！"
        # 构建输入参数和滤镜表达式
        inputs_str = " ".join(inputs)
        cmd = f" {inputs_str} -lavfi '{filter_str}' {map} -y {output_path}"
        return ffmpeg.run_ffmpeg(cmd)
    

def get_video_info(video_path: str):
    cmd = f" -v error -show_streams -of json -i {video_path}"
    return ffmpeg.run_ffprobe(cmd, timeout=60)
        
        
        
def video_play(video_path: str, speed, loop):
    speed = float(speed)
    loop = int(loop)
    cmd = f" -loop {loop} "
    if loop != 0:
        cmd = f" {cmd} -autoexit"
    audio_filter_str = ""
    video_filter_str = ""
    if (speed != 1):
        fmt_ctx = ffmpeg.media_format_ctx(video_path)
        if len(fmt_ctx.audio_streams) > 0:
            audio_filter_str = f"-af atempo={speed}"
        if len(fmt_ctx.video_streams) > 0:
            video_filter_str = f"-vf setpts={1/speed}*PTS"
    cmd = f" {cmd } {audio_filter_str} {video_filter_str}   -i {video_path}"
    print(cmd)
    return ffmpeg.run_ffplay(cmd, timeout=60)
        
     
class Position(Enum):
    TopLeft = 1,
    TopCenter = 2,
    TopRight = 3,
    RightCenter = 4,
    BottomRight = 5,
    BottomCenter = 6,
    BottomLeft = 7,
    LeftCenter = 8,
    Center = 9
           
def overlay_video(background_video, overlay_video, output_path: str = None, position: int = 1,  dx = 0, dy = 0):
    """
    两个视频叠加，注意不是拼接长度，而是画中画效果

    参数：
    background_video(str) - 背景视频文件的路径。
    overlay_video(str) - 前景视频文件路径。
    output_path(str) - 输出路径
    position(enum) - 相对位置，TopLeft: 左上角,TopCenter: 上居中, TopRight: 右上角 RightCenter: 右居中 BottomRight: 右下角 BottomCenter: 下居中 BottomLeft: 左下角 LeftCenter: 左居中 Center: 居中
    dx(int) - 整形,前景视频坐标x值
    dy(int) - 整形,前景视频坐标y值
    """
    try:
        base, ext = os.path.splitext(background_video)
        if (output_path == None):
            if (ext == None or len(ext) == 0):
                ext = ".mp4"
            output_path = f"{base}_clip{ext}"
        x = ""
        y = ""
        if position == 1:
            x = f"{dx}"
            y = f"{dy}"
        elif position == Position.LeftCenter:
             x = f"{dx}"
             y = f"(H-h)/2+{dy}"
        elif position == 7:
            x = f"{dx}"
            y = f"(H-h)+{dy}"
        elif position == 6:
            x = f"(W-w)/2+{dx}"
            y = f"(H-h)+{dy}"
        elif position == 5:
            x = f"(W-w)+{dx}"
            y = f"(H-h)+{dy}"    
        elif position == 4:
            x = f"(W-w)+{dx}"
            y = f"(H-h)/2+{dy}"    
        elif position == 3:
            x = f"(W-w)+{dx}"
            y = f"{dy}"   
        elif position == 2:
            x = f"(W-w)/2+{dx}"
            y = f"{dy}"   
        elif position == 9:
            x = f"(W-w)/2+{dx}"
            y = f"(H-h)/2+{dy}"   
            
        cmd = f" -i {background_video} -i {overlay_video} -filter_complex \"[0:v][1:v]overlay=x={x}:y={y}[ov];[0:a][1:a]amix=inputs=2:weights='3 1'[oa]\" -map '[ov]' -map '[oa]'"
        cmd = f"{cmd} -y {output_path}"
        print(cmd)
        status_code, log = ffmpeg.run_ffmpeg(cmd, timeout=1000)
        print(log)
        return {status_code, log, output_path}
    except Exception as e:
        print(f"剪辑失败: {str(e)}")
        return {-1, str(e), ""}
    
    
def scale_video(video_path, width, height = -2,output_path: str = None):
    """
    视频缩放

    参数：
    width(int) - 目标宽度， 如果是-2,代表保持宽高比，且是2的倍数。
    height(int) - 目标高度，如果是-2,代表保持宽高比，且是2的倍数。
    output_path(str) - 输出路径
    """
    try:
        base, ext = os.path.splitext(video_path)
        if (output_path == None):
            if (ext == None or len(ext) == 0):
                ext = ".mp4"
            output_path = f"{base}_clip{ext}"
    
        cmd = f" -i {video_path} -filter_complex \"scale={width}:{height}\""
        cmd = f"{cmd} -y {output_path}"
        print(cmd)
        status_code, log = ffmpeg.run_ffmpeg(cmd, timeout=1000)
        print(log)
        return {status_code, log, output_path}
    except Exception as e:
        print(f"剪辑失败: {str(e)}")
        return {-1, str(e), ""}
    

def extract_frames_from_video(video_path,fps=0, output_folder=None, format=0, total_frames=0):
    """
    使用 FFmpeg 提取视频中的每一帧图像。

    :param video_path: 视频文件的路径。
    :param fps: 每多少秒抽一帧，如果传0，代表每一帧都抽
    :param output_folder: 输出图像的文件夹路径。
    :param format: 输出图像的图片格式 0：png 1:jpg 2:webp。
    """
    # 确保输出文件夹存在
    if output_folder == None:
          output_folder = os.path.dirname(video_path)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    img_ext = "png"
    if (format == 0):
        img_ext = "png"
    elif (format == 1):
        img_ext = "jpg"
    else:
        img_ext = "webp"
    output_path = os.path.join(output_folder, f'frame_%04d.{img_ext}')
    try:
        cmd = f" -i {video_path}"
        # 执行 FFmpeg 命令
        if fps > 0:
            cmd = f" {cmd} -vf 'fps=1/{fps}'"
        else:
            cmd = f" {cmd} -vsync 0"
        if (total_frames > 0):
            cmd = f" {cmd} -vframes {total_frames} "
        cmd = f" {cmd} -y {output_path}"
        status_code, log = ffmpeg.run_ffmpeg(cmd, timeout=1000)
        print(log)
        return {status_code, log, output_path}
    except Exception as e:
        print(f"抽取失败: {str(e)}")
        return {-1, str(e), ""}
