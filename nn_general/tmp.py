# weighted loss function

import torch
from torch.nn import CrossEntropyLoss

'''
weighted loss during multi-class classification task
'''

def weighted_loss_computation(logits, num_labels, labels, device):

    weights = [1, 4] # [negative, positive]
    class_weight = torch.tensor(weights).float().to(device)
    clf_loss = CrossEntropyLoss(weight=class_weight)

    loss = clf_loss(logits.view(-1, num_labels), labels.view(-1))

    return loss