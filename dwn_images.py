from icrawler.builtin import GoogleImageCrawler
from concurrent.futures import ThreadPoolExecutor

# Read words from file
with open("pokedex.txt", "r", encoding="utf-8") as file:
    words = [line.strip() for line in file]

# Function to download images for a single word
def download_images(word):
    google_Crawler = GoogleImageCrawler(storage={"root_dir": fr"images/{word}"})
    google_Crawler.crawl(keyword=word, max_num=50)

def download_images_sprite(word):
    google_Crawler = GoogleImageCrawler(storage={"root_dir": fr"images/{word}"})
    google_Crawler.crawl(keyword=f"{word} sprite", max_num=50)

def download_images_anime(word):
    google_Crawler = GoogleImageCrawler(storage={"root_dir": fr"images/{word}"})
    google_Crawler.crawl(keyword=f"{word} anime", max_num=50)

# Use ThreadPoolExecutor for parallel execution
num_threads = 8  # Adjust the number of threads based on your system
with ThreadPoolExecutor(max_workers=num_threads) as executor:
    executor.map(download_images, words)
    executor.map(download_images_sprite, words)
    executor.map(download_images_anime, words)
