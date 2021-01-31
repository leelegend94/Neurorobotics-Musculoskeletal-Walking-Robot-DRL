import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv("./history_test.csv")
df['smooth'] = df['Reward'].rolling(window=400).mean()
sns.lineplot(x=df.index,y="Reward",data=df)
sns.lineplot(x=df.index,y="smooth",data=df)
#sns.lineplot(x=df.index,y="Z",data=df)
plt.show()
