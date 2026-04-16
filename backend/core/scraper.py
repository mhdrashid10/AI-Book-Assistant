from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
from .models import Book
from .rag_utils import process_book

def scrape_books(pages=3, books_per_page=10):
    """
    Multi-page scraping with progress
    Default: 3 pages (30 books)
    """
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), 
        options=options
    )
    
    books_scraped = 0
    
    try:
        for page in range(1, pages + 1):
            url = f"https://books.toscrape.com/catalogue/page-{page}.html"
            print(f"📄 Scraping page {page}/{pages}...")
            
            driver.get(url)
            time.sleep(3)
            
            book_links = driver.find_elements(By.CSS_SELECTOR, "h3 a")[:books_per_page]
            
            for link in book_links:
                try:
                    book_url = link.get_attribute("href")
                    title = link.get_attribute("title")
                    
                    driver.get(book_url)
                    time.sleep(2)
                    
                    # Get description
                    try:
                        desc_elem = driver.find_element(By.CSS_SELECTOR, "div#product_description + p")
                        description = desc_elem.text
                    except:
                        description = "No description available."
                    
                    # Get rating
                    try:
                        rating_class = driver.find_element(By.CSS_SELECTOR, "p.star-rating").get_attribute("class")
                        rating = rating_class.split()[-1]
                        rating_map = {"One": 1.0, "Two": 2.0, "Three": 3.0, "Four": 4.0, "Five": 5.0}
                        rating_num = rating_map.get(rating, 3.0)
                    except:
                        rating_num = 3.0
                    
                    # Get price
                    try:
                        price = driver.find_element(By.CSS_SELECTOR, "p.price_color").text
                    except:
                        price = ""
                    
                    # Save book
                    book, created = Book.objects.get_or_create(
                        title=title,
                        defaults={
                            'author': 'Unknown Author',
                            'description': description,
                            'rating': rating_num,
                            'price': price,
                            'book_url': book_url
                        }
                    )
                    
                    if created or not book.summary:
                        process_book(book)
                    
                    books_scraped += 1
                    print(f"   ✅ Scraped: {title[:60]}...")
                    
                    driver.back()
                    time.sleep(1.5)
                    
                except Exception as e:
                    print(f"   ⚠️ Skipped a book: {e}")
                    continue
        
        print(f"\n🎉 Multi-page scraping completed! Total books scraped: {books_scraped}")
        return books_scraped
        
    finally:
        driver.quit()