#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理模块
负责加载和管理YAML配置文件
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any


class Config:
    """配置管理器"""

    def __init__(self, config_path: str = None):
        """
        初始化配置

        Args:
            config_path: 配置文件路径，默认为config/default.yaml
        """
        if config_path is None:
            # 默认配置文件路径
            script_dir = Path(__file__).parent.parent.parent
            config_path = script_dir / 'config' / 'default.yaml'

        self.config_path = Path(config_path)
        self.config = self._load_config()
        self._expand_env_vars()

    def _load_config(self) -> Dict[str, Any]:
        """加载YAML配置文件"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")

        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        return config

    def _expand_env_vars(self):
        """展开环境变量（${VAR}）"""
        def expand_value(value):
            if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
                env_var = value[2:-1]
                return os.getenv(env_var, value)
            return value

        def expand_dict(d):
            for key, value in d.items():
                if isinstance(value, dict):
                    expand_dict(value)
                elif isinstance(value, str):
                    d[key] = expand_value(value)
                elif isinstance(value, list):
                    d[key] = [expand_value(v) if isinstance(v, str) else v for v in value]

        expand_dict(self.config)

    def get(self, key_path: str, default=None):
        """
        获取配置值（支持嵌套路径）

        Args:
            key_path: 配置路径，如 'models.glm.api_url'
            default: 默认值

        Returns:
            配置值
        """
        keys = key_path.split('.')
        value = self.config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def get_model_config(self, model_name: str) -> Dict[str, Any]:
        """
        获取模型配置

        Args:
            model_name: 模型名称（glm, deepseek）

        Returns:
            模型配置字典
        """
        return self.config.get('models', {}).get(model_name, {})

    def get_processing_config(self, converter_type: str) -> Dict[str, Any]:
        """
        获取处理配置

        Args:
            converter_type: 转换器类型（pdf, docx）

        Returns:
            处理配置字典
        """
        return self.config.get('processing', {}).get(converter_type, {})

    def get_output_config(self) -> Dict[str, Any]:
        """获取输出配置"""
        return self.config.get('output', {})

    def get_prompt(self, prompt_name: str) -> str:
        """
        获取提示词模板

        Args:
            prompt_name: 提示词名称（ocr, image_description, semantic_matching等）

        Returns:
            提示词字符串
        """
        prompts = self.config.get('prompts', {})
        return prompts.get(prompt_name, '')
