"""
图表生成器
使用Matplotlib生成数据可视化图表
"""
import matplotlib
from pathlib import Path
from typing import Dict, Optional
import matplotlib.pyplot as plt
import numpy as np

from src.utils.config import config
from src.utils.logger import get_logger

# 设置中文字体支持
matplotlib.use("Agg")  # 使用非交互式后端
# 配置中文字体（按优先级排序，自动降级到可用的字体）
plt.rcParams["font.sans-serif"] = [
    "WenQuanYi Micro Hei",    # 文泉驿微米黑（推荐，现代清晰）
    "Noto Sans CJK SC",       # Noto Sans CJK 简体中文
    "Noto Sans CJK JP",       # Noto Sans CJK 日文版（备用）
    "WenQuanYi Zen Hei",      # 文泉驿正黑（备用）
    "DejaVu Sans"             # 最后备用（不支持中文）
]
plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题

logger = get_logger(__name__)


class ChartGenerator:
    """图表生成器"""

    def __init__(self):
        """初始化图表生成器"""
        self.dpi = config.chart.dpi
        self.figure_width = config.chart.figure_width
        self.figure_height = config.chart.figure_height
        logger.info("图表生成器初始化完成")

    def generate_chart(
        self,
        chart_data: Dict,
        save_path: Optional[str] = None,
    ) -> Optional[str]:
        """
        根据数据生成图表

        Args:
            chart_data: 图表数据，包含type、title、data等
            save_path: 保存路径（可选）

        Returns:
            str: 图片保存路径，失败返回None
        """
        try:
            chart_type = chart_data.get("chart_type", "bar")

            logger.info(f"开始生成{chart_type}图表: {chart_data.get('title', '')}")

            # 根据图表类型调用对应的生成方法
            if chart_type == "bar":
                return self._generate_bar_chart(chart_data, save_path)
            elif chart_type == "line":
                return self._generate_line_chart(chart_data, save_path)
            elif chart_type == "pie":
                return self._generate_pie_chart(chart_data, save_path)
            else:
                logger.warning(f"不支持的图表类型: {chart_type}")
                return None

        except Exception as e:
            logger.error(f"图表生成失败: {e}")
            return None

    def _generate_bar_chart(
        self, data: Dict, save_path: Optional[str] = None
    ) -> str:
        """生成柱状图"""
        fig, ax = plt.subplots(figsize=(self.figure_width, self.figure_height))

        labels = data.get("data", {}).get("labels", [])
        values = data.get("data", {}).get("values", [])
        xlabel = data.get("data", {}).get("xlabel", "")
        ylabel = data.get("data", {}).get("ylabel", "")
        title = data.get("title", "")

        # 绘制柱状图
        x = np.arange(len(labels))
        bars = ax.bar(x, values, color="#1890ff", alpha=0.8)

        # 设置标签和标题
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.set_title(title, fontsize=14, fontweight="bold")
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=45, ha="right")

        # 添加数值标签
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                height,
                f"{height:.0f}",
                ha="center",
                va="bottom",
                fontsize=10,
            )

        plt.tight_layout()

        return self._save_chart(fig, save_path or "bar_chart")

    def _generate_line_chart(
        self, data: Dict, save_path: Optional[str] = None
    ) -> str:
        """生成折线图"""
        fig, ax = plt.subplots(figsize=(self.figure_width, self.figure_height))

        labels = data.get("data", {}).get("labels", [])
        values = data.get("data", {}).get("values", [])
        xlabel = data.get("data", {}).get("xlabel", "")
        ylabel = data.get("data", {}).get("ylabel", "")
        title = data.get("title", "")

        # 绘制折线图
        x = np.arange(len(labels))
        line = ax.plot(x, values, color="#1890ff", linewidth=2, marker="o", markersize=8)

        # 填充区域
        ax.fill_between(x, values, alpha=0.3, color="#1890ff")

        # 设置标签和标题
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.set_title(title, fontsize=14, fontweight="bold")
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=45, ha="right")

        # 添加网格
        ax.grid(True, linestyle="--", alpha=0.6)

        plt.tight_layout()

        return self._save_chart(fig, save_path or "line_chart")

    def _generate_pie_chart(
        self, data: Dict, save_path: Optional[str] = None
    ) -> str:
        """生成饼图"""
        fig, ax = plt.subplots(figsize=(self.figure_width, self.figure_height))

        labels = data.get("data", {}).get("labels", [])
        values = data.get("data", {}).get("values", [])
        title = data.get("title", "")

        # 配色方案
        colors = ["#1890ff", "#52c41a", "#faad14", "#f5222d", "#722ed1", "#13c2c2"]

        # 绘制饼图
        wedges, texts, autotexts = ax.pie(
            values,
            labels=labels,
            autopct="%1.1f%%",
            colors=colors[: len(labels)],
            startangle=90,
        )

        # 设置字体大小
        for text in texts:
            text.set_fontsize(11)
        for autotext in autotexts:
            autotext.set_fontsize(10)
            autotext.set_color("white")

        ax.set_title(title, fontsize=14, fontweight="bold", pad=20)

        plt.tight_layout()

        return self._save_chart(fig, save_path or "pie_chart")

    def _save_chart(self, fig, save_path: str) -> str:
        """
        保存图表

        Args:
            fig: matplotlib图表对象
            save_path: 保存路径

        Returns:
            str: 实际保存路径
        """
        # 如果没有指定保存路径，使用默认路径
        if not save_path.endswith(".png"):
            output_dir = Path(config.app.output_dir) / "charts"
            output_dir.mkdir(parents=True, exist_ok=True)
            save_path = str(output_dir / f"{save_path}_{id(fig)}.png")

        # 保存图表
        fig.savefig(save_path, dpi=self.dpi, bbox_inches="tight", facecolor="white")
        plt.close(fig)

        logger.info(f"图表已保存: {save_path}")
        return save_path


# 创建全局实例
chart_generator = ChartGenerator()
