FROM unitree_ros2_devcontainer-devcontainer-humble:latest

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    build-essential \
    ca-certificates \
    clang \
    clang-format \
    clang-tidy \
    cmake \
    git \
    libeigen3-dev \
    libgflags-dev \
    libgoogle-glog-dev \
    libopencv-dev \
    libpcl-dev \
    libyaml-cpp-dev \
    libepoxy-dev \
    libgl1-mesa-dev \
    libglew-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff5-dev \
    libwayland-dev \
    libxkbcommon-dev \
    libx11-dev \
    libxext-dev \
    libxfixes-dev \
    libxi-dev \
    libxinerama-dev \
    libxcursor-dev \
    libxxf86vm-dev \
    pkg-config \
    pcl-tools \
    curl \
    ninja-build \
    python3-colcon-common-extensions \
    python3-pip \
    python3-rosdep \
    python3-vcstool \
    python3 \
    wget \
    ros-humble-pcl-conversions \
    ros-humble-tf2-eigen \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /tmp

COPY src/lightning_lm/thirdparty/Pangolin-0.9.3.zip /tmp/Pangolin-0.9.3.zip

RUN apt-get update && apt-get install -y unzip && rm -rf /var/lib/apt/lists/* \
    && unzip /tmp/Pangolin-0.9.3.zip -d /tmp \
    && cd /tmp/Pangolin-0.9.3 \
    && cmake -B build -S . \
       -DCMAKE_BUILD_TYPE=Release \
       -DCMAKE_INSTALL_PREFIX=/usr/local \
       -DBUILD_PANGOLIN_PYTHON=OFF \
    && cmake --build build -j"$(nproc)" \
    && cmake --install build \
    && echo "/usr/local/lib" > /etc/ld.so.conf.d/pangolin.conf \
    && ldconfig \
    && cd / \
    && rm -rf /tmp/Pangolin-0.9.3 /tmp/Pangolin-0.9.3.zip

RUN rosdep init || true

RUN echo "source /opt/ros/humble/setup.bash" >> /etc/bash.bashrc

WORKDIR /workspace
