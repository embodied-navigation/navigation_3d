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
    openssh-client \
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
    python3-yaml \
    python3-vcstool \
    python3 \
    wget \
    tmux \
    ros-humble-pcl-conversions \
    ros-humble-rviz2 \
    ros-humble-rviz-default-plugins \
    ros-humble-tf2-ros \
    ros-humble-tf2-eigen \
    ros-humble-nav2-costmap-2d \
    ros-humble-nav2-common \
    ros-humble-nav2-msgs \
    ros-humble-nav2-util \
    ros-humble-nav2-voxel-grid \
    && rm -rf /var/lib/apt/lists/*

RUN rosdep init || true

RUN echo "source /opt/ros/humble/setup.bash" >> /etc/bash.bashrc

WORKDIR /workspace
