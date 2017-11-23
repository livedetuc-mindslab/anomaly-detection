# The MAUM Platform

## Overview

- Dialog Service Platform
- Dialog Service Development Platform
- Installation type: On-Premise or SaaS on AWS or azure.

## Development Environment
- server
   - C++
- protocols
   - grpc based interface
- admin console web
   - angular 2
   - angular 2 material
- admin console rest
   - nodejs 6.10 or later
   - grpc node
   - [loopback](http://loopback.io/) 3
- web proxy server
   - nginx 1.11 or later
- web had
   - nodejs with websocket

## Build

### Overview

- CMake (2.8.12) above, 3.1 or later is better choice.
- GCC 4.8.2 for full support c++-11, SEE issue #18, [18](https://github.com/mindslab-ai/minds-va/issues/18)
- nodejs 6.10.0 above

### Checkout

```bash
git clone git@github.com:mindslab-ai/maum.git
```

### External Dependencies
It shows build time dependencies only.
All prerequisite packages are installed by `prerequisite.sh`.

The following package dependencies show this project perspectives only.
Do not use the following command directly.

##### Ubuntu External Dependencies
```bash
sudo apt-get install -y \
  gcc-4.8 g++-4.8 g++ \
  make cmake \
  autoconf automake libtool \
  python-pip python-dev \
  openmpi-common \
  libboost-all-dev \
  libcurl4-openssl-dev \
  libsqlite3-dev \
  libmysqlclient-dev \
  libuv-dev libssl-dev \
  libarchive13 libarchive-dev \
  libatlas-base-dev libatlas-dev \
  docker.io \
  unzip \
  nginx \
  ffmpeg
sudo ldconfig
curl -sL https://deb.nodesource.com/setup_6.x | sudo -E bash -
sudo apt-get install -y nodejs
```

##### CentOS or REDHAT External Dependencies
```bash
sudo yum -y install epel-release
sudo yum -y groupinstall 'Development Tools'
sudo yum -y install \
  gcc gcc-c++ \
  autoconf automake libtool make \
  cmake cmake3 \
  glibc-devel.x86_64 \
  java-1.8.0-openjdk-devel.x86_64 \
  python-devel.x86_64 \
  flex-devel..x86_64 \
  boost-devel.x86_64 \
  libcurl-devel.x86_64 \
  sqlite-devel.x86_64 \
  mysql-community-devel.x86_64 \
  openssl-devel.x86_64 \
  libarchive-devel.x86_64 \
  atlas-devel.x86_64 \
  lapack-devel.x86_64 \
  libuv-devel.x86_64 \
  httpd nginx \
  policycoreutils-python

## TODO (jeongho-kim) docker install

# install pip & package
curl "https://bootstrap.pypa.io/get-pip.py" -o "get-pip.py"
sudo python get-pip.py
rm get-pip.py
# npm
curl --silent --location https://rpm.nodesource.com/setup_6.x | sudo bash -
sudo yum install -y nodejs

```

#### External Python Packages

```bash
sudo pip install --upgrade pip
sudo pip install --upgrade virtualenv
sudo pip install boto3 grpcio==1.0.1 requests numpy theano gensim
```

#### External Node Packages
```bash
sudo npm install -g @angular/cli@1.0.0
```

### Internal Dependencies
The following dependencies are managed by submodules. (See `git submodule`)
- libminds
  - protobuf 3.2
  - grpc 1.1.3
- minds-stt
- minds-ta
- hazelcast-cpp-client
- (cassandra) cpp-driver

Above protobuf, grpc, hazelcast-cpp-client, cassandra-cpp-driver is not
managed by OS package system not yet. We manage it locally via git submodule.

### How to use `build.sh`
- All sub build tasks.
  - libminds: protobuf, libminds, grpc 
  - libdb: hazelcast-cpp-client, cassadra-cpp-driver 
  - stt: minds-stt
  - ta: minds-ta
  - maum: maum servers, web-console, web-rest
    - web-had is not build automatically.
- Build Mode
  - It build required tasks.
  - It install all built outputs to target directory.
    Default target directory is `~/minds`.
  - It install all required resources to target directory.
  ```bash
  ./build.sh ~/minds all
  ./build.sh ~/minds maum
  ./build.sh ~/minds libminds stt
  ```
- Deploy Mode
  - It create an temporary directory for deploy build.
  - It build required packages.
  - It install all binaries and resources except stt, ta resources.
  - It generates `.tar.gz` file to `out` directory at source root.
  ```bash
  ./build.sh tar
  ./build.sh tar ta-only
  ./build.sh tar stt-only
  ```
- Other commnads
  ```bash
  ./build.sh clean-deploy
  ./build.sh clean-cache
  ```
#### Internal build.sh
- ~/.minds-build
  - `cache`: This directory has several prebuilt results.
     It caches previous external build output for protobuf, grpc,
     hazelcast-cpp-client, cassandra-cpp-driver by compiler version.
  - `*.done`: If a prerequisite.sh successfully install all depencencies,
     this files are generated with given sha1 hash for its script.
- `build-debug`: `cmake` create this directory for develop mode.
- `build-deploy-debug`: `cmake` create this directory for deploy mode.
- Generated tar file has version number from `git describe`.

#### cmake
- Use 2.8.12 above.
- In centos, use `cmake3` not `cmake`.

It use the following options.

- DCMAKE_INSTALL_PREFIX=${MINDS_ROOT}
- DCMAKE_BUILD_TYPE=Debug
- DCMAKE_CXX_COMPILER:FILEPATH=/usr/bin/g++-4.8
- DCMAKE_C_COMPILER:FILEPATH=/usr/bin/gcc-4.8

In centos, `/usr/bin/g++` version is 4.8.5.

### Custom build for special options.
Maum has several preprocessors to build special outputs.

- for audio file storing
  ```bash
  mkdir ~/git/maum/build-debug-record
  cd ~/git/maum/build-debug-record
  cmake \
    -DCMAKE_INSTALL_PREFIX=${MINDS_ROOT} \
    -DCMAKE_BUILD_TYPE=Debug \
    -DCMAKE_CXX_COMPILER:FILEPATH=/usr/bin/g++-4.8 \
    -DCMAKE_C_COMPILER:FILEPATH=/usr/bin/gcc-4.8 \
    -DDEFINE_RECORD_AUDIO=ON \
    ..
  ```

- Use `alias.root`

```bash
git config --global --add alias.root '!pwd'
make -C $(git root)/build-debug install
```

- CLion create debug build directory. Use it.
  - Goto `Settings > Build, Execution, Deployment > CMake` in settings.
  - Add cmake options.
  ```bash
    -DCMAKE_INSTALL_PREFIX=${MINDS_ROOT}
    -DCMAKE_CXX_COMPILER:FILEPATH=/usr/bin/g++-4.8
    -DCMAKE_C_COMPILER:FILEPATH=/usr/bin/gcc-4.8
  ```
    
```bash
make -C $(git root)/cmake-build-debug install
```

## Development tools, Testing

In development, `~/minds` is the default installation directory.
It is more convenient to handle built binaries and libraries.

### Settings
```bash
export MINDS_ROOT=~/minds
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:${MINDS_ROOT}/lib
export PATH=$PATH:${MINDS_ROOT}/bin:
CDPATH=~/minds:~/git/maum:..:. # maum path is can be changed by personal setting.
```

```bash
cd logs # it will drop you at ~/minds/logs
cd bin
```

### Use `mindset`

```bash
mindset gen dev
mindset gen prod
```

It generates all configuration files always.

### Use systemd

### Scripts to run server

```bash
sudo ${MINDS_ROOT}/bin/mindset systemd 

sudo sytemctl daemon-reload
sudo systemctl start minds.target
sudo systemctl list-units minds*
sudo systemctl restart minds.target
sudo systemctl stop minds.target
sudo systemctl enable minds.target
sudo systemctl disable minds.target
```

### Start Docker manually

#### docker install
```
sudo apt-get install docker.io
sudo usermod -aG docker $USER
```

#### Hazelcast docker container
```bash
sudo apt-get install openjdk-8-jdk
docker pull hazelcast/hazelcast
docker run -p 5701:5701 -ti hazelcast/hazelcast
```

#### Cassandra docker container
```bash
test -d ${MINDS_ROOT}/db | mkdir -p  ${MINDS_ROOT}/db
docker run --name cassandra  \
 -p 9042:9042 \
 -v ${MINDS_ROOT}/db:/var/lib/cassandra \
 -d cassandra:latest
```

### python library dependency for dialog agent testing.
```bash
sudo pip install pymysql
```
# Rep1

