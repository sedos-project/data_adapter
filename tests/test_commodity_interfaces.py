import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

# Define filename to analyse
name = 'sedos_set_io'

# choose option
# com_choice = 'secondary'
com_choice = 'all'

# Read the Excel file and process_set sheet
df = pd.read_excel(name+'.xlsx', sheet_name='Process_Set')

# Fill empty cells to facilitate logic - it is not considered as it has not one of the predefined category codes
df.fillna('dummytext', inplace=True)

# Filter out processes which impair the logic
df = df[~df['process'].str.contains('storage|transport|import|export')]

# Delete square brackets from dataframe
df['input'] = df['input'].str.replace(r'[][]', '', regex=True)
df['output'] = df['output'].str.replace(r'[][]', '', regex=True)

# Initialize dictionaries to store the commodities for each sector and category
sectors = ['pow', 'x2x', 'ind', 'mob', 'hea']
if com_choice == 'secondary':
    categories = ['sec']
else:
    categories = ['pri', 'sec', 'iip', 'exo']
cols = len(categories)

# Create plotting object
fig, axes = plt.subplots(nrows=1, ncols=cols, figsize=(cols*10, 16), sharey=False)
if len(categories) == 1:
    axes = [axes]  # Wrap the single AxesSubplot object in a list for indexing

# Initialize dictionaries to store the commodities for each sector
for i, category in enumerate(categories):
    input_commodities = {sector: set() for sector in sectors}
    output_commodities = {sector: set() for sector in sectors}

    # Iterate over the rows and populate the dictionaries
    for _, row in df.iterrows():
        row_sectors = [sector.strip()[0:3] for sector in row['process'].split(',')]
        categories_set = set([category.strip()[0:3] for category in row['input'].split(',') + row['output'].split(',')])
        for sector in row_sectors:
            if category in categories_set:
                input_commodities[sector] |= set([commodity.strip() for commodity in row['input'].split(',') if commodity.startswith(category)])
                output_commodities[sector] |= set([commodity.strip() for commodity in row['output'].split(',') if commodity.startswith(category)])

    # Create the matrix visualization for the current category
    combined = {sector: list(input_commodities[sector] | output_commodities[sector]) for sector in sectors}
    unique_commodity_list = sorted(list(set(commodity for sector in combined.values() for commodity in sector)))

    # Create a DataFrame with initial values of 0
    matrix_data = pd.DataFrame(np.NaN, index=unique_commodity_list, columns=sectors)

    # Update the DataFrame with -1 for input, 1 for output, and 0 for both
    for sector in sectors:
        for commodity in combined[sector]:
            if commodity in input_commodities[sector] and commodity in output_commodities[sector]:
                matrix_data.at[commodity, sector] = 0
            elif commodity in input_commodities[sector]:
                matrix_data.at[commodity, sector] = -1
            elif commodity in output_commodities[sector]:
                matrix_data.at[commodity, sector] = 1

    # Plot the matric information
    ax = axes[i]
    im = ax.imshow(matrix_data.values, cmap='RdYlGn', vmin=-1, vmax=1)

    # Create a frame around each cell in the matrix for better readability
    for j in range(len(matrix_data.index)):
        for k in range(len(matrix_data.columns)):
            value = matrix_data.values[j, k]
            color = 'white' if np.isnan(value) else 'red' if value == -1 else 'green' if value == 1 else 'yellow'
            rect = plt.Rectangle((k-0.5, j-0.5), 1, 1, fill=True, facecolor=color, edgecolor='black', linewidth=1)
            ax.add_patch(rect)

    # Labeling
    plt.sca(axes[i])
    ax.set_xticks(range(len(matrix_data.columns)), matrix_data.columns)
    ax.set_yticks(range(len(matrix_data.index)), matrix_data.index)
    ax.set_xlabel('Sectors', fontsize=12)
    ax.set_title(category.upper(), fontsize=16)

# Create a legend for the colors
legend_elements = [
    Patch(facecolor='white', edgecolor='black', label='No Relation'),
    Patch(facecolor='red', edgecolor='black', label='Input'),
    Patch(facecolor='green', edgecolor='black', label='Output'),
    Patch(facecolor='yellow', edgecolor='black', label='Input & Output')]
fig.legend(handles=legend_elements, loc='upper left', fontsize=12)
plt.tight_layout()

# Save the plot as svg
plt.savefig(name+'_'+com_choice+'_relations.svg', format='svg')
plt.show()

