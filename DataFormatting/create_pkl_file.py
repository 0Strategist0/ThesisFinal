"""
# Training

---------------------------------------------------------------------------------------------------------------------------------

Kye Emond

December 1, 2023

---------------------------------------------------------------------------------------------------------------------------------

A short script to extract relevant columns from a root file and convert them to pandas DataFrames in pickle files.
"""

# Imports
import uproot as ur

def main():
    ROOT_FILE_PATH = "/home/kye/projects/ctb-stelzer/kye/HWWTraining/Data/nTuples-cHj3-cHW-12M.root"
    SAVE_PATH = "/home/kye/Data/redone_cHW_events.pkl"

    # Load data from the root file
    with ur.open(ROOT_FILE_PATH) as file:
        events = file["HWWTree_emme"].arrays(library="pandas").copy()

    # Normalize the weights
    for name in events.columns:
        if "weight_" in name:
            events[name] *= events["weight"]

    # Select the weight and kinematic variable columns you want to keep
    cols_to_keep = list(events.columns[2:49]) + list(events.columns[79:88])
    events = events[cols_to_keep].copy()
    print("Finished with events")

    # Save
    events.to_pickle(SAVE_PATH)

if __name__ == "__main__":
    main()