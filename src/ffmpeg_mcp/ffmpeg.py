import subprocess
import shlex
import sys
import threading
import os
import platform
import ffmpeg_mcp.utils as utils
import ffmpeg_mcp.typedef as typedef
def check_os_architecture():
    # 获取当前操作系统
    system = platform.system()
    # 获取处理器架构
    machine = platform.machine()
    return system, machine
        
def run_command(command, timeout=300):
    """
    运行FFmpeg命令并捕获相关信息。

    参数:
        command (str): 要执行的FFmpeg命令行字符串。
        timeout (int): 命令执行的超时时间（以秒为单位），默认300秒。

    返回:
        tuple: 包含以下元素的元组：
            - return_code (int): 命令执行后的返回状态码。
            - output_log (str): 命令执行过程中的标准输出日志。
    """
    logs = []
    return_code = 0
    append_msg = ""
    def read_output(proc):
        try:
            while True:
                line = proc.stdout.readline()
                if not line and proc.poll() is not None:
                    break
                if line:
                    logs.append(line)
        except ValueError:
            # 处理文件关闭时的异常
            pass
    try:
        # 使用subprocess.run执行FFmpeg命令
        args = shlex.split(command, posix=(sys.platform != 'win32'))
        proc = subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1,
            encoding='utf-8',
            errors='replace'
        )
        thread = threading.Thread(target=read_output, args=(proc,))
        thread.start()
        return_code = proc.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        print("command timed out")
        return_code = -1
        append_msg = "Timeout expired"
    except Exception as e:
        return_code = -1
        append_msg = f"An error occurred: {e}"
        # 捕获所有其他异常
    finally:
        # 确保清理资源
        if 'proc' in globals() and proc and proc.poll() is None:  # 如果进程仍在运行
            proc.kill()
        if 'thread' in globals() and thread:
            thread.join()  #
        logs.append(append_msg)
        return return_code, '\n'.join(logs), append_msg
    
def is_file_and_exists(file_path):
    return os.path.isfile(file_path) and os.path.exists(file_path)

def command_dir():
    system,machine = check_os_architecture()
    current_work_dir = os.path.dirname(__file__)
    os.chdir(f"{current_work_dir}/bin")
    if system == "Darwin":
        if machine == "x86_64":
            dir = f"{current_work_dir}/bin/ffmpeg-macos-x86_64"
            url = "https://gitee.com/littlecodergitxxx/ffmpeg-macos-x86_64.git"
        if machine == "arm64":
            dir = f"{current_work_dir}/bin/ffmpeg-macos-arm64"
            url = "https://gitee.com/littlecodergitxxx/ffmpeg-macos-arm64.git"
        if not is_file_and_exists(f"{dir}/ffmpeg"):
            cmd = f"rm -rf {dir}"
            code,_,_ = run_command(cmd)
            cmd = f"git clone {url}"
            code,_,_ = run_command(cmd)
            if code == 0:
                os.chdir(dir)
            else:
                return None
            cmd = f"git checkout v0.1"
            code,_,_= run_command(cmd)
            if code == 0:
                utils.unzip_to_current_directory(f"ffmpeg.zip")
            else:
                return None
            cmd = f"chmod 777 {dir}/ffmpeg"
            code,_,_= run_command(cmd)
            cmd = f"chmod 777 {dir}/ffprobe"
            code,_,_= run_command(cmd)
            cmd = f"chmod 777 {dir}/ffplay"
            code,_,_= run_command(cmd)
        return dir
    return None

def run_ffmpeg(cmd, timeout=300):
    cmd_dir = command_dir()
    if cmd_dir is None:
        return -1, "Not Support Platform"
    cmd = f"{cmd_dir}/ffmpeg {cmd}"
    logs = []
    logs.append(cmd)
    code, log, append_msg = run_command(cmd,timeout)
    logs.append(log)
    logs.append(append_msg)
    return code, '\n'.join(logs)

def run_ffprobe(cmd, timeout = 60):
    cmd_dir = command_dir()
    if cmd_dir is None:
        return -1, "Not Support Platform"
    cmd = f"{cmd_dir}/ffprobe {cmd}"
    code, log, append_msg = run_command(cmd,timeout)
    logs = []
    if (code != 0):
        logs.append(cmd)
        logs.append(log)
        logs.append(append_msg)
        return code,cmd,'\n'.join(logs)
    return code, cmd, log

def run_ffplay(cmd, timeout = 60):
    cmd_dir = command_dir()
    if cmd_dir is None:
        return -1, "Not Support Platform"
    cmd = f"{cmd_dir}/ffplay {cmd}"
    code, log, append_msg = run_command(cmd,timeout)
    logs = []
    if (code != 0):
        logs.append(cmd)
        logs.append(log)
        logs.append(append_msg)
        return code,cmd,'\n'.join(logs)
    return code, cmd, log
    
def media_format_ctx(path):
    cmd = f" -show_streams -of json -v error -i {path}"
    code, cmd, log = run_ffprobe(cmd)
    if (code == 0):
        return typedef.FormatContext(log)
    return None