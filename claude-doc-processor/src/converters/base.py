"""
转换器基类

定义所有转换器的通用接口和公共方法
"""

import os
import json
import logging
import time
from typing import Dict, Tuple, Optional
from datetime import datetime
import yaml


class BaseConverter:
    """转换器基类"""

    def __init__(self, config_path: Optional[str] = None):
        """
        初始化转换器

        Args:
            config_path: 配置文件路径（可选，默认使用config/default.yaml）
        """
        # 加载配置
        self.config = self._load_config(config_path)

        # 初始化日志
        self._setup_logging()

        # 初始化统计信息
        self.stats = {
            'start_time': None,
            'end_time': None,
            'processing_time': 0,
            'input_file': None,
            'output_file': None,
            'total_images': 0,
            'matched_images': 0,
            'stages_completed': []
        }

    # ========================================
    # 抽象方法（子类必须实现）
    # ========================================

    def convert(
        self,
        input_path: str,
        output_dir: str,
        **kwargs
    ) -> Tuple[bool, str, Dict]:
        """
        执行转换

        Args:
            input_path: 输入文件路径
            output_dir: 输出目录
            **kwargs: 额外参数

        Returns:
            (成功状态, 输出文件路径, 统计信息字典)
        """
        raise NotImplementedError("子类必须实现convert()方法")

    # ========================================
    # 公共方法
    # ========================================

    def _load_config(self, config_path: Optional[str] = None) -> Dict:
        """
        加载配置文件

        Args:
            config_path: 配置文件路径

        Returns:
            配置字典
        """
        if config_path is None:
            # 默认配置文件路径
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            config_path = os.path.join(project_root, 'config', 'default.yaml')

        if not os.path.exists(config_path):
            logging.warning(f"配置文件不存在: {config_path}，使用默认配置")
            return self._get_default_config()

        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        # 扩展环境变量
        config = self._expand_env_vars(config)

        return config

    def _get_default_config(self) -> Dict:
        """获取默认配置"""
        return {
            'models': {
                'glm': {
                    'api_url': 'http://localhost:9999',
                    'model': 'zai-org/glm-4.6v-flash',
                    'max_tokens': 8192,
                    'timeout': 60,
                    'temperature': 0.3
                },
                'deepseek': {
                    'api_key': '',
                    'model': 'deepseek-chat',
                    'timeout': 120,
                    'temperature': 0.1,
                    'max_tokens': 4000
                }
            },
            'processing': {
                'pdf': {
                    'dpi': 200,
                    'max_pages': None,
                    'opencv_min_area': 0.02,
                    'opencv_padding': 10,
                    'enable_formatting': False
                },
                'docx': {
                    'libreoffice_timeout': 60,
                    'image_max_size': 1280,
                    'document_chunk_size': 64000,
                    'image_quality': 85
                }
            },
            'output': {
                'default_dir': 'output',
                'save_intermediate': True,
                'log_level': 'INFO'
            },
            'image_extraction': {
                'method': 'auto',
                'min_width': 50,
                'min_height': 50
            }
        }

    def _expand_env_vars(self, config: Dict) -> Dict:
        """
        扩展配置中的环境变量

        Args:
            config: 配置字典

        Returns:
            扩展后的配置字典
        """
        def expand_value(value):
            if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
                env_var = value[2:-1]
                return os.environ.get(env_var, '')
            elif isinstance(value, dict):
                return {k: expand_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [expand_value(item) for item in value]
            return value

        return expand_value(config)

    def _setup_logging(self):
        """设置日志系统"""
        log_level = self.config.get('output', {}).get('log_level', 'INFO')
        log_format = self.config.get('output', {}).get(
            'log_format',
            '%(asctime)s - %(levelname)s - %(message)s'
        )

        logging.basicConfig(
            level=getattr(logging, log_level),
            format=log_format,
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        self.logger = logging.getLogger(self.__class__.__name__)

    def _save_metadata(self, output_dir: str, stats: Dict):
        """
        保存元数据到meta.json

        Args:
            output_dir: 输出目录
            stats: 统计信息字典
        """
        metadata = {
            'converter': self.__class__.__name__,
            'timestamp': datetime.now().isoformat(),
            'processing_time_seconds': stats.get('processing_time', 0),
            'input_file': stats.get('input_file'),
            'output_file': stats.get('output_file'),
            'statistics': {
                'total_images': stats.get('total_images', 0),
                'matched_images': stats.get('matched_images', 0),
                'stages_completed': stats.get('stages_completed', [])
            }
        }

        metadata_path = os.path.join(output_dir, 'meta.json')
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        self.logger.info(f"💾 元数据已保存: {metadata_path}")

    def _log_stats(self, stats: Dict):
        """
        输出统计信息

        Args:
            stats: 统计信息字典
        """
        self.logger.info("")
        self.logger.info("=" * 60)
        self.logger.info("转换统计")
        self.logger.info("=" * 60)
        self.logger.info(f"  输入文件: {stats.get('input_file', 'N/A')}")
        self.logger.info(f"  输出文件: {stats.get('output_file', 'N/A')}")
        self.logger.info(f"  处理时间: {stats.get('processing_time', 0):.2f} 秒")
        self.logger.info(f"  总图片数: {stats.get('total_images', 0)}")
        self.logger.info(f"  匹配成功: {stats.get('matched_images', 0)}")
        self.logger.info(f"  完成阶段: {len(stats.get('stages_completed', []))} 个")
        self.logger.info("=" * 60)

    def _start_timer(self):
        """开始计时"""
        self.stats['start_time'] = time.time()

    def _stop_timer(self):
        """停止计时"""
        if self.stats['start_time']:
            self.stats['end_time'] = time.time()
            self.stats['processing_time'] = self.stats['end_time'] - self.stats['start_time']

    def _validate_input_file(self, input_path: str, expected_extensions: list) -> bool:
        """
        验证输入文件

        Args:
            input_path: 输入文件路径
            expected_extensions: 期望的扩展名列表（如 ['.pdf', '.PDF']）

        Returns:
            是否有效
        """
        if not os.path.exists(input_path):
            self.logger.error(f"❌ 文件不存在: {input_path}")
            return False

        ext = os.path.splitext(input_path)[1].lower()
        if ext not in [e.lower() for e in expected_extensions]:
            self.logger.error(f"❌ 不支持的文件类型: {ext}，期望: {expected_extensions}")
            return False

        return True

    def _create_output_dir(self, output_dir: str) -> bool:
        """
        创建输出目录

        Args:
            output_dir: 输出目录路径

        Returns:
            是否成功
        """
        try:
            os.makedirs(output_dir, exist_ok=True)
            return True
        except Exception as e:
            self.logger.error(f"❌ 创建输出目录失败: {e}")
            return False

    def _get_output_filename(self, input_path: str, output_dir: str) -> str:
        """
        生成输出文件名

        Args:
            input_path: 输入文件路径
            output_dir: 输出目录

        Returns:
            输出文件完整路径
        """
        basename = os.path.splitext(os.path.basename(input_path))[0]
        return os.path.join(output_dir, f'{basename}.md')
