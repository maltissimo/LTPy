filename = 'HWDocs/OBIS-LX/Obis_Commands.txt'

# Initialize an empty list to hold the parsed data
data = []

# Open the file and read lines
with open(filename, 'r') as file:
    lines = file.readlines()

# Process each line

# Process each line
for line in lines:
    # Remove any leading/trailing whitespace
    line = line.strip()

    # Split the line into parts
    parts = line.split()

    # Find the last element which is the numbers part
    numbers = parts[-1]

    # The first part is the command
    command = parts[0]

    # Everything in between is the description
    description = ' '.join(parts[1:-1])

    # Append the parsed parts as a list to the data list
    data.append([command, description, numbers])

# Print the result
for row in data:
    print(row)

outfile = "commandlist.txt"
with open(outfile, 'w') as file:
    out = ''
    for i in range
