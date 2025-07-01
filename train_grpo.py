import os
import re
import json
from datasets import Dataset

# Load and prep dataset
SYSTEM_PROMPT = """
You are an AI Security Analyst in Cyberthreat Intelligence (CTI). Your task is to:
(1) identify any of the following STIX Domain Objects (SDOs), STIX Cyber-observable Objects (SCOs)
and STIX Relationship Objects (SROs) in a given report and
(2) generate the respective STIX2.1 bundle that represents your findings.
It follows the list of SDOs, SCOs and SROs that you are searching for as well as the mandatory and optional details you should
include in the bundle for each one.

### SROs ###
relationship -> id, type , relationship_type, source_ref, target_ref, description (Optional)

### SCOs ###
domain-name -> id, type, value
hostname -> id, type, value
url -> id, type, value
email-addr -> id, type, value
ipv4-addr -> id, type, value
cryptocurrency-wallet -> id, type, value

### SDOs ###
indicator -> id, type, name, description (Optional), indicator_types (Optional list), pattern, pattern_type, pattern_type (Should one of "stix", "snort", "yara")
file -> id, type, name (Optional), hashes (Should be json), size (Optional), mime_type (Optional)
attack-pattern -> id, type, name, description (Optional), aliases (Optional)
identity -> id, type, name, description (Optional)
malware -> id, type, name, description (Optional), malware_types (Optional), is_family (Optional), aliases (Optional), os_execution_envs (Optional), architecture_execution_envs (Optional), implementation_languages (Optional)
report -> id, type, name, description (Optional), labels:list, report_types (Optional list), created (Should be datetime), object_refs (Should be a list)
location -> id, type, name, description (Optional), country, description (Optional), latitude (Optional), longtitude (Optional), city (Optional)
vulnerability -> id, type, name, description (Optional)
intrusion-set -> id, type, name, description (Optional), aliases (Optional), goals (Optional), resource_level (Optional), primary_motivation (Optional), secondary_motivation (Optional)

Respond in the following format:
<reasoning>
(Identify all SDOs, SCOs and SROs)...
</reasoning>
<answer>
(Generate the STIX bundle)...
</answer>
"""

XML_COT_FORMAT = """\
<reasoning>
{reasoning}
</reasoning>
<answer>
{answer}
</answer>
"""

train_data_path = os.path.join(extract_to, "io-pairs", "train")
data = []
for file in os.listdir(train_data_path):
    if file.endswith(".json"):
        with open(os.path.join(train_data_path, file), "r") as f:
            data.append(json.load(f))

def create_training_dataset(data:list):
  # List of data must be serialized. "output" should be str
  data_serialized = [
    {"input": example["input"],
     "output": json.dumps(example["output"])} for example in data]
  train_dataset = Dataset.from_list(data_serialized)
  train_dataset = train_dataset.map(lambda x: {
      'prompt': [
          {'role': 'system', 'content': SYSTEM_PROMPT},
          {'role': 'user', 'content': x['input']}
      ],
      'answers': x['output']
  })
  return train_dataset.remove_columns(['input', 'output'])

train_dataset = create_training_dataset(data)




from dataprep.stix.StixConfig import StixToPydanticMap, STIX
from pydantic import BaseModel, ValidationError

def deserialize_answer(answer: str) -> dict:
    return json.loads(answer)

def deserialize_response_for_evaluation(answer: str) -> dict:
    if is_stix_bundle(answer):
        return json.loads(answer)
    else:
        return {"id":"", "type":"bundle", "objects":[]}

def extract_xml_answer(response: str) -> str:
    answer = response.split("<answer>")[-1]
    answer = answer.split("</answer>")[0]
    return answer.strip()

def is_stix_bundle(text: str) -> bool:
    try:
        bundle = json.loads(text)
        pydantic_stix_bundle = STIX(**bundle)
        return True
    except:
        return False

def count_valid_stix_objects(text: str) -> bool:
    smap = StixToPydanticMap()
    cnt = 0.0
    if is_stix_bundle(text):
        bundle = json.loads(text)
        for obj in bundle["objects"]:
            try:
                smap(obj)
                cnt += 1
            except ValidationError:
                pass
        return cnt / len(bundle["objects"])
    else:
      return cnt
    

# Reward functions
from evaluation.stix_evaluator import STIXEvaluator

def format_reward_func(completions, **kwargs) -> list[float]:
    """Reward function that checks if the completion has a specific format."""
    pattern = r"<reasoning>.*?</reasoning>\s*<answer>.*?</answer>"
    responses = [completion[0]["content"] for completion in completions]
    matches = [re.match(pattern, r) for r in responses]
    return [0.5 if match else 0.0 for match in matches]

def stix_validity_reward_func(completions, answers, **kwargs) -> list[float]:
    """Reward function that checks if the completion can is a stix bundle."""
    responses = [completion[0]['content'] for completion in completions]
    extracted_responses = [extract_xml_answer(r) for r in responses]
    return [0.5 if is_stix_bundle(r) else 0.0 for r in extracted_responses]

def stix_objects_validity_reward_func(completions, answers, **kwargs) -> list[float]:
    """Reward function that checks if the completion has valid stix objects."""
    responses = [completion[0]['content'] for completion in completions]
    extracted_responses = [extract_xml_answer(r) for r in responses]
    return [0.5 * count_valid_stix_objects(r) for r in extracted_responses]

def accuracy_reward_func(completions, answers, **kwargs) -> list[float]:
    evaluator = STIXEvaluator()
    responses = [completion[0]['content'] for completion in completions]
    extracted_responses = [extract_xml_answer(r) for r in responses]
    desirialized_responses = [deserialize_response_for_evaluation(r) for r in extracted_responses]
    desirialized_answers = [deserialize_answer(a) for a in answers]
    return [evaluator.evaluate_single(r, a)[2] for r, a in zip(desirialized_responses, desirialized_answers)]


from unsloth import FastLanguageModel, is_bfloat16_supported
from unsloth.chat_templates import get_chat_template
import torch
max_seq_length = 5096 # Can increase for longer reasoning traces
lora_rank = 8 # Larger rank = smarter, but slower

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "unsloth/Llama-3.2-1B",
    max_seq_length = max_seq_length,
    load_in_4bit = True, # False for LoRA 16bit
    fast_inference = True, # Enable vLLM fast inference
    max_lora_rank = lora_rank,
    gpu_memory_utilization = 0.7, # Reduce if out of memory
)

model = FastLanguageModel.get_peft_model(
    model,
    r = lora_rank, # Choose any number > 0 ! Suggested 8, 16, 32, 64, 128
    target_modules = ["gate_proj", "up_proj", "down_proj",],
    lora_alpha = lora_rank,
    use_gradient_checkpointing = "unsloth", # Enable long context finetuning
    random_state = 3407,
)

# Bring chat template of the tokenizer
tokenizer = get_chat_template(tokenizer, chat_template="llama-3.2")



from trl import GRPOConfig, GRPOTrainer
training_args = GRPOConfig(
    use_vllm = True, # use vLLM for fast inference!
    learning_rate = 5e-6,
    adam_beta1 = 0.9,
    adam_beta2 = 0.99,
    weight_decay = 0.1,
    warmup_ratio = 0.1,
    lr_scheduler_type = "cosine",
    optim = "paged_adamw_8bit",
    logging_steps = 1,
    per_device_train_batch_size = 1,
    gradient_accumulation_steps = 1, # Increase to 4 for smoother training
    num_generations = 4, # Decrease if out of memory
    max_prompt_length = 5096,
    max_completion_length = 5096,
    # num_train_epochs = 1, # Set to 1 for a full training run
    max_steps = 500,
    save_steps = 250,
    max_grad_norm = 0.1,
    report_to = "none", # Can use Weights & Biases
    output_dir = "outputs",
)


trainer = GRPOTrainer(
    model = model,
    processing_class = tokenizer,
    reward_funcs = [
        format_reward_func,
        stix_validity_reward_func,
        stix_objects_validity_reward_func,
        accuracy_reward_func
    ],
    args = training_args,
    train_dataset = train_dataset,
)
trainer.train()