# Import Splinter, BeautifulSoup, and Pandas
from splinter import Browser
from bs4 import BeautifulSoup as bs
import pandas as pd
import datetime as dt
from webdriver_manager.chrome import ChromeDriverManager

def scrape_all():
    # Initiate headless driver for deployment
    #browser = Browser("chrome", executable_path="chromedriver", headless=True)
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=False)

    news_title, news_paragraph = mars_news(browser)

    # Run scraping functions 
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "hemispheres": hemispheres(browser),
        "last_modified": dt.datetime.now()
    }

    # Quit browser
    browser.quit()
    return data


def mars_news(browser):

    # Scrape Mars News
    
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)

    html = browser.html
    soup = bs(html, 'html.parser')

    
    try:
        slide = soup.find('li', class_='slide')
        news_title = slide.find("div", class_="content_title").text
        news_p = slide.find("div", class_="article_teaser_body").text

    except AttributeError:
        return None, None

    return news_title, news_p


def featured_image(browser):
    # Visit URL
    jpl_nasa_url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
    browser.visit(jpl_nasa_url)

    browser.find_by_tag('button')[1].click()
    
    html = browser.html
    imgages_soup = bs(html, 'html.parser')


    try:
        image = imgages_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None

    image_path = f'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/{image}'

    return image_path

def mars_facts():
    try:
        df = pd.read_html('http://space-facts.com/mars/')[0]

    except BaseException:
        return None

    df.columns = ['Description', 'Mars']
    df.set_index('Description', inplace=True)

    return df.to_html(classes="table table-striped")


def hemispheres(browser):
    url = (
        "https://astrogeology.usgs.gov/search/"
        "results?q=hemisphere+enhanced&k1=target&v1=Mars"
    )

    browser.visit(url)

    hemisphere_image_urls = []
    for i in range(4):
        browser.find_by_css("a.product-item h3")[i].click()
        hemi_data = scrape_hemisphere(browser.html)
        hemisphere_image_urls.append(hemi_data)
        browser.back()

    return hemisphere_image_urls


def scrape_hemisphere(html_text):
    hemi_soup = bs(html_text, "html.parser")

    try:
        title_elem = hemi_soup.find("h2", class_="title").get_text()
        sample_elem = hemi_soup.find("a", text="Sample").get("href")

    except AttributeError:
        title_elem = None
        sample_elem = None

    hemispheres = {
        "title": title_elem,
        "img_url": sample_elem
    }

    return hemispheres


if __name__ == "__main__":

    print(scrape_all())
