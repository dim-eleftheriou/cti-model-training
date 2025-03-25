import os

os.system('pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126')
os.system('pip install "unsloth[windows] @ git+https://github.com/unslothai/unsloth.git"')
os.system('pip install evaluate rouge_score tensorboard scikit-learn absl-py matplotlib')