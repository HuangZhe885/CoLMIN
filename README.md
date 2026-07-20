# CoLMIN: LLM-based Multi-Decision Path Negotiation for Cooperative Autonomous Driving
<img width="1566" height="558" alt="image" src="https://github.com/user-attachments/assets/aaea0c7d-bb7f-4b51-963a-d3d190ab54da" />



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
### Step1: Download Models
Create a model storage directory and download the required models:

Example： Download Qwen2.5-VL-3B-Instruct-AWQ
```
mkdir vlm_models
huggingface-cli download Qwen/Qwen2.5-VL-3B-Instruct-AWQ --local-dir vlm_models/Qwen/Qwen2.5-VL-3B-Instruct-AWQ
```
### Step2: Start vlm model:
```
conda activate vllm
# VLM on call
CUDA_VISIBLE_DEVICES=4 vllm serve ckpt/colmin/VLM --port 1111 --max-model-len 8192 --trust-remote-code --enable-prefix-caching

# LLM on call
CUDA_VISIBLE_DEVICES=5 vllm serve ckpt/colmin/LLM --port 8888 --max-model-len 4096 --trust-remote-code --enable-prefix-caching 

CUDA_VISIBLE_DEVICES=3 vllm serve ckpt/colmin/LLM_7B --port 2222 --max-model-len 8192 --trust-remote-code --enable-prefix-caching
```
Note: make sure that the selected ports (1111,8888,2222) are not occupied by other services. If you use other ports, please modify values of key 'comm_client' and 'vlm_client' in

### Step3:  Run CARLA
```
conda activate colmin
# Start CARLA server, if port 2000 is already in use, choose another
CUDA_VISIBLE_DEVICES=0 ./external_paths/carla_root/CarlaUE4.sh --world-port=2000 -prefer-nvidia
```
### Step4: Run CoLMIN (close-loop evaluation)
```
bash scripts/eval/eval_mode.sh 0 2000 colmin ideal Interdrive_all
```
### Step5: Summarize the results
```
python visualization/result_analysis.py results/results_driving_colmin
```

# Docker Installation

We provide a Docker-based setup for the CoLMIN runtime environment. The Docker
image contains the Python environment and core dependencies for perception,
planning, and closed-loop evaluation. CARLA, checkpoints, datasets, and LLM/VLM
weights are not included in the image and should be mounted at runtime.

We recommend running the LLM/VLM services separately with `vllm`, because vLLM
usually requires a newer Python/CUDA stack than the CoLMIN closed-loop runtime.

## 1. Prepare Docker Files

Create `docker/Dockerfile.CoLMIN` in the repository:

```dockerfile
FROM nvidia/cuda:11.3.1-cudnn8-devel-ubuntu20.04

ENV DEBIAN_FRONTEND=noninteractive
ENV CONDA_DIR=/opt/conda
ENV PATH=${CONDA_DIR}/bin:${PATH}
ENV CUDA_HOME=/usr/local/cuda
ENV FORCE_CUDA=1

RUN apt-get update && apt-get install -y \
    git wget curl vim build-essential cmake ninja-build \
    libglib2.0-0 libsm6 libxext6 libxrender-dev libgl1-mesa-glx \
    libx11-6 libx11-xcb1 libxcb1 libxcb-render0 libxcb-shape0 libxcb-xfixes0 \
    ffmpeg libomp-dev ca-certificates unzip \
    && rm -rf /var/lib/apt/lists/*

RUN wget https://repo.anaconda.com/miniconda/Miniconda3-py37_4.12.0-Linux-x86_64.sh -O /tmp/miniconda.sh && \
    bash /tmp/miniconda.sh -b -p ${CONDA_DIR} && \
    rm /tmp/miniconda.sh && \
    conda clean -afy

SHELL ["/bin/bash", "-lc"]

RUN conda create -n colmin python=3.7 cmake=3.22.1 -y && \
    conda run -n colmin conda install -y \
    pytorch==1.10.1 torchvision==0.11.2 torchaudio==0.10.1 \
    cudatoolkit=11.3 -c pytorch -c conda-forge && \
    conda run -n colmin conda install -y cudnn -c conda-forge && \
    conda clean -afy

ENV PATH=${CONDA_DIR}/envs/colmin/bin:${CONDA_DIR}/bin:${PATH}

WORKDIR /workspace

RUN git clone --depth=1 https://github.com/HuangZhe885/CoLMIN.git /workspace/CoLMIN

WORKDIR /workspace/CoLMIN

RUN python -m pip install --upgrade "pip<24" wheel && \
    python -m pip install -r opencood/requirements.txt && \
    python -m pip install -r simulation/requirements.txt && \
    python -m pip install spconv-cu116 && \
    python -m pip install efficientnet_pytorch==0.7.0 && \
    python setup.py develop && \
    python opencood/utils/setup.py build_ext --inplace

RUN cd /workspace && \
    git clone https://github.com/klintan/pypcd.git && \
    cd pypcd && \
    python -m pip install python-lzf && \
    python setup.py install

RUN mkdir -p /workspace/CoLMIN/external_paths \
    /workspace/CoLMIN/ckpt \
    /workspace/CoLMIN/results

ENV PYTHONPATH=/workspace/CoLMIN:/workspace/CoLMIN/external_paths/carla_root/PythonAPI/carla/dist/carla-0.9.10-py3.7-linux-x86_64.egg:${PYTHONPATH}

CMD ["/bin/bash"]
```

Create `.dockerignore` in the repository:

```dockerignore
.git
ckpt
results
external_paths
data
*.pth
*.ckpt
*.tar
*.zip
*.egg
__pycache__
```

## 2. Build Docker Image

Build the image on your server:

```bash
docker build -f docker/Dockerfile.CoLMIN -t YOUR_DOCKERHUB_NAME/colmin:cu113 .
```

For example:

```bash
docker build -f docker/Dockerfile.CoLMIN -t huangzhe885/colmin:cu113 .
```

## 3. Push to DockerHub

After the image is built successfully, upload it to DockerHub:

```bash
docker login
docker push YOUR_DOCKERHUB_NAME/colmin:cu113
```

Other users can then directly pull the image:

```bash
docker pull YOUR_DOCKERHUB_NAME/colmin:cu113
```

## 4. Run Docker Container

Start the container and mount CARLA, checkpoints, datasets, and result folders:

```bash
docker run --gpus all --net=host --ipc=host --shm-size=32g -it \
  -v /path/to/carla:/workspace/CoLMIN/external_paths/carla_root \
  -v /path/to/ckpt:/workspace/CoLMIN/ckpt \
  -v /path/to/data_root:/workspace/CoLMIN/external_paths/data_root \
  -v /path/to/results:/workspace/CoLMIN/results \
  --name colmin_env \
  YOUR_DOCKERHUB_NAME/colmin:cu113 bash
```

Please replace the mounted paths with your local paths. For example,
`/path/to/carla` should point to the CARLA 0.9.10.1 directory.

If you use the example image name:

```bash
docker run --gpus all --net=host --ipc=host --shm-size=32g -it \
  -v /path/to/carla:/workspace/CoLMIN/external_paths/carla_root \
  -v /path/to/ckpt:/workspace/CoLMIN/ckpt \
  -v /path/to/data_root:/workspace/CoLMIN/external_paths/data_root \
  -v /path/to/results:/workspace/CoLMIN/results \
  --name colmin_env \
  huangzhe885/colmin:cu113 bash
```

## 5. Start LLM/VLM Services

Start the LLM/VLM services outside the Docker container in the `vllm`
environment:

```bash
conda activate vllm

# VLM service
CUDA_VISIBLE_DEVICES=4 vllm serve ckpt/colmin/VLM \
  --port 1111 \
  --max-model-len 8192 \
  --trust-remote-code \
  --enable-prefix-caching

# LLM service
CUDA_VISIBLE_DEVICES=5 vllm serve ckpt/colmin/LLM \
  --port 8888 \
  --max-model-len 4096 \
  --trust-remote-code \
  --enable-prefix-caching

# Optional LLM-7B service
CUDA_VISIBLE_DEVICES=3 vllm serve ckpt/colmin/LLM_7B \
  --port 2222 \
  --max-model-len 8192 \
  --trust-remote-code \
  --enable-prefix-caching
```

Make sure the ports used here are consistent with the `comm_client` and
`vlm_client` settings in the agent configuration.

## 6. Run CARLA

Inside the Docker container, start the CARLA server:

```bash
cd /workspace/CoLMIN
CUDA_VISIBLE_DEVICES=0 ./external_paths/carla_root/CarlaUE4.sh \
  --world-port=2000 \
  -prefer-nvidia
```

If port `2000` is already occupied, choose another port and use the same port in
the evaluation command.

## 7. Run Closed-loop Evaluation

Open another terminal and enter the same container:

```bash
docker exec -it colmin_env bash
```

Run CoLMIN closed-loop evaluation:

```bash
cd /workspace/CoLMIN
bash scripts/eval/eval_mode.sh 0 2000 colmin ideal Interdrive_all
```

Summarize the results:

```bash
python visualization/result_analysis.py results/results_driving_colmin
```

## Notes

- The Docker image does not include CARLA, datasets, checkpoints, or LLM/VLM
  weights.
- CARLA should be version `0.9.10.1`.
- The container uses `--net=host`, so the vLLM ports can be accessed directly
  from inside the container.
- If you change the CARLA world port, keep the port consistent between the
  CARLA server and `scripts/eval/eval_mode.sh`.



## Acknowledgement

We build our framework on top of 'V2XVerse' and "CoLMDriver", please refer to the repo
```
https://github.com/CollaborativePerception/V2Xverse
https://github.com/cxliu0314/CoLMDriver
```
