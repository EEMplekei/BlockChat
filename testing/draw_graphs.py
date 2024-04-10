from matplotlib import pyplot as plt
import numpy as np
import json

# Load data from the file
with open("output.txt", "r") as file:
	data = json.load(file)

def performance_scaling(data):
	keys = [key for key in list(data.keys()) if key.startswith('(5')]

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

	bars1 = ax1.bar(index, throughputs, bar_width, label='Throughput')
	bars2 = ax2.bar(index, block_times, bar_width, label='Block Time', color='#ff7f0f')

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
			ax.annotate(f"{round(height, 3)} {unit}",
						xy=(bar.get_x() + bar.get_width() / 2, height),
						xytext=(0, 3),
						textcoords="offset points",
						ha='center', va='bottom')

	add_labels(ax1, bars1, "trans/sec")
	add_labels(ax2, bars2, "s")

	plt.tight_layout()
	plt.show()

def node_scaling(data):
	# Extracting keys for 5 and 10 nodes
	keys_5_nodes = [key for key in data.keys() if key.startswith('(5')]
	keys_10_nodes = [key for key in data.keys() if key.startswith('(10')]

	# Throughput for different block sizes for 5 and 10 nodes
	throughputs_5_nodes = [data[key]["throughput"] for key in keys_5_nodes]
	throughputs_10_nodes = [data[key]["throughput"] for key in keys_10_nodes]
	blocktime_5_nodes = [data[key]["block_time"] for key in keys_5_nodes]
	blocktime_10_nodes = [data[key]["block_time"] for key in keys_10_nodes]
 
	# Extract block sizes for labeling
	block_sizes = [key.split(",")[1][:-1] for key in keys_5_nodes]
	x = np.arange(len(block_sizes))
 
	# Plotting
	fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6))
	bar_width = 0.20
	index = range(len(block_sizes))

	for i, (throughput, node_count) in enumerate(zip([throughputs_5_nodes, throughputs_10_nodes], [5, 10])):
		bars1 = ax1.bar(x - bar_width/2 + i*bar_width, throughput, bar_width, label=f'{node_count} nodes')
		for bar in bars1:
			ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f'{round(bar.get_height(), 2)} tx/s', ha='center', va='bottom', fontsize=8)

	for i, (block_time, node_count) in enumerate(zip([blocktime_5_nodes, blocktime_10_nodes], [5, 10])):
		bars2 = ax2.bar(x-bar_width/2+i*bar_width, block_time, bar_width, label=f'{node_count} nodes')
		plt.bar_label(bars2, fmt='{:,.3f} s', size=10)
  
	fig.suptitle(f'Throughput and block time scaling with block size and node count', weight='bold', size=14, color='black')
	ax1.set_xlabel('Block Size')
	ax1.set_ylabel('Throughput (trans/sec)')
	ax1.set_title('Throughput for different block sizes and node counts', weight='bold', size=12, color='black')
	ax1.set_xticks(index)
	ax1.set_xticklabels([f"{block_sizes[i]}" for i in range(len(block_sizes))])
	ax1.legend()

	ax2.set_xlabel('Block Size')
	ax2.set_ylabel('Block Time (s)')
	ax2.set_title('Block Time for different block sizes and node counts', weight='bold', size=12, color='black')
	ax2.set_xticks(index)
	ax2.set_xticklabels([f"{block_sizes[i]}" for i in range(len(block_sizes))])
	ax2.legend()

	plt.tight_layout()
	plt.show()

performance_scaling(data)
node_scaling(data)