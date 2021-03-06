import random
import string
import sys

import numpy as np
from torch.backends import cudnn
import torch
from torch.utils.data import Dataset, DataLoader

from ResidualLoss.dataset import cifar10_data_loader_train, cifar10_dataset_train, L2Dataset
from ResidualLoss.model import CIFAR_17


def setup_seed(seed):
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.cuda.manual_seed(seed)
    np.random.seed(seed)
    random.seed(seed)
    cudnn.deterministic = True


setup_seed(1914)
batch_size = 100

# model_before = CIFAR_17().cuda()
# state_dict = torch.load('./CIFAR-17-1.pt')
# model_before.load_state_dict(state_dict)
# model_before.eval()
# correct_before_sum = 0
#
# train_data_loader = cifar10_data_loader_train(batch_size)
# for data, target in train_data_loader:
#     data, target = data.view(data.size(0), -1).cuda(), target.cuda()
#
#     output_before, features = model_before.features(data)
#
#     for i in features:
#         print(i.shape)
#
#     break
# alpha = 0.01
# priority = 0.06
# print("./CNN-l2-freeze-upperbound/alpha-%s-p-%s.pt" % (alpha, priority))

new_dataset = L2Dataset(cifar10_dataset_train())

new_dataloader = DataLoader(new_dataset, batch_size=2, shuffle=False)

for idx, data in enumerate(new_dataloader):
    print(data)
    new_dataset.l2_ref[3] = torch.ones(8)
    print(1 < new_dataset.l2_loss[0])
    if idx > 1:
        break
