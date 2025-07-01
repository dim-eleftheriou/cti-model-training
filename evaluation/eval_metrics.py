import torch
import evaluate
#import nltk

bleu = evaluate.load("bleu")
acc = evaluate.load("accuracy")
rouge = evaluate.load('rouge')

def compute_metrics(eval_preds, tokenizer):
    preds, labels = eval_preds
    # preds have the same shape as the labels, after the argmax(-1) has been calculated
    # by preprocess_logits_for_metrics but we need to shift the labels
    labels = labels[:, 1:]
    preds = preds[:, :-1]
    # -100 is a default value for ignore_index used by DataCollatorForCompletionOnlyLM
    mask = labels == -100
    labels[mask] = tokenizer.pad_token_id
    preds[mask] = tokenizer.pad_token_id

    decoded_labels = tokenizer.batch_decode(labels, skip_special_tokens=True)
    decoded_preds = tokenizer.batch_decode(preds, skip_special_tokens=True)

    bleu_score = bleu.compute(predictions=decoded_preds, references=decoded_labels)
    accuracy = acc.compute(predictions=preds[~mask], references=labels[~mask])
    rouge_score = rouge.compute(predictions=decoded_preds, references=decoded_labels)

    return {**bleu_score, **rouge_score, **accuracy}

# def postprocess_text(preds, labels):
#     preds = [pred.strip() for pred in preds]
#     labels = [label.strip() for label in labels]

#     # rougeLSum expects newline after each sentence
#     preds = ["\n".join(nltk.sent_tokenize(pred)) for pred in preds]
#     labels = ["\n".join(nltk.sent_tokenize(label)) for label in labels]

#     return preds, labels

# def compute_metrics__(eval_preds):
#     preds, labels = eval_preds
#     if isinstance(preds, tuple):
#         preds = preds[0]
#     # Replace -100s used for padding as we can't decode them
#     preds = np.where(preds != -100, preds, tokenizer.pad_token_id)
#     decoded_preds = tokenizer.batch_decode(preds, skip_special_tokens=True)
#     labels = np.where(labels != -100, labels, tokenizer.pad_token_id)
#     decoded_labels = tokenizer.batch_decode(labels, skip_special_tokens=True)

#     # Some simple post-processing
#     decoded_preds, decoded_labels = postprocess_text(decoded_preds, decoded_labels)

#     result = rouge.compute(predictions=decoded_preds, references=decoded_labels, use_stemmer=True)
#     result = {k: round(v * 100, 4) for k, v in result.items()}
#     prediction_lens = [np.count_nonzero(pred != tokenizer.pad_token_id) for pred in preds]
#     result["gen_len"] = np.mean(prediction_lens)
#     return result

def perplexiy(model, tokenizer, dataset):
    nlls = []
    max_length = 2048
    stride = 512
    for s in range(len(dataset['text'])):
        encodings = tokenizer(dataset['text'][s], return_tensors="pt")
        seq_len = encodings.input_ids.size(1)
        prev_end_loc = 0
        for begin_loc in range(0, seq_len, stride):
            end_loc = min(begin_loc + max_length, seq_len)
            trg_len = end_loc - prev_end_loc
            input_ids = encodings.input_ids[:, begin_loc:end_loc].to("cuda")
            target_ids = input_ids.clone()
            target_ids[:, :-trg_len] = -100
            # Create attention mask based on pad token id
            pad_token_id = tokenizer.pad_token_id if tokenizer.pad_token_id is not None else 0
            attention_mask = (input_ids != pad_token_id).long()
            with torch.no_grad():
                outputs = model(input_ids, labels=target_ids, attention_mask=attention_mask)
                neg_log_likelihood = outputs.loss
            nlls.append(neg_log_likelihood)
            prev_end_loc = end_loc
            if end_loc == seq_len:
                break
    ppl = torch.exp(torch.stack(nlls).mean())
    return ppl