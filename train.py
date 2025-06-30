import warnings
warnings.filterwarnings("ignore")

import datetime

from unsloth import FastLanguageModel
import torch

from multiprocessing import cpu_count
num_proc = cpu_count()

import yaml

from data_processor import SplittedJsonIoDataset, filter_by_token_counts
from customs import customize_tokenizer

from unsloth import UnslothTrainer, UnslothTrainingArguments

from trl import SFTTrainer, DataCollatorForCompletionOnlyLM
from transformers import TrainingArguments, DataCollatorForSeq2Seq, DataCollatorForLanguageModeling
from unsloth import is_bfloat16_supported

from unsloth.chat_templates import train_on_responses_only

from unsloth import unsloth_train

#from eval_metrics import compute_metrics

from utils import save_log_history, save_model

if __name__ == "__main__":

    # Load configuration file
    with open("config.yaml", "r") as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)

    # Load model and tokenizer
    model, tokenizer = FastLanguageModel.from_pretrained(
        **config["model_loading_args"]
    )

    # Configure tokenizer parameters 
    model, tokenizer = customize_tokenizer(model, tokenizer, config)

    # Load dataset
    dataset = SplittedJsonIoDataset(tokenizer, config).create()

    # Remove examples of dataset based on token counts
    if config["filter_dataset"]:
        dataset = filter_by_token_counts(dataset, tokenizer, config)

    # Add LoRA weights
    model = FastLanguageModel.get_peft_model(
        model=model,
        **config["lora_parameters"]
    )

    # Set Data Collator based on training parameters
    if config["fine_tuning_args"]["training_type"]=="text_completion":
        _train_on_responses_only_bool = True
        data_collator = DataCollatorForSeq2Seq(tokenizer=tokenizer)
    elif config["fine_tuning_args"]["training_type"]=="continued_pre_training":
        _train_on_responses_only_bool = False
        data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)
    else:
        raise Exception("Wrong Training Type. Check config.yaml")

    # Initiate UnslothTrainer
    trainer = UnslothTrainer(
        model = model,
        tokenizer = tokenizer,
        train_dataset = dataset["train"],
        eval_dataset = dataset["eval"],
        data_collator = data_collator,
        dataset_text_field = "text",
        max_seq_length = config["model_loading_args"]["max_seq_length"], # Used only when packing=True for creating a ConstantLengthDataset.
        packing = config["sft_trainer_arguments"]["apply_packing"],
        dataset_num_proc = min(num_proc, config["sft_trainer_arguments"]["dataset_num_proc"]),
        #compute_metrics=compute_metrics,
        args = UnslothTrainingArguments(
            fp16 = not is_bfloat16_supported(),
            bf16 = is_bfloat16_supported(),
            **config["training_arguments"]
        )
    )

    if _train_on_responses_only_bool:
        trainer = train_on_responses_only(
            trainer,
            instruction_part = config["instruction_part"],
            response_part = config["response_part"]
        )
    
    trainer_stats = unsloth_train(trainer)
    
    save_log_history(trainer)

    #save_model(model, tokenizer, config)