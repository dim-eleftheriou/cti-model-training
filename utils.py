import os
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import subprocess
from transformers import TrainerCallback
from torch.utils.tensorboard import SummaryWriter

def save_log_history(trainer, return_history=False):

    # Create a directory for the log histoty
    if not os.path.exists("log_history"):
        os.makedirs("log_history")

    train_loss = []
    eval_loss = []
    learning_rate = []
    step = []
    epoch = []

    for idx in range(len(trainer.state.log_history) - 1):
        log_item = trainer.state.log_history[idx]
        if bool((idx+1) % 2 and idx!=1):
            train_loss.append(log_item["loss"])
            learning_rate.append(log_item["learning_rate"])
            step.append(log_item["step"])
            epoch.append(log_item["epoch"])
        else:
            eval_loss.append(log_item["eval_loss"])

    log_df = pd.DataFrame({
        "step":step,
        "epoch":epoch,
        "train_loss":train_loss,
        "eval_loss":eval_loss,
        "learning_rate":learning_rate
    })

    # Loss plot
    plt.figure(figsize=(10, 5))
    plt.plot(log_df["step"], log_df["train_loss"], label="Training Loss", marker="o", linestyle="-")
    plt.plot(log_df["step"], log_df["eval_loss"], label="Validation Loss", marker="s", linestyle="--")
    plt.xlabel("Steps")
    plt.ylabel("Loss")
    plt.title("Training vs Validation Loss")
    plt.legend()
    plt.grid(True)
    plt.savefig("log_history/loss_plot.png", dpi=300)

    # LR plot
    plt.figure(figsize=(10, 5))
    plt.plot(log_df["step"], log_df["learning_rate"], marker="o", linestyle="-")
    plt.xlabel("Steps")
    plt.ylabel("Learning Rate")
    plt.title("Learning Rate Curve")
    plt.legend()
    plt.grid(True)
    plt.savefig("log_history/lr_plot.png", dpi=300)

    if return_history:
        return log_df

def save_model(model, tokenizer, save_args):
    # Create a datetime stamp for logging
    dt = datetime.datetime.now().__str__().replace(" ", "--")

    if not os.path.exists(save_args["adapters_name"]):
        os.makedirs(save_args["adapters_name"])
    
    os.mkdirs(os.path.join(save_args["adapters_name"], dt))

    # Local saving in pt
    model.save_pretrained(os.path.join(save_args["adapters_name"], dt, "lora_model"))
    tokenizer.save_pretrained(os.path.join(save_args["adapters_name"], dt, "lora_model"))

    # Local saving in GGUF
    if save_args["save_to_gguf"]:
        model.save_pretrained_gguf(
            os.path.join(save_args["adapters_name"], dt, "lora_model"),
            tokenizer,
            quantization_method = save_args["quantization_method_gguf"],
        )

    # Online saving in pt
    if save_args["push_to_hub"]:
        model.push_to_hub(f"{save_args['online_directory']}/{save_args['online_name']}")
        tokenizer.push_to_hub(f"{save_args['online_directory']}/{save_args['online_name']}")

    # Online saving in GGUF
    if save_args["push_to_hub_gguf"]:
        model.push_to_hub_gguf(
            f"{save_args['online_directory']}/{save_args['online_name']}-GGUF",
            tokenizer,
            quantization_method = save_args["quantization_method_gguf"],
        )

class GPUMonitorCallback(TrainerCallback):
    def on_train_begin(self, args, state, control, **kwargs):
        # Create TensorBoard writer at training start
        self.writer = SummaryWriter(log_dir=args.logging_dir)

    def on_train_end(self, args, state, control, **kwargs):
        # Close writer when training ends
        self.writer.close()

    def log_gpu_stats(self, state, prefix=""):
        """Helper: query nvidia-smi and log stats with an optional prefix."""
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=index,utilization.gpu,memory.used,memory.total",
             "--format=csv,noheader,nounits"],
            stdout=subprocess.PIPE, text=True
        )

        for line in result.stdout.strip().split("\n"):
            idx, util, mem_used, mem_total = map(int, line.split(", "))
            step = state.global_step if state.global_step is not None else 0
            self.writer.add_scalar(f"{prefix}GPU{idx}/utilization", util, step)
            self.writer.add_scalar(f"{prefix}GPU{idx}/memory_used_MB", mem_used, step)

    def on_step_end(self, args, state, control, **kwargs):
        # Called after each training step
        self.log_gpu_stats(state, prefix="train/")

    def on_evaluate(self, args, state, control, **kwargs):
        # Called during evaluation (validation phase)
        self.log_gpu_stats(state, prefix="eval/")

