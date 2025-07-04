from unsloth.chat_templates import get_chat_template

class ChatTemplateError(Exception):
    pass

def customize_tokenizer(model, tokenizer, config):

    # Bring chat template of the tokenizer
    if not hasattr(tokenizer, "chat_template"):
        if "chat_template" in config.keys():
            tokenizer = get_chat_template(tokenizer, chat_template=config["chat_template"])
            print(f"A {config['chat_template']} is selected for a model of class {model.__class__.__name__}")
        else:
            raise ChatTemplateError("""Tokenizer doesn't have a chat_template argument.
                                    It must be specified in config.yaml file""")
    else:
        print(f"Tokenizer has a built-in chat template.")

    # Set configuration for the tokenizer
    if config["fine_tuning_args"]["training_type"]=="text_completion":
        if tokenizer.pad_token is None:
            print("Pad token is not set. Assigning pad_token = eos_token...")
            tokenizer.pad_token = tokenizer.eos_token
        elif tokenizer.pad_token != tokenizer.eos_token:
            print(f"Pad token is already set to: {tokenizer.pad_token}")
        else:
            print("Pad token is already equal to EOS token.")
        #tokenizer._add_bos_token = False
        if tokenizer.padding_side != "right":
            print(f"Default padding side is {tokenizer.padding_side}. It is forced to be on the right!")
            tokenizer.padding_side = "right"
        else:
            print(f"Default padding side is right!")

    # Add special tokens to tokenizer and model's embedding layer accordingly
    if config["fine_tuning_args"]["special_tokens_list"]:
        print(f"Adding special tokens in the embedding layer of the model...")
        tokenizer.add_tokens(config["fine_tuning_args"]["special_tokens_list"])
        model.resize_token_embeddings(len(tokenizer))

    return model, tokenizer