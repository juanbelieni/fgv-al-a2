"""
PageRank algorithm implementation, with Wikipedia data.
"""

# Import libraries
import pandas as pd
import numpy as np

print("Importing data...")

# Import data
# Columns: title, link, count
df = pd.read_csv("wikipedia_links.csv")

# Create list of article titles, sorted alphabetically
titles = sorted(df["title"].unique())

# Remove rows not linking to titles in the list
df = df[df["link"].isin(titles)]

# Remove rows that have titles that no other articles link to
df = df[df["title"].isin(df["link"].unique())]

# Update titles list to match the new dataframe
titles = sorted(df["title"].unique())

print(f"Data imported: {len(titles)} titles and {len(df)} links")
print(f"\nCreating adjacency matrix...")

# Create n*nx3 adjacency matrix from dataframe
n = len(titles)
adjacencies = np.zeros((n * n, 3))

for i in range(n):
    for j in range(n):
        title = titles[i]
        link = titles[j]

        count = df[(df["title"] == title) & (df["link"] == link)]["count"]
        count = count.values[0] if len(count) > 0 else 0

        adjacencies[i * n + j, 0] = i
        adjacencies[i * n + j, 1] = j
        adjacencies[i * n + j, 2] = count

# Create nxn transition matrix from adjacency matrix
transition = adjacencies[:, 2].reshape(n, n)

print(f"Adjacency matrix created: {n*n}x3")
print("\nCreating transition matrix...")

# Transition matrix normalization
# Sum of each column
transition_sum = np.sum(transition, axis=0)

# Transform transition_sum into a diagonal matrix, and inverting it
transition_sum = np.diag(transition_sum)
transition_sum_inv = np.linalg.inv(transition_sum)

# Multiple transition matrix with the inverse of the diagonal matrix
transition = np.dot(transition, transition_sum_inv)

# Add random noise to transition matrix
d = 0.85
transition = d * transition + (1 - d) / n

print(f"Transition matrix created: {n}x{n}")
print("\nCalculating page ranks...")

# Initialize page rank vector
page_rank = np.ones(n) / n

# Calculate page rank, by iterating over the transition matrix
for i in range(100):
    page_rank = np.dot(transition, page_rank)

# Sort page rank vector
page_rank_sorted = np.argsort(page_rank)

# Print top 10 articles and their page rank as percentage
print("\nTop 10 articles:")
for i in range(10):
    title = titles[page_rank_sorted[-i - 1]]
    page_rank_percentage = round(page_rank[page_rank_sorted[-i - 1]] * 100, 2)
    print(f"{title} ({page_rank_percentage}%)")