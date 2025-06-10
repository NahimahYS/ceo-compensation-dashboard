import pandas as pd

df = pd.read_excel('Book1.xlsx')
print("Your column names are:")
print(df.columns.tolist())
print("\nFirst row of data:")
print(df.iloc[0])