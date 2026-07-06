import time
import torch
import chess
from network import NNUE
from features import HalfKPFeatures

def validate_speed(batch_size=1, test_iterations=10000, warmup_iterations=1000, use_real_features=True):
    print("=== NNUE Inference Speed Validation ===")
    
    # Instantiate the model
    print("Instantiating NNUE model...")
    model = NNUE()
    model.eval()
    
    input_size = HalfKPFeatures.NUM_FEATURES
    
    if use_real_features:
        print(f"Extracting features from initial chess board (batch_size={batch_size})...")
        board = chess.Board()
        sparse_features = HalfKPFeatures.board_to_tensor(board)
        dense_features = sparse_features.to_dense()
        
        # White to move in startpos
        feat_stm_single = dense_features[0].unsqueeze(0)
        feat_nstm_single = dense_features[1].unsqueeze(0)
        
        features_stm = feat_stm_single.repeat(batch_size, 1)
        features_nstm = feat_nstm_single.repeat(batch_size, 1)
    else:
        print(f"Generating dummy inputs (batch_size={batch_size}, input_size={input_size})...")
        features_stm = torch.randn(batch_size, input_size)
        features_nstm = torch.randn(batch_size, input_size)
    
    device = torch.device('cpu')
    model.to(device)
    features_stm = features_stm.to(device)
    features_nstm = features_nstm.to(device)
    
    print(f"Warming up ({warmup_iterations} iterations)...")
    with torch.no_grad():
        for _ in range(warmup_iterations):
            _ = model(features_stm, features_nstm)
            
    print(f"Running test ({test_iterations} iterations)...")
    start_time = time.time()
    
    with torch.no_grad():
        for _ in range(test_iterations):
            _ = model(features_stm, features_nstm)
            
    end_time = time.time()
    elapsed = end_time - start_time
    
    nodes_per_second = (test_iterations * batch_size) / elapsed
    
    print("-" * 30)
    print(f"Batch size : {batch_size}")
    print(f"Total nodes: {test_iterations * batch_size}")
    print(f"Time taken : {elapsed:.4f} seconds")
    print(f"Speed      : {nodes_per_second:.2f} nodes/sec")
    print("-" * 30)

if __name__ == "__main__":
    validate_speed(batch_size=1, test_iterations=10000, use_real_features=True)
    
    # Also test with batched evaluation, which might be useful for batched search or MCTS
    print("\nTesting batched evaluation:")
    validate_speed(batch_size=64, test_iterations=1000, use_real_features=True)
