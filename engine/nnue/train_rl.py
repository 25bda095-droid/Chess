import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, IterableDataset
from tqdm import tqdm
import os
import chess
import random

from network import NNUE
from features import HalfKPFeatures
from data_loader import create_pgn_dataloader

# Hyperparameters
BATCH_SIZE = 4096
EPOCHS = 3  # Train 3 times over the RL dataset
LR = 1e-4    # Smaller learning rate for fine-tuning

class RLDataset(IterableDataset):
    def __init__(self, data_list):
        self.data_list = data_list
        
    def __iter__(self):
        random.shuffle(self.data_list)
        for fen, policy, value in self.data_list:
            board = chess.Board(fen)
            sparse = HalfKPFeatures.board_to_tensor(board)
            dense_tensor = sparse.to_dense()
            feat_white = dense_tensor[0]
            feat_black = dense_tensor[1]
            
            if board.turn == chess.WHITE:
                feat_stm = feat_white
                feat_nstm = feat_black
            else:
                feat_stm = feat_black
                feat_nstm = feat_white
                
            yield feat_stm, feat_nstm, torch.tensor([value], dtype=torch.float32)

def train_rl_with_replay():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("Loading RL Self-Play data from disk...")
    
    rl_data_path = os.path.join(os.path.dirname(__file__), '..', '..', 'rl_selfplay_data.pt')
    if not os.path.exists(rl_data_path):
        print("Data not found!")
        return

    rl_dataset_raw = torch.load(rl_data_path)
    # We want half a batch of RL data
    rl_dataloader = DataLoader(RLDataset(rl_dataset_raw), batch_size=BATCH_SIZE // 2)
    
    pgn_path = "/home/rishav/MY_PERSONAL_WORKS/MY_ALL_PROJECTS/chess/lichess_elite_2025-01.pgn"
    print("Loading Phase 1 Human Data for Experience Replay...")
    # Max games 20,000 is plenty for the replay buffer (it will reset if it runs out)
    human_dataloader = create_pgn_dataloader(pgn_path, batch_size=BATCH_SIZE // 2, max_games=20000)
    
    model = NNUE(input_size=HalfKPFeatures.NUM_FEATURES, embedding_size=32, hidden_size=16)
    model_path = os.path.join(os.path.dirname(__file__), '..', '..', 'nnue_base_model_final.pth')
    if os.path.exists(model_path):
        print("Loading Base Model for RL Fine-tuning...")
        model.load_state_dict(torch.load(model_path, map_location=device))
        
    model.to(device)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=LR)
    
    estimated_batches = len(rl_dataset_raw) // (BATCH_SIZE // 2)
    
    print("\nStarting RL Training Phase 2 with Experience Replay!")
    for epoch in range(EPOCHS):
        model.train()
        total_loss = 0.0
        
        human_iter = iter(human_dataloader)
        
        pbar = tqdm(rl_dataloader, desc=f"Epoch [{epoch+1}/{EPOCHS}]", total=estimated_batches)
        for rl_feat_stm, rl_feat_nstm, rl_target in pbar:
            try:
                human_feat_stm, human_feat_nstm, human_target = next(human_iter)
            except StopIteration:
                human_iter = iter(human_dataloader)
                human_feat_stm, human_feat_nstm, human_target = next(human_iter)
                
            # THE REPLAY BUFFER: Mix 50% RL data and 50% Human data together!
            feat_stm = torch.cat((rl_feat_stm, human_feat_stm), dim=0).to(device)
            feat_nstm = torch.cat((rl_feat_nstm, human_feat_nstm), dim=0).to(device)
            target = torch.cat((rl_target, human_target), dim=0).to(device)
            
            optimizer.zero_grad()
            output = model(feat_stm, feat_nstm)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            pbar.set_postfix({'Loss': f"{loss.item():.4f}"})
            
        print(f"Epoch [{epoch+1}/{EPOCHS}] Average Loss: {total_loss/(estimated_batches+1):.4f}\n")
        
    print("Saving Replay-enhanced superhuman model...")
    save_path = os.path.join(os.path.dirname(__file__), '..', '..', 'nnue_rl_model_final.pth')
    torch.save(model.state_dict(), save_path)
    print(f"Done! Model saved as '{save_path}'")

if __name__ == "__main__":
    train_rl_with_replay()
