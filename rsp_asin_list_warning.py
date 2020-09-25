import pandas as pd
import glob


path = r"C:\Users\akmarmu\Documents\RSP asins"  # use your path
all_files = glob.glob(path + "/*.csv")

li = []

for filename in all_files:
    df = pd.read_csv(
        filename
    )
    li.append(df)

frame = pd.concat(li, axis=0, ignore_index=True)
frame.to_csv("combined.csv")
