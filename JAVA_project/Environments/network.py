import torch
import torch.nn as nn
import torch.nn.functional as F

class ActorCritic(nn.Module):
    def __init__(self, obs_dim, act_dim):
        super(ActorCritic, self).__init__()
        
        # Backbone CNN
        self.backbone = nn.Sequential(
            nn.Conv2d(1, 16, kernel_size=3, padding=1),  # (batch, 16, 10, 5)
            nn.ReLU(),
            nn.Conv2d(16, 32, kernel_size=3, padding=1), # (batch, 32, 10, 5)
            nn.ReLU(),
            nn.Flatten()                                 # (batch, 32*10*5)
        )
        backbone_out_dim = 32 * 10 * 5

        self.fc = nn.Sequential(
            nn.Linear(backbone_out_dim, 128),
            nn.ReLU(),
            nn.LayerNorm(128),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.LayerNorm(128),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.LayerNorm(64)
        )
        self.policy_head = nn.Linear(64, act_dim)
        self.value_head = nn.Linear(64, 1)

    def forward(self, x):
        # x shape: (batch, 50) oppure (batch, 10, 5)
        if x.dim() == 2 and x.shape[1] == 50:
            x = x.view(-1, 1, 10, 5)
        elif x.dim() == 1 and x.shape[0] == 50:
            x = x.view(1, 1, 10, 5)
        elif x.dim() == 2 and x.shape[1] == 10*5:
            x = x.view(-1, 1, 10, 5)
        elif x.dim() == 1 and x.shape[0] == 10*5:
            x = x.view(1, 1, 10, 5)
        # Ora x è (batch, 1, 10, 5)
        x = self.backbone(x)
        x = self.fc(x)
        return self.policy_head(x), self.value_head(x)

    def act(self, x):
        logits, value = self.forward(x)
        dist = torch.distributions.Categorical(logits=logits)
        action = dist.sample()
        return action.item(), dist.log_prob(action), dist.entropy(), value