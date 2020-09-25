import pandas as pd

# df = pd.read_excel('1.xlsx')
df = pd.DataFrame({"Column 1": ["A", "B", "C", "D"], "Column 2": ["E", "F", "G", "H"]})

df = pd.Series(df.values.ravel("F"))
# df.to_csv('sss.csv')
