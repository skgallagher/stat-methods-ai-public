import numpy as np

def set_seeds(seed: int = 0):
    try:
        import torch
        torch.manual_seed(seed)
    except Exception:
        pass
    np.random.seed(seed)
