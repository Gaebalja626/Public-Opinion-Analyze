import numpy as np
import glob
from itertools import combinations

embedding_paths = glob.glob("네이버 클로바 임베딩v2*")
names = [(x.split(".")[0]).split("_")[1] for x in embedding_paths]
res = []
for file_path in embedding_paths:
    with open(file_path, 'r', encoding="utf-8") as fp:
        res.append(np.array(eval(fp.readline())))

print(len(res[0]))

cos_sim_sorted = []
for combo in combinations(range(len(embedding_paths)), 2):
    a, b = combo
    cos_sim = (np.sum(res[a]*res[b])) / (np.linalg.norm(res[a]) * np.linalg.norm(res[b]))
    cos_sim_sorted.append((a,b,cos_sim))

cos_sim_sorted = sorted(cos_sim_sorted, key=lambda x: -x[-1])

for i, (a, b, cos_sim) in enumerate(cos_sim_sorted):
    print(f"[{i}] {names[a]:<20}\t{names[b]:<20}\t코사인 유사도 :\t{cos_sim:.4f}")

