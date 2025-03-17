from unsloth.chat_templates import get_chat_template

def customize_tokenizer(model, tokenizer, config):

    # Bring chat template of the tokenizer
    tokenizer = get_chat_template(tokenizer, chat_template=config["chat_template"])

    # Set configuration for the tokenizer
    if config["fine_tuning_args"]["training_type"]=="text_completion":
        #tokenizer._add_bos_token = False
        tokenizer.pad_token = tokenizer.eos_token
        tokenizer.padding_side = "right"

    # Add special tokens to tokenizer and model's embedding layer accordingly
    if config["fine_tuning_args"]["special_tokens_list"]:
        tokenizer.add_tokens(config["fine_tuning_args"]["special_tokens_list"])
        model.resize_token_embeddings(len(tokenizer))

    return model, tokenizer