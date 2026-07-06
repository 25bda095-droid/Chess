import torch
import torch.nn as nn
import torch.nn.functional as F

class FeatureTransformer(nn.Module):
    """
    Feature Transformer for NNUE.
    Transforms sparse input features (like HalfKP or piece-square encodings)
    into a dense embedding representation.
    """
    def __init__(self, input_size: int, embedding_size: int):
        super(FeatureTransformer, self).__init__()
        self.linear = nn.Linear(input_size, embedding_size)

    def forward(self, x):
        # In NNUE, the feature transformer output is typically clipped
        # between 0.0 and 1.0 (Clipped ReLU)
        return torch.clamp(self.linear(x), 0.0, 1.0)


class NNUE(nn.Module):
    """
    Basic NNUE (Efficiently Updatable Neural Network) scaffolding for chess evaluation.
    Architecture: Feature Transformer -> 2 Dense Layers -> 1 Output Layer.
    """
    def __init__(self, input_size: int = 41024, embedding_size: int = 256, hidden_size: int = 32):
        super(NNUE, self).__init__()
        # Input size defaults to HalfKP size (approx 41024), but can be changed for simplified encodings.
        self.feature_transformer = FeatureTransformer(input_size, embedding_size)
        
        # We concatenate the embeddings for both perspectives (White and Black)
        # So the input to the first fully connected layer is 2 * embedding_size
        self.fc1 = nn.Linear(2 * embedding_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, 1)

    def forward(self, features_stm, features_nstm):
        """
        Forward pass for the NNUE evaluation.
        
        Args:
            features_stm: Features from the perspective of the side-to-move.
            features_nstm: Features from the perspective of the not-side-to-move.
        
        Returns:
            The raw evaluation score for the position.
        """
        # Transform features into embeddings
        embed_stm = self.feature_transformer(features_stm)
        embed_nstm = self.feature_transformer(features_nstm)
        
        # Concatenate the embeddings (side-to-move first)
        x = torch.cat([embed_stm, embed_nstm], dim=1)
        
        # Pass through dense layers
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        
        # Final evaluation output (raw score, no activation)
        out = self.fc3(x)
        return out
