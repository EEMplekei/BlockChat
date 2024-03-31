from matplotlib import pyplot as plt
import json

# Load data from the file
with open("output.txt", "r") as file:
    data = json.load(file)

keys = list(data.keys())[::-1]

# Extract corresponding values
block_times = [data[key]["block_time"] for key in keys]
throughputs = [data[key]["throughput"] for key in keys]

# Extract number of nodes and block size from keys for labeling
node_labels = [key.split(",")[0][1:] for key in keys]
blocksize_labels = [key.split(",")[1][:-1] for key in keys]

# Plotting
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10))

bar_width = 0.35
index = range(len(keys))

bars1 = ax1.bar(index, throughputs, bar_width, label='Throughput', color='c')
bars2 = ax2.bar(index, block_times, bar_width, label='Block Time', color='y')

ax1.set_xlabel('Number of Nodes, Block Size')
ax1.set_ylabel('Throughput')
ax1.set_title('Throughput for Each Node and Block Size combination')
ax1.set_xticks(index)
ax1.set_xticklabels([f"{node_labels[i]}, {blocksize_labels[i]}" for i in range(len(keys))], rotation=45)
ax1.legend()

ax2.set_xlabel('Number of Nodes, Block Size')
ax2.set_ylabel('Block Time')
ax2.set_title('Block Time for Each Node and Block Size combination')
ax2.set_xticks(index)
ax2.set_xticklabels([f"{node_labels[i]}, {blocksize_labels[i]}" for i in range(len(keys))], rotation=45)
ax2.legend()

# Function to add labels on bars
def add_labels(ax, bars):
    for bar in bars:
        height = bar.get_height()
        ax.annotate('{}'.format(round(height, 2)),
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom')

add_labels(ax1, bars1)
add_labels(ax2, bars2)

plt.tight_layout()
plt.show()
