import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv("./test.csv")
sns.lineplot(x=df.index,y="reward",data=df)
plt.show()
