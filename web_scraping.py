import spacy
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from selenium.webdriver.chrome.options import Options
import pandas as pd
import re
import time

def scrape_product_details(search_term):
    # Set up the Chrome web driver options for all websites
    chrome_options = Options()
    chrome_options.add_argument("--headless")

    # Amazon Scraping
    amazon_driver = webdriver.Chrome(options=chrome_options)
    amazon_driver.get("https://www.amazon.in")
    amazon_search_box = WebDriverWait(amazon_driver, 20).until(EC.presence_of_element_located((By.ID, "twotabsearchtextbox")))
    amazon_search_box.clear()
    amazon_search_box.send_keys(search_term)
    time.sleep(2)  # Add a delay to allow the search term to be entered
    amazon_driver.find_element(By.ID, "nav-search-submit-button").click()
    amazon_products = WebDriverWait(amazon_driver, 20).until(EC.presence_of_all_elements_located((By.XPATH, '//div[@data-component-type="s-search-result"]')))

    amazon_product_names = []
    amazon_product_prices = []
    amazon_product_urls = []

    for product in amazon_products:
        if "Sponsored" not in product.text:
            names = product.find_elements(By.XPATH, ".//span[@class='a-size-medium a-color-base a-text-normal']")
            for name in names:
                amazon_product_names.append(name.text)

            try:
                if len(product.find_elements(By.XPATH, ".//span[@class='a-price-whole']")) > 0:
                    prices = product.find_elements(By.XPATH, ".//span[@class='a-price-whole']")
                    for price in prices:
                        amazon_product_prices.append(price.text)
                else:
                    amazon_product_prices.append("0")
            except:
                pass

            try:
                product_url = product.find_element(By.XPATH, ".//a[@class='a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal']").get_attribute("href")
                amazon_product_urls.append(product_url)
            except:
                amazon_product_urls.append("N/A")

    # Flipkart Scraping
    flipkart_driver = webdriver.Chrome(options=chrome_options)
    flipkart_driver.get("https://www.flipkart.com")
    flipkart_search_box = WebDriverWait(flipkart_driver, 20).until(EC.presence_of_element_located((By.NAME, "q")))
    flipkart_search_box.clear()
    flipkart_search_box.send_keys(search_term)
    flipkart_search_box.submit()
    WebDriverWait(flipkart_driver, 20).until(EC.presence_of_element_located((By.XPATH, "//div[@class='_1AtVbE']")))

    flipkart_product_names = [name.text for name in flipkart_driver.find_elements(By.XPATH, "//div[@class='_4rR01T']")]
    flipkart_product_prices = [price.text for price in flipkart_driver.find_elements(By.XPATH, "//div[@class='_30jeq3 _1_WHN1']")]
    flipkart_product_urls = [url.get_attribute("href") for url in flipkart_driver.find_elements(By.XPATH, "//a[@class='_1fQZEK']")]
    
    amazon_df = pd.DataFrame(zip(amazon_product_names, amazon_product_prices, amazon_product_urls, ['Amazon']*len(amazon_product_names)), columns=['product_name', 'product_price', 'product_url', 'website'])
    flipkart_df = pd.DataFrame(zip(flipkart_product_names, flipkart_product_prices, flipkart_product_urls, ['Flipkart']*len(flipkart_product_names)), columns=['product_name', 'product_price', 'product_url', 'website'])
    # Concatenate DataFrames into a single DataFrame
    combined_df = pd.concat([amazon_df, flipkart_df], ignore_index=True)

    # Close the web drivers
    amazon_driver.quit()
    flipkart_driver.quit()
    
    output_file_path = r"C:\Users\aadith\Desktop\alignment only\scraped_product_details.xlsx"
    combined_df.to_excel(output_file_path, index=False)
    print(f"Scraped product details from all websites have been saved to {output_file_path}")
  
    sorted_products = combined_df.sort_values(by='product_price', ascending=True)
    print(sorted_products)
    
    
    return combined_df