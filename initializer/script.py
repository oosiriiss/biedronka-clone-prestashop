import requests
import json
import xml.etree.ElementTree as ET
import re
import os
import random
import urllib3

API_URL = 'https://localhost:443/api'
API_KEY = 'DBV8CNPPZLBCCREL5PHLQECG5AN9PSHY'
DEBUG = True

class PrestaShopImporter:
    def __init__(self, api_url, api_key):
        self.api_url = api_url
        self.session = requests.Session()
        self.session.auth = (api_key, '')
        self.session.verify = False
        
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        self.category_cache = {}
        self.features_cache = {}
        self.feature_values_cache = {}
        
        # 1. NA STARCIE POBIERAMY WSZYSTKIE DOSTEPNE JEZYKI
        self.languages = self._get_shop_languages()
        print(f"Wykryte języki w sklepie (ID): {self.languages}")

    def _get_shop_languages(self):
        """Pobiera listę ID wszystkich aktywnych języków w sklepie"""
        try:
            # Pobieramy tylko ID
            url = f"{self.api_url}/languages?display=[id]&filter[active]=1"
            response = self.session.get(url)
            root = ET.fromstring(response.content)
            
            ids = []
            for language in root.findall(".//language"):
                ids.append(language.find('id').text)
            
            if not ids:
                return ['1'] # Fallback
            return ids
        except Exception as e:
            print(f"Błąd pobierania języków: {e}")
            return ['1', '2'] # Fallback bezpieczny

    def _get_schema(self, resource) -> ET.Element:
        url = f"{self.api_url}/{resource}?schema=blank"
        response = self.session.get(url)
        if response.status_code != 200:
            raise Exception(f"Błąd schematu {resource}: {response.text}")
        return ET.fromstring(response.content)

    def _slugify(self, text):
        text = text.lower()
        replacements = {'ą':'a', 'ć':'c', 'ę':'e', 'ł':'l', 'ń':'n', 'ó':'o', 'ś':'s', 'ź':'z', 'ż':'z'}
        for k, v in replacements.items():
            text = text.replace(k, v)
        text = re.sub(r'[^a-z0-9]+', '-', text).strip('-')
        return text if text else 'produkt'

    def _fill_multilang(self, parent_element, tag_name, value):
        """
        Kluczowa funkcja: czyści domyślny tag języka i wstawia wartość
        dla WSZYSTKICH języków zdefiniowanych w sklepie.
        """
        node = parent_element.find(tag_name)
        if node is None:
            node = ET.SubElement(parent_element, tag_name)
        
        # Usuwamy stare wpisy (z schema=blank zazwyczaj jest jeden pusty)
        for child in list(node):
            node.remove(child)
            
        # Dodajemy wpis dla KAŻDEGO języka w sklepie
        for lang_id in self.languages:
            lang_node = ET.SubElement(node, 'language')
            lang_node.set('id', str(lang_id))
            # Konwersja na string i obsługa None
            lang_node.text = str(value) if value else ""

    def get_or_create_feature(self, name):
        if name in self.features_cache:
            return self.features_cache[name]

        print(f" -> Tworzenie cechy: {name}")
        root = self._get_schema('product_features')
        feature = root.find('product_feature')
        
        # Używamy multilang
        self._fill_multilang(feature, 'name', name)
        
        xml_str = ET.tostring(root, encoding='utf-8')
        response = self.session.post(f"{self.api_url}/product_features", data=xml_str)
        
        if response.status_code == 201:
            ret_xml = ET.fromstring(response.content)
            new_id = int(ret_xml.find('product_feature/id').text)
            self.features_cache[name] = new_id
            self.feature_values_cache[new_id] = {}
            return new_id
        return None

    def get_or_create_feature_value(self, feature_id, value_text):
        if feature_id in self.feature_values_cache:
            if value_text in self.feature_values_cache[feature_id]:
                return self.feature_values_cache[feature_id][value_text]

        print(f" -> Dodawanie wartości cechy: '{value_text}'")
        root = self._get_schema('product_feature_values')
        f_val = root.find('product_feature_value')
        f_val.find('id_feature').text = str(feature_id)
        
        # Używamy multilang
        self._fill_multilang(f_val, 'value', value_text)
        
        xml_str = ET.tostring(root, encoding='utf-8')
        response = self.session.post(f"{self.api_url}/product_feature_values", data=xml_str)
        
        if response.status_code == 201:
            ret_xml = ET.fromstring(response.content)
            new_id = int(ret_xml.find('product_feature_value/id').text)
            if feature_id not in self.feature_values_cache:
                self.feature_values_cache[feature_id] = {}
            self.feature_values_cache[feature_id][value_text] = new_id
            return new_id
        return None

    def create_category(self, name, parent_name=None):
        if name in self.category_cache:
            return self.category_cache[name]

        print(f"Tworzenie kategorii: {name}")
        parent_id = 2
        if parent_name and parent_name in self.category_cache:
            parent_id = self.category_cache[parent_name]

        root = self._get_schema('categories')
        category = root.find('category')
        category.find('active').text = '1'
        category.find('id_parent').text = str(parent_id)
        
        # Multilang dla nazwy i linku
        self._fill_multilang(category, 'name', name)
        self._fill_multilang(category, 'link_rewrite', self._slugify(name))
        
        pos = category.find('position')
        if pos is not None: category.remove(pos)

        response = self.session.post(f"{self.api_url}/categories", data=ET.tostring(root))
        if response.status_code == 201:
            tree = ET.fromstring(response.content)
            new_id = int(tree.find('category/id').text)
            self.category_cache[name] = new_id
            return new_id
        return None

    def create_product(self, product_data):
        print(f"Dodawanie produktu: {product_data.get('title', 'Bez nazwy')}")
        
        cat_path = product_data.get('absolute_path', '').split('/')
        category_id = 2 
        if len(cat_path) > 1:
            cat_name = cat_path[-2]
            category_id = self.category_cache.get(cat_name, 2)

        price_raw = product_data.get('price', '0').replace(' PLN', '').replace(' zł', '').replace(',', '.').strip()
        try:
            price = float(price_raw)
        except:
            price = 0.0

        root = self._get_schema('products')
        product = root.find('product')
        
        position_node = product.find('position_in_category')
        if position_node is not None: product.remove(position_node)

        product.find('price').text = str(price)
        product.find('active').text = '1'
        product.find('state').text = '1'
        product.find('available_for_order').text = '1'
        product.find('show_price').text = '1'
        product.find('id_category_default').text = str(category_id)
        product.find('id_tax_rules_group').text = '1' 
        product.find('type').text = 'simple'
        
        # --- SEKCJA MULTILANG ---
        # Teraz wypełniamy pola dla WSZYSTKICH języków naraz
        title = product_data.get('title', 'bez nazwy')
        self._fill_multilang(product, 'name', title)
        self._fill_multilang(product, 'link_rewrite', self._slugify(title))
        
        desc_html = ""
        for section in product_data.get('description_sections', []):
            desc_html += f"<h3>{section.get('header','')}</h3><p>{section.get('content','')}</p>"
        self._fill_multilang(product, 'description', desc_html)
        # -----------------------

        features_to_add = {}
        if 'brand' in product_data and product_data['brand']:
            features_to_add['Marka'] = product_data['brand']
        if 'packaging_details' in product_data and product_data['packaging_details']:
            features_to_add['Opakowanie'] = product_data['packaging_details']

        if features_to_add:
            associations = product.find('associations')
            pf_node = associations.find('product_features')
            if pf_node is None:
                pf_node = ET.SubElement(associations, 'product_features')
            
            for child in list(pf_node): pf_node.remove(child)

            for f_name, f_value_text in features_to_add.items():
                f_id = self.get_or_create_feature(f_name)
                if f_id:
                    v_id = self.get_or_create_feature_value(f_id, f_value_text)
                    if v_id:
                        feature_node = ET.SubElement(pf_node, 'product_feature')
                        ET.SubElement(feature_node, 'id').text = str(f_id)
                        ET.SubElement(feature_node, 'id_feature_value').text = str(v_id)

        associations = product.find('associations')
        categories_node = associations.find('categories')
        for child in list(categories_node): categories_node.remove(child)
        cat_node = ET.SubElement(categories_node, 'category')
        ET.SubElement(cat_node, 'id').text = str(category_id)

        response = self.session.post(f"{self.api_url}/products", data=ET.tostring(root))
        
        if response.status_code != 201:
            print(f"Błąd dodawania produktu: {response.text}")
            return

        new_xml = ET.fromstring(response.content)
        product_id = new_xml.find('product/id').text
        print(f" -> Sukces! ID: {product_id}")

        # losowanie ilosci 
        if random.random() < 0.20:
            qty = 0
            print(" -> Stan magazynowy: BRAK (wylosowano 0)")
        else:
            qty = random.randint(1, 10)
            print(f" -> Stan magazynowy: {qty} szt.")
            
        self._update_stock(product_id, qty)

        if 'images' in product_data:
            for img_path in product_data['images']:
                self._upload_image(product_id, os.path.join('../scraper/',img_path))

    def _update_stock(self, product_id, quantity):
        url = f"{self.api_url}/stock_availables?filter[id_product]={product_id}&display=full"
        response = self.session.get(url)
        if response.status_code != 200: return
        root = ET.fromstring(response.content)
        stock_node = root.find('stock_availables/stock_available')
        if stock_node is not None:
            stock_id = stock_node.find('id').text
            stock_node.find('quantity').text = str(quantity)
            if stock_node.find('depends_on_stock') is not None:
                stock_node.find('depends_on_stock').text = '0'
            else:
                dos = ET.SubElement(stock_node, 'depends_on_stock'); dos.text = '0'
            new_root = ET.Element('prestashop')
            new_root.set('xmlns:xlink', "http://www.w3.org/1999/xlink")
            new_root.append(stock_node)
            self.session.put(f"{self.api_url}/stock_availables/{stock_id}", data=ET.tostring(new_root))

    def _upload_image(self, product_id, image_path):
        if not os.path.exists(image_path): return
        files = {'image': ('image.jpg', open(image_path, 'rb'), 'image/jpeg')}
        self.session.post(f"{self.api_url}/images/products/{product_id}", files=files)


importer = PrestaShopImporter(API_URL, API_KEY)

print("--- Import Kategorii ---\n")
if os.path.exists('../scraper/categories.jsonl'):
    with open('../scraper/categories.jsonl', 'r', encoding='utf-8') as f:
        for line in f:
            data = json.loads(line)
            importer.create_category(data['name'], data['parent'])

print("--- Import Produktów ---")
if os.path.exists('../scraper/products.jsonl'):
    with open('../scraper/products.jsonl', 'r', encoding='utf-8') as f:
        for line in f:
            data = json.loads(line)
            importer.create_product(data)
