import json
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

data_path = "C:/Users/eleftheriou/Desktop/train_data/llm_batched_data"

def read_data(data_path):
    names = []
    examples = []
    objects = []
    for folder in os.listdir(data_path):
        if folder.endswith(".zip") or folder.endswith(".py") or folder.endswith(".csv") or folder=="lower_level_tasks":
            continue
        for ex in os.listdir(os.path.join(data_path, folder)):
            names.append(ex)
            with open(os.path.join(data_path, folder, ex), mode="r", encoding="utf-8") as f:
                data = json.load(f)
            examples.append(data)
            objects.append(data["output"]["objects"])
    return names, examples, objects

def extract_object_types(objects_in_example):
    return [obj["type"] for obj in objects_in_example]

names, examples, objects = read_data(data_path)
object_types = list(map(extract_object_types, objects))

df = pd.DataFrame({
    "bundle":names,
    "object":object_types
    })

df_exploded = df.explode("object")

df_exploded["count"] = 1
df_stats = df_exploded.groupby(["bundle", "object"]).count().reset_index()
sns.barplot(df_stats, x="object", y="count")
plt.show()

objects_df = df_stats[["object", "count"]].groupby("object").agg(
    average = pd.NamedAgg("count", "mean"),
    std_deviation = pd.NamedAgg("count", "std"),
    median = pd.NamedAgg("count", "median")
).reset_index().sort_values(by="median", ascending=False)
objects_df.to_csv("C:/Users/eleftheriou/Desktop/train_data/llm_batched_data/data_stats.csv", index=False)