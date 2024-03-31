import json
import matplotlib.pyplot as plt

# Load data from the file
with open("../output.txt", "r") as file:
    data = json.load(file)

# Extract keys and corresponding values
keys = list(data.keys())
blocktimes = [data[key]["blocktime"] for key in keys]
throughputs = [data[key]["throughput"] for key in keys]

# Extract number of nodes and block size from keys for labeling
node_labels = [key.split(",")[0][1:] for key in keys]
blocksize_labels = [key.split(",")[1][:-1] for key in keys]

# Plotting
plt.figure(figsize=(10, 6))
bar_width = 0.35
index = range(len(keys))

bars1 = plt.bar(index, blocktimes, bar_width, label='Block Time')
bars2 = plt.bar([i + bar_width for i in index], throughputs, bar_width, label='Throughput')

plt.xlabel('Number of Nodes, Block Size')
plt.ylabel('Value')
plt.title('Block Time and Throughput for Each Node and Block Size combination')
plt.xticks([i + bar_width / 2 for i in index], [f"{node_labels[i]}, {blocksize_labels[i]}" for i in range(len(keys))])
plt.legend()

# Function to add labels on bars
def add_labels(bars):
    for bar in bars:
        height = bar.get_height()
        plt.annotate('{}'.format(round(height, 2)),
                     xy=(bar.get_x() + bar.get_width() / 2, height),
                     xytext=(0, 3),
                     textcoords="offset points",
                     ha='center', va='bottom')

add_labels(bars1)
add_labels(bars2)

plt.tight_layout()
plt.show()
