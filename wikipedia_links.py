# Importting necessary libraries
from os import link
import requests
import pandas as pd
from bs4 import BeautifulSoup
import urllib

# Return random Wikipedia article
def get_random_article() -> str:
    url = f"https://en.wikipedia.org/api/rest_v1/page/random/html"

    response = requests.get(url)

    if response.status_code == 200:
        return response.content
    else:
        print(f"Error: {response.status_code}")


# Return an Wikipedia article, given its title
def get_article(title: str) -> str:
    url = f"https://en.wikipedia.org/api/rest_v1/page/html/{title}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        print(f"Error: {response.status_code} ({title})")

# Parse the HTML of an article and append the links to a dataframe
def parse_article(df: pd.DataFrame, article: str) -> None:
    df = df.copy()

    # Parsing the article
    soup = BeautifulSoup(article, "html.parser")

    # Article title
    title = soup.find("link", {"rel": "dc:isVersionOf"})["href"].split("/")[-1]
    title = urllib.parse.unquote(title)

    # If article was already scraped, skip it
    if title in df["title"].values:
        print(f'Article "{title}" already scraped, skipping...\n')
        return df

    # Getting links articles with rel "mw:WikiLink"
    links = soup.find_all("a", {"rel": "mw:WikiLink"})
    links = [link.get("href")[2:] for link in links]

    # Printing article title and number of links
    print(f"> {title} ({len(links)} links)")

    # Appending article title with each link to dataframe
    for link in set(links):
        df = df.append({"title": title, "link": link}, ignore_index=True)

    return df


# Creating a dataframe with article title and link columns
df = pd.DataFrame(columns=["title", "link"])

# Number of random articles to be scraped
NUM_RANDOM_ARTICLES = 4

# Scraping random articles
for i in range(NUM_RANDOM_ARTICLES):
    # Showing progress
    print(f"Random article {i+1}/{NUM_RANDOM_ARTICLES}")
    
    article = get_random_article()
    df = parse_article(df, article)

# Scraped links tracking
scraped_links = []

# Number of iterations
NUM_ITERATIONS = 5

# Number of links to be scraped per iteration
NUM_LINKS_PER_ITERATION = 4

for i in range(NUM_ITERATIONS):
    # Showing progress
    print(f"\nIteration {i+1}/{NUM_ITERATIONS}\n")

    # Get count of each link
    links = df.groupby("link").size().reset_index(name="count")

    # Filter links that were already scraped
    links = links[~links["link"].isin(df["title"].values)]
    links = links[~links["link"].isin(scraped_links)]

    # Get links with most occurrences
    links = links.sort_values("count", ascending=False).head(NUM_LINKS_PER_ITERATION)

    # Scraping articles
    for index, row in links.reset_index().iterrows():
        # Showing progress
        print(f"Article {index+1}/{len(links)}")

        link = row["link"]

        article = get_article(link)
        df = parse_article(df, article)

        scraped_links.append(link)


# Saving the dataframe to a csv file named "wikipedia_links.csv"
df.to_csv("wikipedia_links.csv", index=False)
