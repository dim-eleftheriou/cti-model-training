import mlflow
from mlflow.models import infer_signature

import yaml

from unsloth import FastLanguageModel
import torch

with open("config.yaml", "r") as f:
    config = yaml.load(f, Loader=yaml.SafeLoader)

model, tokenizer = FastLanguageModel.from_pretrained(
    **config["model_loading_args"]
)