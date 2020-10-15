import random
from torch.autograd import Variable
from torch import optim

import numpy as np
from torch.backends import cudnn
import torch.nn.functional as F
import torch

from ResidualLoss.dataset import cifar10_data_loader_test, cifar10_data_loader_train
from ResidualLoss.model import CIFAR_16


def setup_seed(seed):
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.cuda.manual_seed(seed)
    np.random.seed(seed)
    random.seed(seed)
    cudnn.deterministic = True


setup_seed(1914)
num_epochs = 200
batch_size = 100
learning_rate = 0.0001
alpha = 0.0005


ref_model = CIFAR_16().cuda()
model = CIFAR_16().cuda()
state_dict = torch.load('./CIFAR-16-5723.pt')
ref_model.load_state_dict(state_dict)
ref_model.eval()
model.load_state_dict(state_dict)
model.train()

optimizer = optim.Adam(model.parameters(), lr=learning_rate, weight_decay=1e-5)

train_data_loader = cifar10_data_loader_train(batch_size)
test_data_loader = cifar10_data_loader_test(batch_size)


def residual_train():
    total_correct_sum = 0
    total_classification_loss = 0
    length = len(train_data_loader.dataset)
    for epoch in range(num_epochs):
        model.train()
        total_train_loss = 0
        total_correct = 0
        for data in train_data_loader:
            img, target = data
            img = Variable(img.view(img.size(0), -1)).cuda()

            optimizer.zero_grad()
            output, features = model.features(img)

            ref_output, ref_features = ref_model.features(img)
            ref_pred = ref_output.argmax(dim=1)
            ref_list = 2 * ref_pred.eq(target.cuda()).int() - 1

            loss1 = 0
            for i in range(len(features)):
                zeros = torch.zeros_like(features[i])
                dropped_ref_feature = torch.where(features[i] != 0, ref_features[i], zeros)
                sigmoided_dropped_ref_feature = torch.sigmoid(dropped_ref_feature).detach()
                sigmoided_feature = torch.sigmoid(features[i])

                temp_loss = F.binary_cross_entropy(sigmoided_feature, sigmoided_dropped_ref_feature, reduction='none').mean(dim=1)
                loss1 += (temp_loss * ref_list).sum()

            loss = F.nll_loss(output, target.cuda())
            loss += alpha * loss1

            loss.backward()
            optimizer.step()

            total_train_loss += F.nll_loss(output, target.cuda(), reduction='sum').item()  # sum up batch loss
            pred = output.argmax(dim=1, keepdim=True)  # get the index of the max log-probability
            total_correct += pred.eq(target.cuda().view_as(pred)).sum().item()

        total_train_loss /= length
        total_correct_sum += total_correct
        total_classification_loss += total_train_loss
        print('epoch [{}/{}], loss:{:.4f} Accuracy: {}/{}'.format(epoch + 1, num_epochs, total_train_loss, total_correct, length))
        test()
        # location = './states/CIFAR-12/' + str(2000+epoch) + '.pt'
        ref_model.load_state_dict(model.state_dict())

    print("average correct:", total_correct_sum / num_epochs)
    print("average loss:", total_classification_loss / num_epochs)


def test():
    model.eval()
    test_loss = 0
    correct = 0
    with torch.no_grad():
        for data, target in test_data_loader:
            data = data.view(data.size(0), -1).cuda()
            output = model(data)

            test_loss += F.nll_loss(output, target.cuda(), reduction='sum').item()  # sum up batch loss
            pred = output.argmax(dim=1)  # get the index of the max log-probability
            correct += pred.eq(target.cuda()).sum().item()

    test_loss /= len(test_data_loader.dataset)

    print('Test set: Average loss: {:.4f}, Accuracy: {}/{} ({:.0f}%)\n'.format(
        test_loss, correct, len(test_data_loader.dataset),
        100. * correct / len(test_data_loader.dataset)))


if __name__ == '__main__':
    residual_train()