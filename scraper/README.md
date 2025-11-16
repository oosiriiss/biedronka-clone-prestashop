# Biedronka Scraper

An **asynchronous scraper** for products from [Biedronka Online](https://zakupy.biedronka.pl), written in Python.

The scraper can:

* Retrieve all categories, subcategories, and sub-subcategories of products.
* Collect all products in a category (with pagination).
* Extract product details: name, brand, price, packaging, description.
* Download all product images with specific size, for example `sw=600` and `sh=600`.
* Save all data to JSONL for better performance on large datasets.
* Resume processing from the last processed product.

---

## Installation

* Python 3.12.3

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requriements.txt

python scraper.py
```

---

## How the Scraper Works

1. **Build Page Tree**

   ```python
   scraper = AsyncBiedronkaScraper()
   tree = await scraper.build_tree()
   tree.save("page_tree.json")
   ```

   * Fetches all categories and subcategories.
   * Creates a `PageTree` structure with product URLs.

2. **Process Products**

   ```python
   scraper.tree = PageTree.load("page_tree.json")
   await scraper.process_products_async(last_processed_path=None)
   ```

   * Iterates over all products in the tree.
   * Extracts product data:

     * `title` – product name
     * `brand` – brand
     * `price` – price
     * `packaging_details` – packaging
     * `description_sections` – product description sections

3. **Download Images**

   * Asynchronous downloading using a `Semaphore` to limit parallel downloads.
   * All images are downloaded with `sw=600` and `sh=600`.
   * Saved to `data/images`.
   * Save their paths to `images` list.

4. **Resume From Last Product**

   * You can resume scraping from the last processed product:

   ```python
   await scraper.process_products_async(last_processed_path="path/to/last/product")
   ```

5. **Save Data to JSON**

   * Instead of printing, the scraper saves data in JSONL:

   ```json
   [
       {
           "name": "Product 1",
           "url": "...",
           "title": "...",
           "brand": "...",
           "price": "...",
           "packaging_details": "...",
           "description_sections": [...],
           "images": ["data/images/xxx.jpg", "data/images/yyy.jpg"]
       },
       ...
   ]
   ```