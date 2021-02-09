import torch
import matplotlib.pyplot as plt
import os
import numpy as np
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

from ResidualLoss.dataset import cifar10_data_loader_train
from ResidualLoss.model import CIFAR_17

model = CIFAR_17().cuda()
model.eval()

evaluation_batch_size = 10000
evaluation_data_loader = cifar10_data_loader_train(batch_size=evaluation_batch_size, shuffle=False, loc="../../data")

# result_list = list()
# for i in range(50):
#     correct_list = list()
#     with torch.no_grad():
#         state_dict = torch.load('../CNN-l2-30/lower_10_back/%s.pt' % i)
#         model.load_state_dict(state_dict)
#
#         start_index = 0
#         for data, target in evaluation_data_loader:
#             data, target = data.cuda(), target.cuda()
#             output = model(data)
#
#             pred = output.argmax(dim=1)
#             correct = pred.eq(target)
#             correct_list.append(correct)
#     result_list.append(torch.hstack(correct_list).detach())
#     print(i)
#
# torch.save(torch.vstack(result_list), "./data/CNN-l2-30-lower_10-back-result_2.pt")

result_1 = torch.load("./data/CNN-l2-30-lower_10-result.pt")
result_2 = torch.load("./data/CNN-l2-30-lower_10-back-result_2.pt")
result = torch.vstack([result_1[19], result_2])
correct_num = result.sum(dim=1)

correct_for_train = torch.load("./data/CNN-l2-30-potential.pt")
train_result_list = list()
for idx in correct_for_train:
    train_result_list.append(result[:, idx])
train_result = torch.vstack(train_result_list)

plt.rcParams['figure.figsize'] = (12.0, 6.0)
# plt.rcParams['figure.dpi'] = 100

plt.title("Training Accuracy")
plt.plot([str(i) for i in range(51)], correct_num.detach().cpu())
plt.plot([str(i) for i in range(51)], train_result.sum(dim=0).detach().cpu())
plt.plot([str(i) for i in range(51)], [6449] * 51)
plt.legend(labels=['all_acc', 'train_acc', 'train_num'])
# plt.ylim(00, 7000)
plt.show()
plt.xlabel("epoch")
plt.ylabel("accuracy")

# torch.save(lst_2, "./data/CNN-l2-30-potential.pt")
# print(lst_1)
# print(len(lst_2))

