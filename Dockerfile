# 使用官方 Python 3 运行时作为基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY update_security_group.py .

# 设置脚本为可执行
RUN chmod +x update_security_group.py

# 设置入口点
ENTRYPOINT ["python", "update_security_group.py"]

# 默认命令（可以通过 docker run 覆盖）
CMD ["--help"]

