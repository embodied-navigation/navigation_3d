# FROM unitree_ros2_devcontainer-devcontainer-humble:latest
FROM navigation_3d:2026.04.02

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    ros-humble-bondcpp \
    ros-humble-behaviortree-cpp-v3 \
    ros-humble-diagnostic-updater \
    ros-humble-pcl-ros \
    ros-humble-test-msgs \
    ros-humble-nav-2d-utils \
    ros-humble-openvdb-vendor \
    vim \
    tmux \
    htop \
    curl \
    wget \
    less \
    rsync \
    bash-completion \
    iproute2 \
    iputils-ping \
    net-tools \
    usbutils \
    pciutils \
    python3-pip \
    python3-colcon-common-extensions \
    nlohmann-json3-dev \
    libepoxy-dev \
    libgflags-dev \
    libgraphicsmagick++1-dev \
    libgoogle-glog-dev \
    libopencv-dev \
    libpcl-dev \
    libyaml-cpp-dev \
    libpcap-dev \
    pkg-config \
    libmagick++-dev \
    xtensor-dev \
    libceres-dev \
    libompl-dev \
    zip \
 && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y --no-install-recommends \
    ros-humble-sensor-msgs-py \
    python3-numpy \
    libgl1 \
    libgomp1 \
 && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --no-cache-dir \
    numpy==1.24.4 \
    open3d==0.18.0

RUN . /opt/ros/humble/setup.sh && \
    python3 -c "import rclpy, numpy, open3d; from sensor_msgs_py import point_cloud2; print('lidar calibration python deps ok')"

ARG IMAGE_VERSION
LABEL com.navigation_3d.image_version="${IMAGE_VERSION}"
ENV NAVIGATION_3D_IMAGE_VERSION="${IMAGE_VERSION}"