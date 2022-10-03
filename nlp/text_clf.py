import re

import torch
import pandas as pd
from sklearn.model_selection import train_test_split
from transformers import BertTokenizer
from torch.utils.data import TensorDataset
from transformers import BertForSequenceClassification
from torch.utils.data import DataLoader, RandomSampler, SequentialSampler
from transformers import get_linear_schedule_with_warmup
import numpy as np
from sklearn.metrics import f1_score
import random
from tqdm import tqdm
from torch.optim import AdamW


BATCH_SIZE = 4
EPOCHS = 10
NUM_CLASSES = 3
LR = 1e-5


def f1_score_func(preds, labels):
    preds_flat = np.argmax(preds, axis=1).flatten()
    labels_flat = labels.flatten()
    return f1_score(labels_flat, preds_flat, average='weighted')


def accuracy_per_class(preds, labels):
    label_dict_inverse = {v: k for k, v in range(NUM_CLASSES)}
    preds_flat = np.argmax(preds, axis=1).flatten()
    labels_flat = labels.flatten()

    for label in np.unique(labels_flat):
        y_pred = preds_flat[labels_flat == label]
        y_true = labels_flat[labels_flat == label]
        print(f'Class:{label_dict_inverse[label]}')
        print(f'Accuracy:{len(y_pred[y_pred == label])}/{len(y_true)}\n')


def evaluate(dataloader_val):
    model.eval()
    loss_val_total = 0
    predictions, true_vals = [], []
    for batch in tqdm(dataloader_val):
        batch = tuple(b.to(device) for b in batch)
        inputs = {'input_ids': batch[0],
                  'attention_mask': batch[1],
                  'labels': batch[2],
                  }

        with torch.no_grad():
            outputs = model(**inputs)

        loss = outputs[0]
        logits = outputs[1]
        loss_val_total += loss.item()

        logits = logits.detach().cpu().numpy()
        label_ids = inputs['labels'].cpu().numpy()
        predictions.append(logits)
        true_vals.append(label_ids)

    loss_val_avg = loss_val_total / len(dataloader_val)

    predictions = np.concatenate(predictions, axis=0)
    true_vals = np.concatenate(true_vals, axis=0)

    return loss_val_avg, predictions, true_vals


# BASIC DATA LOADING AND SPLITTING
df = pd.read_csv('../data/imba_IVMHCQ.csv')
df['text'] = df['text'].apply(lambda x: re.sub(r"http\S+", "", x))

text = df['text'].values
labels = df['label'].values

x_train, x_val, y_train, y_val = train_test_split(
    text,
    labels,
    test_size=0.1,
    random_state=69,
    stratify=labels
)


# ENCODING
tokenizer = BertTokenizer.from_pretrained(
    'bert-base-uncased',
    do_lower_case=True
)

enc_train = tokenizer.batch_encode_plus(
    x_train,
    add_special_tokens=True,
    return_attention_mask=True,
    padding=True,
    truncation=True,
    max_length=256,
    return_tensors='pt'
)

enc_val = tokenizer.batch_encode_plus(
    x_val,
    add_special_tokens=True,
    return_attention_mask=True,
    padding=True,
    truncation=True,
    max_length=256,
    return_tensors='pt'
)

inputids_train = enc_train['input_ids']
attmask_train = enc_train['attention_mask']
inputids_val = enc_val['input_ids']
attmask_val = enc_val['attention_mask']

dataset_train = TensorDataset(
    inputids_train,
    attmask_train,
    torch.tensor(y_train)
)

dataset_val = TensorDataset(
    inputids_val,
    attmask_val,
    torch.tensor(y_val)
)


# LOADING MODEL AND CREATING DATA LOADERS
model = BertForSequenceClassification.from_pretrained(
    'bert-base-uncased',
    num_labels=NUM_CLASSES,
    output_attentions=False,
    output_hidden_states=False
)


dataloader_train = DataLoader(
    dataset_train,
    sampler=RandomSampler(dataset_train),
    batch_size=BATCH_SIZE
)
dataloader_val = DataLoader(
    dataset_val,
    sampler=SequentialSampler(dataset_val),
    batch_size=BATCH_SIZE
)

optimizer = AdamW(
    model.parameters(),
    lr=LR,
    eps=1e-8
)
scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=0,
        num_training_steps=len(dataloader_train)*EPOCHS
)

seed_val = 69
random.seed(seed_val)
np.random.seed(seed_val)
torch.manual_seed(seed_val)
torch.cuda.manual_seed_all(seed_val)

device = 'cpu'
model.to(device)


# TRAINING
for epoch in tqdm(range(1, EPOCHS + 1)):
    model.train()

    loss_train_total = 0

    progress_bar = tqdm(dataloader_train,
                        desc='Epoch {:1d}'.format(epoch),
                        leave=False,
                        disable=False)

    for batch in progress_bar:
        model.zero_grad()
        batch = tuple(b.to(device) for b in batch)
        inputs = {
            'input_ids': batch[0],
            'attention_mask': batch[1],
            'labels': batch[2]
        }
        outputs = model(**inputs)
        loss = outputs[0]
        loss_train_total += loss.item()
        loss.backward()

        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        scheduler.step()
        progress_bar.set_postfix(
            {'training_loss': '{:.5f}'.format(loss.item() / len(batch))})

    # torch.save(model.state_dict(), f'../models/BERT_IVMHCQ_imba_epoch{epoch}.model')
    tqdm.write(f'\nEpoch {epoch}')

    loss_train_avg = loss_train_total / len(dataloader_train)
    tqdm.write(f'Training loss: {loss_train_avg}')

    val_loss, predictions, true_vals = evaluate(dataloader_val)
    val_f1 = f1_score_func(predictions, true_vals)
    tqdm.write(f'Validation {val_loss}')
    tqdm.write(f'F1 Score (weigthed): {val_f1}')

# torch.save(model.state_dict(), f'../models/BERT_IVMHCQ_imba.model')
