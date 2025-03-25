import os
import pandas as pd
import matplotlib.pyplot as plt

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



