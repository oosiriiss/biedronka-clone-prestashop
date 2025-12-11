import json
import os
import aiohttp
import asyncio
import hashlib
import urllib.parse
import aiofiles
import re
from bs4 import BeautifulSoup
import logging


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class TreeNode:
    def __init__(self, name, url, absolute_path=None):
        self.name = name
        self.url = url
        self.children = []
        self._absolute_path = absolute_path or name

    @property
    def absolute_path(self):
        return self._absolute_path.lstrip("/")
    
    @absolute_path.setter
    def absolute_path(self, value):
        self._absolute_path = value

    def add_child(self, node):
        node.absolute_path = self.absolute_path + "/" + node.name
        self.children.append(node)

    def get_children(self):
        return self.children

    def is_leaf(self):
        return not self.children
    
    def to_dict(self):
        return {
            "name": self.name,
            "url": self.url,
            "absolute_path": self.absolute_path,
            "children": [ch.to_dict() for ch in self.children]
        }

    @staticmethod
    def from_dict(data):
        node = TreeNode(data["name"], data["url"], data.get("absolute_path"))
        node.children = [TreeNode.from_dict(ch) for ch in data.get("children", [])]
        return node

    

class PageTree:
    def __init__(self):
        self.root = TreeNode("", "")


    def add_page(self, absolute_path, page_name, page_url):
        parts = absolute_path.split("/") if absolute_path else []
        current_node = self.root

        for part in parts:
            child = next((ch for ch in current_node.get_children() if ch.name == part), None)

            if not child:
                logging.error(f"This branch does not exist {absolute_path}!")
                raise ValueError(f"Branch does not exist: {absolute_path}")

            current_node = child

        child_node = TreeNode(page_name, page_url)
        current_node.add_child(child_node)

        return child_node


    def dfs_leaves_after(self, func, last_processed_path=None):
        skip_node = None
        if last_processed_path:
            skip_node = self.root
            for part in last_processed_path.split("/"):
                skip_node = next((ch for ch in skip_node.get_children() if ch.name == part), None)
                if not skip_node:
                    raise ValueError(f"Last processed path not found: {last_processed_path}")

        found_skip = [skip_node is None]

        def _dfs(node):
            if node.is_leaf():
                if found_skip[0]:
                    func(node)
                elif node == skip_node:
                    found_skip[0] = True

            for ch in node.get_children():
                _dfs(ch)

        _dfs(self.root)


    def save(self, filepath):
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.root.to_dict(), f, ensure_ascii=False, indent=2)

    
    @staticmethod
    def load(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        tree = PageTree()
        tree.root = TreeNode.from_dict(data)
        return tree
    

class AsyncScraper:
    def __init__(self, base_url="https://google.com/"):
        self.base_url = base_url.rstrip("/")

    async def _fetch_html(self, url: str) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.text()

    def _parse_html(self, html: str):
        return BeautifulSoup(html, "html.parser")

    async def get_html(self, subpage="/") -> str:
        url = subpage if subpage.startswith("http") else f"{self.base_url}/{subpage.lstrip('/')}"
        return await self._fetch_html(url)

    async def check_selector_exists(self, page_html: str, selector: str) -> bool:
        soup = self._parse_html(page_html)
        return soup.select_one(selector) is not None

    async def get_subpages(self, subpage, container_selector, link_selector):
        url = subpage if subpage.startswith("http") else f"{self.base_url}/{subpage.lstrip('/')}"
        html = await self.get_html(url)
        soup = self._parse_html(html)
        container = soup.select_one(container_selector)
        if not container:
            raise ValueError(f"Container not found: {container_selector}")

        result = []
        for a in container.select(link_selector):
            href = a.get("href")
            text = a.get_text(strip=True)
            if href and href.startswith("/"):
                href = f"{self.base_url}{href}"
            result.append({"text": text, "url": href})

        return result

    async def get_number_of_subpages(self, subpage, pagination_container_selector) -> int:
        url = subpage if subpage.startswith("http") else f"{self.base_url}/{subpage.lstrip('/')}"
        html = await self.get_html(url)
        soup = self._parse_html(html)
        container = soup.select_one(pagination_container_selector)
        if not container:
            return 1

        page_numbers = [
            int(link.get_text(strip=True))
            for link in container.find_all('a')
            if link.get_text(strip=True).isdigit()
        ]
        return max(page_numbers, default=1)

    async def get_all_items_from_container(self, subpage, container_selector, item_selector):
        url = subpage if subpage.startswith("http") else f"{self.base_url}/{subpage.lstrip('/')}"
        html = await self.get_html(url)
        soup = self._parse_html(html)
        container = soup.select_one(container_selector)
        if not container:
            return []

        items = container.select(item_selector)
        result = []
        for item in items:
            href = item.get("href")
            if href and href.startswith("/"):
                href = f"{self.base_url}{href}"
            result.append(href)
        return result

    async def get_all_items_from_paginated_container(self, subpage, container_selector, item_selector, pagination_selector):
        total_pages = await self.get_number_of_subpages(subpage, pagination_selector)
        all_items = []
        for page in range(1, total_pages + 1):
            page_url = f"{subpage}?page={page}" if page > 1 else subpage
            items = await self.get_all_items_from_container(page_url, container_selector, item_selector)
            all_items.extend(items)
        return all_items


    def _get_text_from_element(self, page_html, text_selector):
        soup = self._parse_html(page_html)
        tag = soup.select_one(text_selector)
        return tag.get_text(strip=True) if tag else None

    def get_tag(self, page_html, tag_selector):
        soup = self._parse_html(page_html)
        return soup.select_one(tag_selector)

    def get_child_tag(self, parent_tag, tag_selector):
        return parent_tag.select_one(tag_selector)

    def get_child_tags(self, parent_tag, tag_selector):
        return parent_tag.select(tag_selector)

    def get_attribute_of_tag(self, tag, attribute):
        return tag.get(attribute)

    def get_text_from_tag(self, tag):
        return tag.get_text(strip=True)


semaphore = asyncio.Semaphore(5)
class AsyncBiedronkaScraper(AsyncScraper):
    def __init__(self):
        super().__init__("https://zakupy.biedronka.pl")
        self.tree = PageTree()

    async def get_categories(self):
        categories = await self.get_subpages("/", "nav.header-navigation", "a.header-l1-item__link")

        categories = [item for item in categories if item["text"] != "Polecane"]
        return categories

    async def get_subcategories(self, category_page):
        subcategories = await self.get_subpages(
            subpage=category_page,
            container_selector="div.refinement-category",
            link_selector="a.refinement-category__link"
        )

        for sub in subcategories:
            sub["text"] = re.sub(r'\s*\d+$', '', sub["text"])

        subcategories = [item for item in subcategories if item["text"] != "Wszystkie"]
        return subcategories

    async def get_subsubcategories(self, category_page):
        html = await self.get_html(category_page)
        exists = await self.check_selector_exists(html, "div.refinement-subcategory__wrapper")
        if not exists:
            return []

        subsubcategories = await self.get_subpages(
            subpage=category_page,
            container_selector="ul.refinement-subcategory__list",
            link_selector="a.refinement-subcategory__link"
        )

        for sub in subsubcategories:
            sub["text"] = re.sub(r'\s*\d+$', '', sub["text"])

        subsubcategories = [item for item in subsubcategories if "Wszystkie" not in item["text"]]
        return subsubcategories

    async def get_all_items_from_subcategory(self, subcategory_page):
        items = await self.get_all_items_from_paginated_container(
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
    

    async def download_images(self, item_html, session):
        images_path = "data/images"
        os.makedirs(images_path, exist_ok=True)

        async def download_image(url, folder, filename):
            async with semaphore:
                filepath = os.path.join(folder, filename)
                if not os.path.exists(filepath):
                    print(f"Pobieram obraz: {url}")
                    try:
                        headers = {"User-Agent": "Mozilla/5.0"}
                        async with session.get(url, headers=headers, timeout=10) as resp:
                            resp.raise_for_status()
                            content = await resp.read()
                            async with aiofiles.open(filepath, "wb") as f:
                                await f.write(content)
                        print(f"Zapisano obraz: {filepath}")
                    except Exception as e:
                        print(f"Błąd pobierania {url}: {e}")
                return filepath

        def set_sw_sh(url, size=600):
            """
            Ustawia parametry sw i sh w URL na podaną wartość.
            """
            parsed = urllib.parse.urlparse(url)
            query = urllib.parse.parse_qs(parsed.query)
            query["sw"] = [str(size)]
            query["sh"] = [str(size)]
            new_query = urllib.parse.urlencode(query, doseq=True)
            return urllib.parse.urlunparse(parsed._replace(query=new_query))

        # Sprawdzenie sekcji miniaturek
        thumbnails_exist = await self.check_selector_exists(item_html, "div.carousel-product-thumbnails")

        if not thumbnails_exist:
            main_img_container = self.get_tag(item_html, "div.carousel-product")
            img_tag = self.get_child_tag(main_img_container, "img")
            if img_tag is None:
                print("Main image not found")
                return [f"{images_path}/no_image.jpg"]

            src = self.get_attribute_of_tag(img_tag, "data-srcset")
            src = set_sw_sh(src)
            image_name = hashlib.md5(src.encode("utf-8")).hexdigest() + ".jpg"
            await download_image(src, images_path, image_name)
            return [f"{images_path}/{image_name}"]

        # Pobranie wszystkich miniaturek
        thumbnails_container = self.get_tag(item_html, "div.carousel-product-thumbnails")
        slides = self.get_child_tags(thumbnails_container, "div.swiper-slide")
        paths = []

        for slide in slides:
            img_tag = self.get_child_tag(slide, "img")
            if img_tag is None:
                continue

            src = self.get_attribute_of_tag(img_tag, "data-srcset")
            src = set_sw_sh(src)
            image_name = hashlib.md5(src.encode("utf-8")).hexdigest() + ".jpg"
            await download_image(src, images_path, image_name)
            paths.append(f"{images_path}/{image_name}")

        return paths


    

    async def build_tree(self):
        categories = await self.get_categories()
        for cat in categories:
            cat_node = self.tree.add_page("", cat["text"], cat["url"])
            subcats = await self.get_subcategories(cat["url"])
            for sub in subcats:
                sub_node = self.tree.add_page(cat_node.absolute_path, sub["text"], sub["url"])
                subsubcats = await self.get_subsubcategories(sub["url"])
                if subsubcats:
                    for subsub in subsubcats:
                        subsub_node = self.tree.add_page(sub_node.absolute_path, subsub["text"], subsub["url"])
                        items = await self.get_all_items_from_subcategory(subsub["url"])
                        for idx, item_url in enumerate(items, 1):
                            self.tree.add_page(subsub_node.absolute_path, f"Produkt {idx}", item_url)
                            logging.info("sub " + item_url)
                else:
                    items = await self.get_all_items_from_subcategory(sub["url"])
                    for idx, item_url in enumerate(items, 1):
                        self.tree.add_page(sub_node.absolute_path, f"Produkt {idx}", item_url)
                        logging.info(item_url)

        return self.tree
    

    async def process_products_async(self, last_processed_path=None):
        async with aiohttp.ClientSession() as session:
            async def process_node(node):
                try:
                    html = await self.get_html(node.url)
                    title = self.get_title_of_item(html)
                    brand = self.get_brand_of_item(html)
                    packaging_details = self.get_packaging_details(html)
                    price = self.get_price_of_item(html)
                    description_sections = self.get_description_sections_of_item(html)
                    paths = await self.download_images(html, session)
                    
                    product_data = {
                        "name": node.name,
                        "url": node.url,
                        "title": title,
                        "brand": brand,
                        "price": price,
                        "packaging_details": packaging_details,
                        "description_sections": description_sections,
                        "images": paths,
                        "absolute_path": node.absolute_path
                    }

                    # Zapis do pliku po każdym przetworzonym produkcie
                    with open("products.jsonl", "a", encoding="utf-8") as f:
                        f.write(json.dumps(product_data, ensure_ascii=False) + "\n")

                    print(f"{node.name}: {title}")
                    print(f"{node.name}: {brand}")
                    print(f"{node.name}: {price}")
                    print(f"{node.name}: {packaging_details}")
                    print(f"{node.name}: {description_sections}")
                    print(f"{node.name}: {paths}")
                    print(f"Przetworzono wezel: {node.absolute_path}")
                    print()
                except Exception as e:
                    print(f"Błąd przetwarzania {node.absolute_path}: {e}")

            # Zbierz wszystkie węzły do listy
            all_nodes = []
            def add_node(node):
                all_nodes.append(node)

            self.tree.dfs_leaves_after(add_node, last_processed_path=last_processed_path)

            BATCH_SIZE = 5
            for i in range(0, len(all_nodes), BATCH_SIZE):
                batch = all_nodes[i:i + BATCH_SIZE]
                tasks = [asyncio.create_task(process_node(n)) for n in batch]
                await asyncio.gather(*tasks)

    async def get_all_categories_jsonl(self, output_file="categories.jsonl"):
        categories = await self.get_categories()
        all_categories = []

        for cat in categories:
            cat_dict = {
                "name": cat["text"],
                "parent": None
            }
            all_categories.append(cat_dict)
            print(f"{cat_dict}")

            subcats = await self.get_subcategories(cat["url"])
            for sub in subcats:
                sub_dict = {
                    "name": sub["text"],
                    "parent": cat["text"]
                }
                all_categories.append(sub_dict)
                print(f"{sub_dict}")

                subsubcats = await self.get_subsubcategories(sub["url"])
                for subsub in subsubcats:
                    subsub_dict = {
                        "name": subsub["text"],
                        "parent": sub["text"]
                    }
                    all_categories.append(subsub_dict)
                    print(f"{subsub_dict}")

        with open(output_file, "w", encoding="utf-8") as f:
            for item in all_categories:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")


async def main():
    scraper = AsyncBiedronkaScraper()
    # tree = await scraper.build_tree()
    # tree.save("page_tree.json")
    #  scraper.tree = PageTree.load("page_tree.json")


    # await scraper.process_products_async()
    await scraper.get_all_categories_jsonl()

asyncio.run(main())









