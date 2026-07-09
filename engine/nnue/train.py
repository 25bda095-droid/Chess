import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from tqdm import tqdm

from network import NNUE
from features import HalfKPFeatures
from data_loader import create_pgn_dataloader

def train_model(model, dataloader, epochs=5, lr=1e-3, device='cpu'):
    """
    Dummy training loop for the NNUE model.
    """
    model.to(device)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)
    
    print(f"Starting training on {device}...")
    for epoch in range(epochs):
        model.train()
        total_loss = 0.0
        
        # Estimate total batches for ETA: ~65 positions per game across 200k games
        estimated_total_batches = (200000 * 65) // 4096 
        
        # Use tqdm for beautiful progress bars with ETA
        pbar = tqdm(dataloader, desc=f"Epoch [{epoch+1}/{epochs}]", total=estimated_total_batches, dynamic_ncols=True)
        
        for batch_idx, (feat_stm, feat_nstm, target) in enumerate(pbar):
            feat_stm, feat_nstm, target = feat_stm.to(device), feat_nstm.to(device), target.to(device)
            
            optimizer.zero_grad()
            
            # Forward pass
            output = model(feat_stm, feat_nstm)
            
            # Compute loss
            loss = criterion(output, target)
            
            # Backward pass and optimization
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            
            # Save checkpoint every 5000 batches
            if batch_idx > 0 and batch_idx % 5000 == 0:
                checkpoint_path = f"nnue_checkpoint_batch_{batch_idx}.pth"
                torch.save(model.state_dict(), checkpoint_path)
                
            # Update progress bar with the current loss
            pbar.set_postfix({'Loss': f"{loss.item():.4f}"})
            
        # We need to guard against batch_idx not being defined if dataloader is empty
        num_batches = batch_idx + 1 if 'batch_idx' in locals() else 1
        avg_loss = total_loss / num_batches
        print(f"Epoch [{epoch+1}/{epochs}] completed. Average Loss: {avg_loss:.4f}\n")
        
    print("Training completed. Saving final model...")
    torch.save(model.state_dict(), "nnue_base_model_final.pth")
    return model


if __name__ == "__main__":
    import os
    
    # Hyperparameters
    INPUT_SIZE = HalfKPFeatures.NUM_FEATURES # Uses 41024
    EMBEDDING_SIZE = 32
    HIDDEN_SIZE = 16
    BATCH_SIZE = 4096 # Optimal sweet spot for CPU parsing vs GPU speed
    EPOCHS = 1
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # 1. Instantiate the NNUE model
    model = NNUE(input_size=INPUT_SIZE, embedding_size=EMBEDDING_SIZE, hidden_size=HIDDEN_SIZE)
    # print(model) # Commented out to keep logs beautiful
    
    pgn_path = "/home/rishav/MY_PERSONAL_WORKS/MY_ALL_PROJECTS/chess/lichess_elite_2025-01.pgn"
    
    if os.path.exists(pgn_path):
        print(f"Found Lichess Elite Database! Creating real dataloader...")
        # Train on 200,000 games for a lightning fast 50-minute Base Training!
        dataloader = create_pgn_dataloader(pgn_path, batch_size=BATCH_SIZE, max_games=200000)
    else:
        raise FileNotFoundError(f"PGN file not found at {pgn_path}. Cannot train without data.")
    
    # 3. Train the model
    train_model(model, dataloader, epochs=EPOCHS, lr=1e-3, device=device)
