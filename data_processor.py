import os
import json
import datasets


class SplittedJsonIoDataset:

    def __init__(self, tokenizer, config):
        self.tokenizer = tokenizer
        self.system_message = config["system_message"]
        self.io_dataset_path = config["io_dataset_path"]
        self.train_path = os.path.join(config["io_dataset_path"], "train")
        self.eval_path = os.path.join(config["io_dataset_path"], "validation")

    @staticmethod
    def load_single_example(path:str, filename:str):
        with open(os.path.join(path, filename), mode="r", encoding="utf-8") as f:
            return json.load(f)
    
    def format_example(self, example:dict):
        formatted_example = [
            {"role": "assistant", "content": self.system_message},
            {"role": "user", "content": example["input"]},
            {"role": "assistant", "content": str(example["output"])}
        ]
        return formatted_example
    
    def load_raw_data(self) -> tuple[list[str], list[str]]:   
        raw_train_list = [self.load_single_example(self.train_path, filename) for filename in os.listdir(self.train_path)]
        raw_eval_list = [self.load_single_example(self.eval_path, filename) for filename in os.listdir(self.eval_path)]
        return raw_train_list, raw_eval_list

    def create(self):
        # Load raw data
        raw_train_list, raw_eval_list = self.load_raw_data()
        # Format examples in lists of dicts
        formatted_train_list = [self.format_example(example) for example in raw_train_list]
        formatted_eval_list = [self.format_example(example) for example in raw_eval_list]
        # Add template of the model in examples
        templated_train_list = [self.tokenizer.apply_chat_template(convo, tokenize = False, add_generation_prompt = False) for convo in formatted_train_list]
        templated_eval_list = [self.tokenizer.apply_chat_template(convo, tokenize = False, add_generation_prompt = False) for convo in formatted_eval_list]
        # Create hf seperated datasets
        hf_train = datasets.Dataset.from_list([dict(text=ex) for ex in templated_train_list])
        hf_eval = datasets.Dataset.from_list([dict(text=ex) for ex in templated_eval_list])
        # Create a hf dataset dict
        dataset = datasets.DatasetDict({"train":hf_train, "eval":hf_eval})
        return dataset

    @staticmethod
    def serialize(data:list):
        data_serialized = [
            {"input": example["input"],
            "output": json.dumps(example["output"])} for example in data]
        return data_serialized
    
    def grpo_format_dataset(self, dataset:datasets.Dataset):
        formatted_dataset = dataset.map(lambda x: {
            'prompt': [
                {'role': 'system', 'content': self.system_message},
                {'role': 'user', 'content': x['input']}
            ],
            'answers': x['output']
        })
        return formatted_dataset.remove_columns(['input', 'output'])

    def grpo_create(self):
        # Load raw data
        raw_train_list, raw_eval_list = self.load_raw_data()
        # List of data must be serialized. "output" should be str
        train_data_serialized = self.serialize(raw_train_list)
        eval_data_serialized = self.serialize(raw_eval_list)
        # Create HF datasets
        train_dataset = datasets.Dataset.from_list(train_data_serialized)
        eval_dataset = datasets.Dataset.from_list(eval_data_serialized)
        # Format for GRPO training
        train_dataset = self.grpo_format_dataset(train_dataset)
        eval_dataset = self.grpo_format_dataset(eval_dataset)
        # Create a hf dataset dict
        dataset = datasets.DatasetDict({"train":train_dataset, "eval":eval_dataset})
        return dataset

def filter_by_token_counts(dataset, tokenizer, config):
    if config["max_seq_length"]:
        limit = config["max_seq_length"]
    else:
        limit = tokenizer.model_max_length
    dataset = dataset.filter(lambda x: len(tokenizer.encode(x["text"])) <= limit)
    return dataset