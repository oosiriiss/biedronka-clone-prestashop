import requests
from bs4 import BeautifulSoup
import hashlib
import os
import re


def download_image(url, folder="data/images", filename="image.jpg"):
    os.makedirs(folder, exist_ok=True)

    response = requests.get(url, stream=True)
    response.raise_for_status()

    filepath = os.path.join(folder, filename)

    with open(filepath, "wb") as f:
        for chunk in response.iter_content(1024):
            f.write(chunk)

    return filepath


class Scraper:
    def __init__(self, base_url="https://google.com/"):
        self.base_url = base_url


    def get_html(self, subpage = "/"):
        if subpage.startswith("http"):
            url = subpage
        else:
            url = self.base_url.rstrip("/") + "/" + subpage.lstrip("/")
        
        response = requests.get(url)
        response.raise_for_status()
        return response.text


    def check_selector_exists(self, page_html, selector):
        soup = BeautifulSoup(page_html, "html.parser")
        element = soup.select_one(selector)

        return element is not None
    

    def get_subpages(self, subpage, container_selector, link_selector):
        """
        This function returns a dictionary:
            text: string,
            url: string
        """
        
        if subpage.startswith("http"):
            url = subpage
        else:
            url = self.base_url.rstrip("/") + "/" + subpage.lstrip("/")

        html = self.get_html(url)
        soup = BeautifulSoup(html, "html.parser")
        container = soup.select_one(container_selector)
        if not container:
            raise Exception(f"Container not found: {container_selector}")
        links = container.select(link_selector)

        result = []
        for a in links:
            url = a.get("href")
            text = a.get_text(strip=True)
            # If the path is relative, change it to the full
            if url and url.startswith("/"):
                url = self.base_url.rstrip("/") + url
            result.append({"text": text, "url": url})

        return result
    

    def get_number_of_subpages(self, subpage, pagination_container_selector):
        """
        This function returns a number of subpages by looking for all <a> tags, then finding the maximum number amoung them.
        """

        if subpage.startswith("http"):
            url = subpage
        else:
            url = self.base_url.rstrip("/") + "/" + subpage.lstrip("/")

        html = self.get_html(url)
        soup = BeautifulSoup(html, "html.parser")
        container = soup.select_one(pagination_container_selector)
        if not container:
            raise Exception(f"Container not found: {pagination_container_selector}")
        
        page_numbers = []
        for link in container.find_all('a'):
            text = link.get_text(strip=True)
            if text.isdigit():
                page_numbers.append(int(text))
        
        if not page_numbers:
            return 1
        
        return max(page_numbers)
    

    def get_all_items_from_paginated_container(self, subpage, container_selector, item_selector, pagination_selector):
        all_items = []
        total_pages = self.get_number_of_subpages(subpage, pagination_selector)

        for page in range(1, total_pages + 1):
            page_url = f"{subpage}?page={page}" if page > 1 else subpage
            items = self.get_all_items_from_container(page_url, container_selector, item_selector)
            all_items.extend(items)

        return all_items


    def get_all_items_from_container(self, subpage, container_selector, item_selector):
        if subpage.startswith("http"):
            url = subpage
        else:
            url = self.base_url.rstrip("/") + "/" + subpage.lstrip("/")

        html = self.get_html(url)
        soup = BeautifulSoup(html, "html.parser")

        container = soup.select_one(container_selector)
        if not container:
            print(f"Container not found: {container_selector}")
            return []

        items = container.select(item_selector)
        result = []

        for item in items:
            url = item.get("href")
            if url and url.startswith("/"):
                url = self.base_url.rstrip("/") + url
            result.append(url)

        return result


    def _get_text_from_element(self, page_html, text_selector):
        soup = BeautifulSoup(page_html, "html.parser")

        text = soup.select_one(text_selector).get_text(strip=True)

        return text
    

    def get_tag(self, page_html, tag_selector):
        soup = BeautifulSoup(page_html, "html.parser")

        return soup.select_one(tag_selector)
    

    def get_child_tag(self, parent_tag, tag_selector):
        return parent_tag.select_one(tag_selector)


    def get_child_tags(self, parent_tag, tag_selector):
        child_tags = parent_tag.select(tag_selector)

        return child_tags
    

    def get_attribute_of_tag(self, tag, attribute):
        return tag.get(attribute)
    
    def get_text_from_tag(self, tag):
        return tag.get_text(strip=True)


class BiedronkaScraper(Scraper):
    def __init__(self):
        super().__init__("https://zakupy.biedronka.pl")


    def get_categories(self):
        categories = self.get_subpages(
            subpage="/",
            container_selector="nav.header-navigation",
            link_selector="a.header-l1-item__link"
        )

        return categories
    
    def get_subcategories(self, category_page):
        subcategories = self.get_subpages(
            subpage=category_page,
            container_selector="div.refinement-category",
            link_selector="a.refinement-category__link"
        )

        for sub in subcategories:
            sub["text"] = re.sub(r'\s*\d+$', '', sub["text"])

        subcategories = [item for item in subcategories if item["text"] != "Wszystkie"]

        return subcategories
    
    def get_subsubcategories(self, category_page):
        """
        Sub sub categories may not exist for some sub categories.
        """
        category_page_html = self.get_html(category_page)
        if not self.check_selector_exists(category_page_html, "div.refinement-subcategory__wrapper"):
            # print("No sub sub categories found", category_page)
            return []
        
        subsubcategories = self.get_subpages(
            subpage=category_page,
            container_selector="ul.refinement-subcategory__list",
            link_selector="a.refinement-subcategory__link"
        )

        for sub in subsubcategories:
            sub["text"] = re.sub(r'\s*\d+$', '', sub["text"])
        
        subsubcategories = [item for item in subsubcategories if "Wszystkie" not in item["text"]]

        return subsubcategories

    
    def get_all_items_from_subcategory(self, subcategory_page):
        items = self.get_all_items_from_paginated_container(
            subpage=subcategory_page,
            container_selector="ul.product-grid.js-infinite-scroll-grid.tiles-container",
            item_selector="li.product-grid__item a.product-tile-clickable.js-product-link",
            pagination_selector="div.bucket-pagination__bucket"
        )

        return items
    
    def get_brand_of_item(self, item_html):
        return self._get_text_from_element(item_html, "span.product-description__brand")

    def get_title_of_item(self, item_html):
        return self._get_text_from_element(item_html, "h1.js-product-name.product-description__name")
    
    def get_packaging_details(self, item_html):
        return self._get_text_from_element(item_html, "div.packaging-details")
    
    def get_price_of_item(self, item_html):
        price_meta = self.get_tag(item_html, 'meta[itemprop="price"]')
        currency_meta = self.get_tag(item_html, 'meta[itemprop="priceCurrency"]')

        if price_meta and currency_meta:
            price = float(price_meta["content"])
            currency = currency_meta["content"]
            return f"{price} {currency}"
        
    def get_description_sections_of_item(self, item_html):
        """
        Returns a list of dict:
        {
            "header": str,
            "content": str
        }
        """
        main_div = self.get_tag(item_html, "div.js-pdp-description-main")
        container = self.get_child_tags(main_div, "div.product-description__section.ui-expandable")

        sections = []
        for section in container:
            header = self.get_child_tag(section, "h2.product-description__section-header.ui-expandable__header")
            content = self.get_child_tag(section, "div.product-description__section-body.ui-expandable__body")

            header = self.get_text_from_tag(header)
            content = self.get_text_from_tag(content)

            sections.append({
                "header": header,
                "content": content
            })

        return sections
    
    def download_images(self, item_html):
        images_path = "data/images"
        thumbnails_section_exists = self.check_selector_exists(item_html, "div.carousel-product-thumbnails")
        if not thumbnails_section_exists:
            main_img_container = self.get_tag(item_html, "div.carousel-product")
            img_tag = self.get_child_tag(main_img_container, "img")
            if img_tag is None:
                print("main image not found")
                return [f"{images_path}/no_image.jpg"]
            src = self.get_attribute_of_tag(img_tag, "data-srcset")
            image_name_bytes = src.encode("utf-8")
            hash_object = hashlib.md5(image_name_bytes)
            image_name = f"{hash_object.hexdigest()}.jpg"
            download_image(src, images_path, image_name)
            return [f"{images_path}/{image_name}"]
        
        
        thumbnails_container = self.get_tag(item_html, "div.carousel-product-thumbnails")

        slides = self.get_child_tags(thumbnails_container, "div.swiper-slide")
        paths = []
        for slide in slides:
            img_tag = self.get_child_tag(slide, "img")
            if img_tag is None:
                print("img_tag not found")
                continue

            src = self.get_attribute_of_tag(img_tag, "data-srcset")
            image_name_bytes = src.encode("utf-8")
            hash_object = hashlib.md5(image_name_bytes)
            image_name = f"{hash_object.hexdigest()}.jpg"
            download_image(src, images_path, image_name)
            paths.append(f"{images_path}/{image_name}")



scraper = BiedronkaScraper()

categories = scraper.get_categories()
categories.pop(0) # remove Polecane
for cat in categories:
    category_name = cat["text"]
    category_url = cat["url"]
    print (category_name, category_url)

    subcategories = scraper.get_subcategories(category_url)
    for subcat in subcategories:
        subcategory_name = subcat["text"]
        subcategory_url = subcat["url"]
        print("---", subcategory_name, subcategory_url)

        subsubcategories = scraper.get_subsubcategories(subcategory_url)
        if len(subsubcategories) == 0:
            # Process subcategories items
            for item in scraper.get_all_items_from_subcategory(subcategory_url):
                item_html = scraper.get_html(item)
                print(scraper.get_brand_of_item(item_html))
                print(scraper.get_title_of_item(item_html))
                print(scraper.get_packaging_details(item_html))
                print(scraper.get_description_sections_of_item(item_html))
                print(scraper.get_price_of_item(item_html))
                # scraper.download_images(item_html)
            pass
        else:
            for subsubcat in subsubcategories:
                subsubcategory_name = subsubcat["text"]
                subsubcategory_url = subsubcat["url"]
                print("------", subsubcategory_name, subsubcategory_url)

                for item in scraper.get_all_items_from_subcategory(subsubcategory_url):
                    item_html = scraper.get_html(item)
                    print(scraper.get_brand_of_item(item_html))
                    print(scraper.get_title_of_item(item_html))
                    print(scraper.get_packaging_details(item_html))
                    print(scraper.get_description_sections_of_item(item_html))
                    print(scraper.get_price_of_item(item_html))
                    # scraper.download_images(item_html)


# TODO: Add async
# TODO: Refactor
# TODO: Cache html