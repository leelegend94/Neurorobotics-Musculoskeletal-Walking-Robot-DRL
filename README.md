# Neurorobotics-Musculoskeletal-Walking-Robot-DRL

Train a musculoskeletal robot to walk on HBP Neurorobotics Platform using Deep Reinforcement Learning.

## Prerequisites

### 0. Only works on Ubuntu 18.04

### 1. If gpu support is required, firstly install Nvidia drivers, CUDA, CuDNN.

#### Install NVIDIA driver
sudo ubuntu-drivers autoinstall

 Please follow the steps described here: " https://www.tensorflow.org/install/gpu "  section Linux setup. TensorRT is not required. USE DEFAULT SETTINGS. SKIP NVIDIA DRIVER PART!! DON'T install tensorflow now!

#### Add NVIDIA package repositories
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/cuda-repo-ubuntu1804_10.0.130-1_amd64.deb
sudo dpkg -i cuda-repo-ubuntu1804_10.0.130-1_amd64.deb
sudo apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/7fa2af80.pub
sudo apt-get update
wget http://developer.download.nvidia.com/compute/machine-learning/repos/ubuntu1804/x86_64/nvidia-machine-learning-repo-ubuntu1804_1.0.0-1_amd64.deb
sudo apt install ./nvidia-machine-learning-repo-ubuntu1804_1.0.0-1_amd64.deb
sudo apt-get update

#### Install NVIDIA driver
sudo apt-get install --no-install-recommends nvidia-driver-418
##### Reboot. Check that GPUs are visible using the command: nvidia-smi

##### Install development and runtime libraries (~4GB)
sudo apt-get install --no-install-recommends \
    cuda-10-0 \
    libcudnn7=7.6.2.24-1+cuda10.0  \
    libcudnn7-dev=7.6.2.24-1+cuda10.0


### 2. Install tensorflow(-gpu)
-->Ensure you have Python 2.7 pip, dev, and virtualenv libraries installed.
$ sudo apt-get install python-pip python-dev python-virtualenv

-->Create and activate a virtualenv for TensorFlow, the steps below will assume installation into your ~/.opt directory used by the NRP. If you change this location, you will need to modify later steps.
$ virtualenv ~/.opt/tensorflow_venv
$ source ~/.opt/tensorflow_venv/bin/activate

-->Upgrade pip within your virtualenv, this is required by TensorFlow.
$ easy_install -U pip

-->Install TensorFlow, select one of the options below depending on your GPU configuration.
$ pip install --upgrade tensorflow==1.13.1       # select this option if you have no or a non-Nvidia GPU
$ pip install --upgrade tensorflow-gpu==1.13.1   # select this option if you have an Nvidia GPU with proper drivers

-->uninstall ALL protobuf packages installed in ~/.local/lib/python2.7/site-packages, ~/.opt/platform_venv and ~/.opt/tensorflow_venv
eg. uninstall protobuf in tensorflow_venv:
$ source ~/.opt/tensorflow_venv/bin/activate
$ pip uninstall protobuf

### 3. Install other packages
-->install protobuf 3.6.1 ONLY inside the tensorflow_venv
$ source ~/.opt/tensorflow_venv/bin/activate
$ pip install protobuf==3.6.1

-->install keras, keras-rl in tensorflow_venv
$ source ~/.opt/tensorflow_venv/bin/activate
$ pip install keras
$ pip install keras-rl
