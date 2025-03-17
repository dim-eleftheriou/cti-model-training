from unsloth import FastLanguageModel
import torch

import yaml

from data_processor import SplittedJsonIoDataset
from customs import customize_tokenizer

from trl import SFTTrainer
from transformers import TrainingArguments, DataCollatorForSeq2Seq
from unsloth import is_bfloat16_supported

from unsloth.chat_templates import train_on_responses_only

from unsloth import unsloth_train

with open("config.yaml", "r") as f:
    config = yaml.load(f, Loader=yaml.SafeLoader)

model, tokenizer = FastLanguageModel.from_pretrained(
    **config["model_loading_args"]
)

model, tokenizer = customize_tokenizer(model, tokenizer, config)

# if config["model_loading_args"]["max_seq_length"] is None:
#     max_seq_length = tokenizer.model_max_length

dataset = SplittedJsonIoDataset(tokenizer, config["system_message"]).create()

# Add LoRA weights
model = FastLanguageModel.get_peft_model(
    model=model,
    **config["lora_parameters"]
)

trainer = SFTTrainer(
    model = model,
    tokenizer = tokenizer,
    train_dataset = dataset["train"],
    eval_dataset = dataset["eval"],
    data_collator = DataCollatorForSeq2Seq(tokenizer=tokenizer),
    dataset_text_field = "text",
    max_seq_length = config["model_loading_args"]["max_seq_length"], # Used only when packing=True for creating a ConstantLengthDataset.
    packing = config["fine_tuning_args"]["apply_packing"],
    dataset_num_proc = 1,
    #compute_metrics=compute_metrics_,
    args = TrainingArguments(
        fp16 = not is_bfloat16_supported(),
        bf16 = is_bfloat16_supported(),
        **config["training_arguments"]
    )
)

#from unsloth import UnslothTrainer, UnslothTrainingArguments

trainer = train_on_responses_only(
    trainer,
    instruction_part = "<|start_header_id|>user<|end_header_id|>",
    response_part = "<|start_header_id|>assistant<|end_header_id|>",
)

trainer_stats = unsloth_train(trainer)
