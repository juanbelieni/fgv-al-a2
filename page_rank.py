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

# Lowercase all titles and links
df["title"] = df["title"].str.lower()
df["link"] = df["link"].str.lower()

# Remove rows that have titles that no other articles link to
df = df[df["title"].isin(df["link"])]

# Remove rows not linking to titles in the list
df = df[df["link"].isin(df["title"])]

# Create list of article titles, sorted alphabetically
titles = sorted(df["title"].unique())

print(f"Data imported: {len(titles)} articles")
print(f"\nCreating adjacency matrix...")

# Adjacency matrix
# Create n*nx3 adjacency matrix from dataframe
n = len(titles)
adjacencies = np.zeros((n * n, 3))
adjacencies[:, 0] = np.arange(n * n)
adjacencies[:, 1] = np.arange(n * n) % n

# Set count for each link in adjacency matrix
for title in titles:
    i = titles.index(title)

    # Show progress
    if i % 100 == 0 or i == n - 1:
        print(f"{i + 1}/{n}")

    for _, row in df[df["title"] == title].iterrows():
        link = row["link"]

        if link in titles:
            j = titles.index(link)
            count = row["count"]

            adjacencies[i * n + j, 2] = count
        else:
            print(f"{link} not in titles")

# Create nxn transition matrix from adjacency matrix
transition = adjacencies[:, 2].reshape(n, n).T

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

print(f"Transition matrix created: {n}x{n}")
print("\nCalculating PageRank...")

# Add random noise to transition matrix
d = 0.6
transition = d * transition + (1 - d) / n

print(f"Transition matrix created: {n}x{n}")
print("\nCalculating page ranks...")

# Initialize page rank vector
page_rank = np.ones(n) / n

# Calculate page rank, by iterating over the transition matrix
for i in range(100):
    last_page_rank = page_rank
    page_rank = np.dot(transition, page_rank)

    # Check if page rank has converged
    if np.allclose(last_page_rank, page_rank):
        print(f"Converged after {i} iterations")
        print(f"Difference: {np.sum(np.abs(last_page_rank - page_rank))}")
        break

# Sort page rank vector
page_rank_sorted = np.argsort(page_rank)

# Print top 10 articles and their page rank as percentage
print("\nTop 20 articles:")
for i in range(20):
    title = titles[page_rank_sorted[-i - 1]]
    page_rank_percentage = round(page_rank[page_rank_sorted[-i - 1]] * 100, 2)
    print(f"{title} ({page_rank_percentage}%)")

# Associate page rank with titles in a dataframe
page_rank_df = pd.DataFrame({"title": titles, "page_rank": page_rank})

# Save page rank dataframe to csv
print("\nSaving page rank dataframe to csv...")
page_rank_df.to_csv("page_rank.csv", index=False)
