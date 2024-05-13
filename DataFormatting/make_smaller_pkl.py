# Code to randomly make a smaller dataset from a given dataset with same overall normalization

import pandas as pd
import numpy as np

BIG_DATA_PATH = "/home/kye/Data/cHW_events.pkl"
SMALL_DATA_PATH = "/home/kye/Data/training_cHW_events.pkl"
NUM_TO_SAMPLE = 1000
SEED = 100 #+ 100

# Get the data to use to generate the smaller data
big_data = pd.read_pickle(BIG_DATA_PATH)

# Get a small sample
small_data = big_data[0:int(np.shape(big_data)[0] * 0.9)]#big_data.sample(n=NUM_TO_SAMPLE, random_state=SEED, axis=0)

# Iterate through the weights, renormalizing to make small_data weights the same normalization as big_data
big_norm = big_data["weight_sm"].sum()
small_norm = small_data["weight_sm"].sum()

for title in small_data.columns:
    if "weight" in title:
        small_data[title] *= big_norm / small_norm

# Verify that things work
print("shapes")
print(big_data.shape)
print(small_data.shape)

print("normalizations")
print((big_data.sum(axis=0) - small_data.sum(axis=0)) / big_data.sum(axis=0))

print("ratios")
print((big_data["weight_cHW_pos1p0"] / big_data["weight_sm"]).mean())
print((small_data["weight_cHW_pos1p0"] / small_data["weight_sm"]).mean())

# Save
small_data.to_pickle(SMALL_DATA_PATH)