"""
WeChat Pusher 安装配置
"""
from setuptools import setup, find_packages
from pathlib import Path

# 读取README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# 读取requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = (
    requirements_file.read_text(encoding="utf-8").splitlines()
    if requirements_file.exists()
    else []
)

setup(
    name="wechat-pusher",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="微信公众号AI自动化推送系统",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/wechat-pusher",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "wechat-pusher=src.cli.main:cli",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
