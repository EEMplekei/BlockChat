from matplotlib import pyplot as plt
from colorama import Style
import json

# Load data from the file
with open("output.txt", "r") as file:
	data = json.load(file)

#For the first zhtoumeno
def performance_scaling(data):
	keys = [key for key in list(data.keys())[::-1] if key.startswith('(5')]

	#Throughput and Block Time for 5,10, 20 block size (5 nodes)
	throughputs = [data[key]["throughput"] for key in keys if key.startswith('(5')]
	block_times = [data[key]["block_time"] for key in keys if key.startswith('(5')]

	# Extract number of nodes and block size from keys for labeling
	blocksize_labels = [key.split(",")[1][:-1] for key in keys]

	# Plotting
	fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10))
	fig.suptitle(f'Throughput and block time scaling with block size (5 nodes deployment)', weight='bold', size=14, color='black')
 
	bar_width = 0.35
	index = range(len(keys))

	bars1 = ax1.bar(index, throughputs, bar_width, label='Throughput', color='c')
	bars2 = ax2.bar(index, block_times, bar_width, label='Block Time', color='y')

	ax1.set_xlabel('Block Size')
	ax1.set_ylabel('Throughput (trans/sec)')
	ax1.set_title('Throughput for different block sizes', weight='bold', size=12, color='black')
	ax1.set_xticks(index)
	ax1.set_xticklabels([f"{blocksize_labels[i]}" for i in range(len(keys))])
	ax1.legend()

	ax2.set_xlabel('Block Size')
	ax2.set_ylabel('Block Time (s)')
	ax2.set_title('Block Time for different block sizes', weight='bold', size=12, color='black')
	ax2.set_xticks(index)
	ax2.set_xticklabels([f"{blocksize_labels[i]}" for i in range(len(keys))])
	ax2.legend()

	# Function to add labels on bars
	def add_labels(ax, bars, unit):
		for bar in bars:
			height = bar.get_height()
			ax.annotate(f"{round(height, 2)} {unit}",
						xy=(bar.get_x() + bar.get_width() / 2, height),
						xytext=(0, 3),
						textcoords="offset points",
						ha='center', va='bottom')

	add_labels(ax1, bars1, "trans/sec")
	add_labels(ax2, bars2, "s")

	plt.tight_layout()
	plt.show()

#For the second zhtoumeno
def node_scaling(data):
	pass

performance_scaling(data)
node_scaling(data)