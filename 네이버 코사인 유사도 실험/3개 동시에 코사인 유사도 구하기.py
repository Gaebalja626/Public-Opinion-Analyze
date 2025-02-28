from itertools import combinations
from typing import List, Tuple
import glob
import numpy as np

# Load embeddings and names
embedding_paths = glob.glob("네이버 클로바 임베딩v2*")
names = [(x.split(".")[0]).split("_")[1] for x in embedding_paths]
res = []
for file_path in embedding_paths:
    with open(file_path, 'r', encoding="utf-8") as fp:
        res.append(np.array(eval(fp.readline())))

def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """Calculate cosine similarity between two vectors."""
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def calculate_centroid_similarity(embeddings: List[np.ndarray], num_vectors: int) -> List[Tuple]:
    """Calculate centroid similarity for combinations of embeddings with specified size."""
    results = []
    for combo in combinations(range(len(embeddings)), num_vectors):
        centroid = sum(embeddings[i] for i in combo) / num_vectors
        sims = [cosine_similarity(embeddings[i], centroid) for i in combo]
        avg_sim = sum(sims) / num_vectors
        results.append((combo, sims, avg_sim))
    return sorted(results, key=lambda x: -x[-1])

def display_centroid_similarities(results: List[Tuple], names: List[str]):
    """Display centroid similarity results in a formatted table."""
    for i, (indices, sims, avg_sim) in enumerate(results):
        name_str = ' '.join(f"{names[idx]:<20}\t" for idx in indices)
        sim_str = ' '.join(f"유사도_{j+1}={sim:.4f}" for j, sim in enumerate(sims))
        print(f"[{i}] {name_str} {sim_str} 평균={avg_sim:.4f}")

# Example usage: specify number of vectors (e.g., 3, 4, etc.)
num_vectors = 4
centroid_sim_results = calculate_centroid_similarity(res, num_vectors)
display_centroid_similarities(centroid_sim_results, names)