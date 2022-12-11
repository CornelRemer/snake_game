import os
from typing import List

import torch
from torch import nn, optim
from torch.nn import functional as torch_functional


class LinearQNet(nn.Module):
    def __init__(self, input_feature_size: int = 20, hidden_layer_size: int = 256, output_feature_size: int = 3):
        super().__init__()
        self._linear1 = nn.Linear(in_features=input_feature_size, out_features=hidden_layer_size)
        self._linear2 = nn.Linear(in_features=hidden_layer_size, out_features=output_feature_size)
        self.load()

    def forward(self, tensor):
        tensor = torch_functional.relu(input=self._linear1(tensor))
        tensor = self._linear2(tensor)
        return tensor

    def load(self, file_name: str = "model.pth") -> None:
        # ToDo: load and save does not seems to work...
        model_folder_path = "./model"
        file_name = os.path.join(model_folder_path, file_name)
        try:
            self.load_state_dict(torch.load(file_name))
        except FileNotFoundError:
            print("Model not found, create new one.")
        else:
            print("Model loaded.")

    def save(self, file_name: str = "model.pth") -> None:
        model_folder_path = "./model"
        if not os.path.exists(model_folder_path):
            os.makedirs(model_folder_path)
        file_name = os.path.join(model_folder_path, file_name)
        torch.save(self.state_dict(), file_name)


class QTrainer:
    def __init__(self, model: LinearQNet, learning_rate: float = 0.001, discount_rate: float = 0.9):
        self._model = model
        self._learning_rate = learning_rate
        self._discount_rate = discount_rate

        self._optimizer = optim.Adam(params=self._model.parameters(), lr=self._learning_rate)
        self._criterion = nn.MSELoss()

    def train_step(self, old_state: List[int], action: List[int], reward: int, new_state: List[int], game_over: bool):
        old_state_tensor = torch.tensor(data=old_state, dtype=torch.float)
        new_state_tensor = torch.tensor(new_state, dtype=torch.float)
        action_tensor = torch.tensor(action, dtype=torch.long)
        reward_tensor = torch.tensor(reward, dtype=torch.float)
        game_over_tensor = (game_over,)
        # ToDo: check game_over implementation

        if len(old_state_tensor.shape) == 1:
            old_state_tensor = torch.unsqueeze(input=old_state_tensor, dim=0)
            new_state_tensor = torch.unsqueeze(new_state_tensor, 0)
            action_tensor = torch.unsqueeze(action_tensor, 0)
            reward_tensor = torch.unsqueeze(reward_tensor, 0)

        # 1. predicted Q values with current state
        pred = self._model(old_state_tensor)

        target = pred.clone()
        for idx, _ in enumerate(game_over_tensor):
            Q_new = reward_tensor[idx]
            if not game_over_tensor[idx]:
                Q_new = reward_tensor[idx] + self._discount_rate * torch.max(self._model(new_state_tensor[idx]))
            target[idx][torch.argmax(action_tensor).item()] = Q_new

        # 2. Q_new = reward + gamma * max(next_predicted_Q_value) -> onyl do this if not game_over
        # pred.clone()
        # pred[argmax(action)] = Q_new
        self._optimizer.zero_grad()
        loss = self._criterion(target, pred)
        loss.backward()

        self._optimizer.step()
