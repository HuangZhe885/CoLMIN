# CoLMIN: LLM-based Multi-Decision Path Negotiation for Cooperative Autonomous Driving
<img width="1734" height="626" alt="image" src="https://github.com/user-attachments/assets/94a9ba8e-566f-48bb-9552-2d39dd123e39" />
# Installation
Three environments are needed: 'vllm' for MLLMs inference and 'colmin' for simulation.
# CoLMIN env

## 1. Get code and create pytorch environment.
```
git clone https://github.com/HuangZhe885/CoLMIN.git
conda create --name colmin python=3.7 cmake=3.22.1
conda activate colmin
conda install pytorch==1.10.1 torchvision==0.11.2 torchaudio==0.10.1 cudatoolkit=11.3 -c pytorch -c conda-forge
conda install cudnn -c conda-forge

pip install -r opencood/requirements.txt
pip install -r simulation/requirements.txt

#Install spconv
python -m pip install spconv-cu116

# Set up opencood
python setup.py develop
python opencood/utils/setup.py build_ext --inplace  # Bbx IOU cuda version compile

# Install pypcd
cd .. # go to another folder
git clone https://github.com/klintan/pypcd.git
cd pypcd
python -m pip install python-lzf
python setup.py install
cd ..

# install efficientNet
python -m pip install efficientnet_pytorch==0.7.0
```
## 2. Download and setup CARLA 0.9.10.1.
Carla code is only tested in CARLA 0.9.10.1 which requires python 3.7. So please open another environment with python 3.7 to install carla.
```
conda deactivate
conda create --name Carla python=3.7
conda activate Carla
python -m pip install setuptools==41
chmod +x simulation/setup_carla.sh
./simulation/setup_carla.sh
easy_install carla/PythonAPI/carla/dist/carla-0.9.10-py3.7-linux-x86_64.egg
mkdir external_paths
ln -s ${PWD}/carla/ external_paths/carla_root
# If you already have a Carla, just create a soft link to external_paths/carla_root
```

Note: we choose the setuptools==41 to install because this version has the feature easy_install. After installing the carla.egg you can install the lastest setuptools to avoid No module named distutils_hack.

## 3. vllm env

Refer to official repo of https://github.com/vllm-project/vllm

## How to config?
We use vLLM to deploy and run local models. Here are the detailed deployment steps:

```
conda create -n vllm python=3.12 -y
conda activate vllm
git clone https://github.com/vllm-project/vllm.git
cd vllm
VLLM_USE_PRECOMPILED=1 pip install --editable .
```
### Download Models
Create a model storage directory and download the required models:
Example： Download Qwen2.5-VL-3B-Instruct-AWQ
```
mkdir vlm_models
huggingface-cli download Qwen/Qwen2.5-VL-3B-Instruct-AWQ --local-dir vlm_models/Qwen/Qwen2.5-VL-3B-Instruct-AWQ
```
### Start vlm model:
```
conda activate vllm
# VLM on call
CUDA_VISIBLE_DEVICES=4 vllm serve ckpt/colmin/VLM --port 1111 --max-model-len 8192 --trust-remote-code --enable-prefix-caching

# LLM on call
CUDA_VISIBLE_DEVICES=5 vllm serve ckpt/colmin/LLM --port 8888 --max-model-len 4096 --trust-remote-code --enable-prefix-caching 

CUDA_VISIBLE_DEVICES=3 vllm serve ckpt/colmin/LLM_7B --port 2222 --max-model-len 8192 --trust-remote-code --enable-prefix-caching
```
Note: make sure that the selected ports (1111,8888) are not occupied by other services. If you use other ports, please modify values of key 'comm_client' and 'vlm_client' in
