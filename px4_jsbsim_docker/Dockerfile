
#
# Custom PX4 JSBSim V1.1 development and validation environment in Ubuntu 20.04 Focal
#

FROM px4io/px4-dev-base-focal:2020-06-28


RUN wget --quiet http://packages.osrfoundation.org/gazebo.key -O - | apt-key add - \
	&& sh -c 'echo "deb http://packages.osrfoundation.org/gazebo/ubuntu-stable `lsb_release -sc` main" > /etc/apt/sources.list.d/gazebo-stable.list' \
	&& apt-get update \
	&& DEBIAN_FRONTEND=noninteractive apt-get -y --quiet --no-install-recommends install \
		ant \
		binutils \
		bc \
		dirmngr \
		gazebo11 \
		gstreamer1.0-plugins-bad \
		gstreamer1.0-plugins-base \
		gstreamer1.0-plugins-good \
		gstreamer1.0-plugins-ugly \
		libeigen3-dev \
		libgazebo11-dev \
		libgstreamer-plugins-base1.0-dev \
		libimage-exiftool-perl \
		libopencv-dev \
		libxml2-utils \
		mesa-utils \
		protobuf-compiler \
		x-window-system \
		apt-utils \
		build-essential \
		ca-certificates \
		ccache \
		cmake \
		cppcheck \
		doxygen \
		curl \
		dirmngr \
		file \
		cxxtest \
		gcc \
		gdb \
		lsb-release \
		make \
		openssh-client \
		pkg-config \
		python3-pip \
		sudo \
		unzip \
		zip \
	&& apt-get -y autoremove \
	&& apt-get clean autoclean \
	&& rm -rf /var/lib/apt/lists/{apt,dpkg,cache,log} /tmp/* /var/tmp/*

# install MAVLink headers
RUN git clone --depth 1 https://github.com/mavlink/c_library_v2.git /usr/local/include/mavlink/v2.0 && rm -rf /usr/local/include/mavlink/v2.0/.git

# Some QT-Apps/Gazebo don't not show controls without this
ENV QT_X11_NO_MITSHM 1

# Use UTF8 encoding in java tools (needed to compile jMAVSim)
ENV JAVA_TOOL_OPTIONS=-Dfile.encoding=UTF8


# Install Custom JSBSim
ADD "https://www.random.org/cgi-bin/randbyte?nbytes=10&format=h" skipcache
RUN mkdir /jsbsim_src
WORKDIR /jsbsim_src
RUN git clone -b pr-bldc-validation https://github.com/mvacanti/jsbsim.git .
RUN git checkout fb7de0a093f0c9da084bd97229d15e013ca0a6bd
RUN mkdir /build
WORKDIR /jsbsim_src/build
RUN cmake -DCMAKE_CXX_FLAGS_RELEASE="-O3 -march=native -mtune=native" -DCMAKE_C_FLAGS_RELEASE="-O3 -march=native -mtune=native" -DCMAKE_BUILD_TYPE=Release ..
RUN make install

EXPOSE 14550/udp
EXPOSE 14540/udp