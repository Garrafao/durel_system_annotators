import torch
import torch.nn as nn

class Model(nn.Module):
    def __init__(self, n_input_features):
        super(Model, self).__init__()
        self.l1 = nn.Linear(n_input_features, 100)
        self.relu = nn.ReLU()
        self.l2 = nn.Linear(100, 1)
        # self.l1 = nn.Linear(n_input_features, 1)

    def forward(self, x):
        out = self.l1(x)
        out = self.relu(out)
        out = self.l2(out)
        y_pred = torch.sigmoid(out)
        # y_pred = torch.sigmoid(self.l1(x))
        return y_pred