import json 

# Write the blocktime and throughtput with keys the pair (number of nodes,blocksize) to the output file as json format to be used by a script to make graph
def write_file(nodes, blocksize, blocktime, throughput):
    output_file = "output.txt"
    key = f"({nodes},{blocksize})"
    # Read existing contents from the file
    try:
        with open(output_file, "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {}

    # Update the data with new values
    data[key] = {'blocktime': blocktime, 'throughput': throughput}

    # Write the updated data back to the file
    with open(output_file, "w") as file:
        json.dump(data, file, indent=4)
