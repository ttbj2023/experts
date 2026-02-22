"""
日志工具模块
提供统一的日志记录功能，支持彩色输出和文件日志
"""
import logging
import sys
from pathlib import Path
from typing import Optional

try:
    import colorlog

    HAS_COLORLOG = True
except ImportError:
    HAS_COLORLOG = False

from src.utils.config import config


class Logger:
    """日志管理器"""

    _loggers: dict = {}

    @classmethod
    def get_logger(cls, name: str = "wechat_pusher") -> logging.Logger:
        """
        获取日志记录器

        Args:
            name: 日志记录器名称

        Returns:
            logging.Logger: 配置好的日志记录器
        """
        if name in cls._loggers:
            return cls._loggers[name]

        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, config.app.log_level))

        # 清除已有的处理器
        logger.handlers.clear()

        # 控制台处理器
        console_handler = cls._create_console_handler()
        logger.addHandler(console_handler)

        # 文件处理器
        file_handler = cls._create_file_handler()
        logger.addHandler(file_handler)

        cls._loggers[name] = logger
        return logger

    @classmethod
    def _create_console_handler(cls) -> logging.Handler:
        """创建控制台日志处理器"""
        if config.app.log_color and HAS_COLORLOG:
            # 使用彩色日志
            handler = colorlog.StreamHandler(sys.stdout)
            handler.setFormatter(
                colorlog.ColoredFormatter(
                    "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                    log_colors={
                        "DEBUG": "cyan",
                        "INFO": "green",
                        "WARNING": "yellow",
                        "ERROR": "red",
                        "CRITICAL": "red,bg_white",
                    },
                )
            )
        else:
            # 普通日志
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                )
            )

        handler.setLevel(getattr(logging, config.app.log_level))
        return handler

    @classmethod
    def _create_file_handler(cls) -> logging.Handler:
        """创建文件日志处理器"""
        log_file = Path(config.app.log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)

        handler = logging.FileHandler(log_file, encoding="utf-8")
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        handler.setLevel(logging.DEBUG)  # 文件日志记录所有级别
        return handler

    @classmethod
    def set_level(cls, level: str):
        """
        动态设置日志级别

        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        log_level = getattr(logging, level.upper())
        for logger in cls._loggers.values():
            logger.setLevel(log_level)
            for handler in logger.handlers:
                if isinstance(handler, logging.StreamHandler) and not isinstance(
                    handler, logging.FileHandler
                ):
                    handler.setLevel(log_level)


# 默认日志记录器
logger = Logger.get_logger(__name__)


def setup_logging(level: Optional[str] = None):
    """
    设置全局日志级别

    Args:
        level: 日志级别，如果不指定则使用配置文件中的设置
    """
    if level:
        Logger.set_level(level)


def get_logger(name: str = "wechat_pusher") -> logging.Logger:
    """
    获取日志记录器的便捷函数

    Args:
        name: 日志记录器名称

    Returns:
        logging.Logger: 配置好的日志记录器
    """
    return Logger.get_logger(name)
