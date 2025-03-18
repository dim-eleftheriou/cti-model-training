import evaluate
#import nltk

bleu = evaluate.load("bleu")
acc = evaluate.load("accuracy")
rouge = evaluate.load('rouge')

def compute_metrics(eval_preds):
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