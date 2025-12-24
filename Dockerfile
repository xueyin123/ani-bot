# 使用官方Python运行时作为基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 创建数据和日志目录
RUN mkdir -p /app/data /app/logs /app/downloads

# 设置环境变量
ENV PYTHONPATH=/app

# 暴露端口（如果需要Web界面的话）
EXPOSE 5000

# 运行应用
CMD ["python", "app/main.py"]