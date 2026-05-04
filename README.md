# CoLMIN: LLM-based Multi-Decision Path Negotiation for Cooperative Autonomous Driving
<img width="1734" height="626" alt="image" src="https://github.com/user-attachments/assets/94a9ba8e-566f-48bb-9552-2d39dd123e39" />
# Installation
Three environments are needed: 'vllm' for MLLMs inference and 'colmin' for simulation.
# CoLMIN env


```text
git clone https://github.com/cxliu0314/CoLMDriver.git
conda create --name colmdriver python=3.7 cmake=3.22.1
conda activate colmdriver
conda install pytorch==1.10.1 torchvision==0.11.2 torchaudio==0.10.1 cudatoolkit=11.3 -c pytorch -c conda-forge
conda install cudnn -c conda-forge

pip install -r opencood/requirements.txt
pip install -r simulation/requirements.txt
```
