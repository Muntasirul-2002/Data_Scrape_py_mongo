import scrapy
from pathlib import Path
import datetime
from pymongo import MongoClient


client = MongoClient(
    "mongodb+srv://muntasirul:muntasirulmsd@cluster0.srzr9iy.mongodb.net/"
)

db = client.scrapy


def InsertToDb(page, title, rating, image, price, InStock):
    collection = db[page]
    doc = {
        "title": title,
        "rating": rating,
        "image": image,
        "price": price,
        "inStock": InStock,
        "date": datetime.datetime.now(tz=datetime.timezone.utc),
    }
    inserted = collection.insert_one(doc)
    return inserted.inserted_id


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["toscrape.com"]
    start_urls = ["https://toscrape.com"]

    def start_requests(self):
        urls = [
            "https://books.toscrape.com/catalogue/category/books/travel_2/index.html",
            "https://books.toscrape.com/catalogue/category/books/mystery_3/index.html",
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        page = response.url.split("/")[-2]
        filename = f"books-{page}.html"
        bookdetail = {}
        # Path(filename).write_bytes(response.body)
        self.log(f"Saved file {filename}")
        cards = response.css(".product_pod")
        for card in cards:
            title = card.css("h3>a::text").get()
            # print(title)

            rating = card.css(".star-rating").attrib["class"].split(" ")[1]
            # print(rating)

            image = card.css(".image_container img")
            image = image.attrib["src"].replace(
                "../../../../media", "https://books.toscrape.com/media"
            )
            # print(image.attrib["src"])

            price = card.css(".price_color::text").get()
            # print(price)

            availability = card.css(".availability::text")
            if len(availability.css(".icon-ok")) > 0:
                inStock = True
            else:
                inStock = False
                InsertToDb(page, title, rating, image, price, inStock)
