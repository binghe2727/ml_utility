# inference on roberta
import torch
from tqdm import tqdm
import numpy as np

# inference on the dataset
def get_predictions(model, dataloader, device):
    softmax = torch.nn.Softmax(dim=1)
    model.eval()
    predictions = []
    for batch in tqdm(dataloader):
        #b_input_ids, b_input_mask, b_token_type = batch
        b_input_ids, b_input_mask = batch
        with torch.no_grad():
#             outputs = model(b_input_ids.to(DEVICE),
#                             token_type_ids=b_token_type.to(DEVICE),
#                             attention_mask=b_input_mask.to(DEVICE))
            outputs = model(b_input_ids.to(device), attention_mask=b_input_mask.to(device))
            b_proba = outputs[0]
            b_proba = softmax(b_proba)
            proba = b_proba.detach().cpu().numpy()
            predictions += [proba]
    flat_predictions = np.concatenate(predictions, axis=0)
    predictions = np.argmax(flat_predictions, axis=1).flatten()
    return flat_predictions[:,1].tolist(), predictions