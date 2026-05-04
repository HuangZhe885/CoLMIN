# CoLMIN: LLM-based Multi-Decision Path Negotiation for Cooperative Autonomous Driving
<img width="1734" height="626" alt="image" src="https://github.com/user-attachments/assets/94a9ba8e-566f-48bb-9552-2d39dd123e39" />
# Installation
Three environments are needed: 'vllm' for MLLMs inference and 'colmin' for simulation.
# CoLMIN env

## 1. Get code and create pytorch environment.
```text
git clone https://github.com/cxliu0314/CoLMDriver.git
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
```text
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

### Note: we choose the setuptools==41 to install because this version has the feature easy_install. After installing the carla.egg you can install the lastest setuptools to avoid No module named distutils_hack.



