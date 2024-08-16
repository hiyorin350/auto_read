# ベースイメージを設定
FROM node:14-slim

# 作業ディレクトリを設定
WORKDIR /app

# 必要なツールをインストール
RUN apt-get update && apt-get install -y \
    wget \
    build-essential \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    libffi-dev \
    libncurses5-dev \
    libgdbm-dev \
    tk-dev \
    libnss3-dev \
    liblzma-dev \
    uuid-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libgtk2.0-dev \
    libatlas-base-dev \
    gfortran \
    openmpi-bin \
    libopenmpi-dev \
    tesseract-ocr \
    git

# Python 3.8をソースからビルド
RUN wget https://www.python.org/ftp/python/3.8.10/Python-3.8.10.tgz && \
    tar xzf Python-3.8.10.tgz && \
    cd Python-3.8.10 && \
    ./configure --enable-optimizations && \
    make -j$(nproc) && \
    make install && \
    cd .. && \
    rm -rf Python-3.8.10 Python-3.8.10.tgz

# Pythonパッケージ管理ツールpipをアップグレード
RUN python3.8 -m ensurepip --upgrade && \
    python3.8 -m pip install --upgrade pip

# opencv-python-headlessのインストール
RUN python3.8 -m pip install opencv-python-headless

# Node.jsの依存関係をインストール
COPY package*.json ./
RUN npm install

# Pythonの依存関係をインストール
COPY requirements.txt ./
RUN python3.8 -m pip install --default-timeout=1000 -r requirements.txt

# アプリケーションのソースをコピー
COPY . .

# 必要なディレクトリを作成
RUN mkdir -p uploads

# コンテナ起動時のコマンドを設定
CMD ["node", "app.js"]
