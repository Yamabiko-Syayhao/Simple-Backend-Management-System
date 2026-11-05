# -*- coding: utf-8 -*-
"""项目路径常量"""

from pathlib import Path

# backend/ 根目录
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Alembic 迁移目录
ALEMBIC_VERSION_DIR = BASE_DIR / "app" / "alembic" / "versions"

# 日志目录
LOG_DIR = BASE_DIR / "logs"

# 静态资源
STATIC_DIR = BASE_DIR / "static"

# 上传/下载目录
UPLOAD_DIR = STATIC_DIR / "upload"
DOWNLOAD_DIR = STATIC_DIR / "download"

# 业务文件目录
FILES_DIR = BASE_DIR / "files"

# 环境配置目录
ENV_DIR = BASE_DIR / "env"

# 初始化种子数据目录
SCRIPT_DIR = BASE_DIR / "app" / "scripts" / "data"

# 插件目录
PLUGIN_DIR = BASE_DIR / "app" / "plugin"
