import pandas as pd

# sample DataFrame
data = {'A': [1, 2, 3, 4],
        'B': [5, 6, 7, 8]}

df = pd.DataFrame(data)

# apply exponential weighting
ewm_df1 = df.ewm(span=1).mean()
ewm_df2 = df.ewm(span=2).mean()
ewm_df3 = df.ewm(span=3).mean()

print("############################################")
print(ewm_df1)
print(ewm_df2)
print(ewm_df3)


ewm_df11 = df.ewm(alpha=0.3333).mean()
ewm_df22 = df.ewm(alpha=0.6666).mean()
ewm_df33 = df.ewm(alpha=0.9999).mean()

print("############################################")
print(ewm_df11)
print(ewm_df22)
print(ewm_df33)


ewm_df11 = df.ewm(com=0.3333).mean()
ewm_df22 = df.ewm(com=0.6666).mean()
ewm_df33 = df.ewm(com=0.9999).mean()

print("############################################")
print(ewm_df11)
print(ewm_df22)
print(ewm_df33)
