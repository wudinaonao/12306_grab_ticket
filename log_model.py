import logging
import config

# 设置当前工作目录
# project_path = "/home/naonao/Documents/PythonItem/virgin"
# os.chdir(project_path)
# 创建实例
logger = logging.getLogger()
# 设置日志记录等级
logger.setLevel(logging.INFO)
# 日志文件
# LOG_FILE = "run.log"
# 设置日志文件处理器
fh = logging.FileHandler(config.LOG_FILE, mode="a", encoding="utf-8")
# 设置日志输出到屏幕处理器
ch = logging.StreamHandler()
# 设置日志格式
formatter = logging.Formatter("[%(asctime)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
# 设置日志文件的格式
fh.setFormatter(formatter)
# 设置输出到屏幕的日志格式
ch.setFormatter(formatter)
# 增加日志处理器到logger
logger.addHandler(fh)
logger.addHandler(ch)