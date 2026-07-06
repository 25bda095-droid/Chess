import torch
import torch.nn as nn
import torch.nn.functional as F

class PolicyValueNetwork(nn.Module):
    """
    A simple AlphaZero-style Policy and Value network for self-play RL.
    It takes board features and outputs:
    1. A policy distribution over possible moves.
    2. A scalar value evaluation of the position.
    """
    def __init__(self, input_size: int = 41024, embedding_size: int = 256, hidden_size: int = 128, num_actions: int = 4672):
        super(PolicyValueNetwork, self).__init__()
        
        # Shared feature transformer (could use the HalfKP feature extractor)
        self.feature_extractor = nn.Linear(input_size, embedding_size)
        
        # Policy head
        self.policy_fc1 = nn.Linear(embedding_size, hidden_size)
        self.policy_fc2 = nn.Linear(hidden_size, num_actions)
        
        # Value head
        self.value_fc1 = nn.Linear(embedding_size, hidden_size)
        self.value_fc2 = nn.Linear(hidden_size, 1)

    def forward(self, x):
        """
        Forward pass for Policy and Value.
        
        Args:
            x: Input feature representation (e.g. from HalfKP).
        
        Returns:
            policy_logits: Logits for the action distribution.
            value: Scalar evaluation from -1 to 1.
        """
        # Transform features
        embed = torch.relu(self.feature_extractor(x))
        
        # Policy head
        p = torch.relu(self.policy_fc1(embed))
        policy_logits = self.policy_fc2(p)
        
        # Value head
        v = torch.relu(self.value_fc1(embed))
        value = torch.tanh(self.value_fc2(v))
        
        return policy_logits, value
