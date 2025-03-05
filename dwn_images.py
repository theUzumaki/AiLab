from icrawler.builtin import GoogleImageCrawler

google_Crawler = GoogleImageCrawler(storage={"root_dir": r"bulbasaur"})
google_Crawler.crawl(keyword="bulbasaur", max_num=50)
