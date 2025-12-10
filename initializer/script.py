

import requests
import json
import xml.etree.ElementTree as ET
import re
import os
import random  

API_URL = 'https://localhost:443/api'
# Wygeneorwane w Admin panel -> Advanced parameters -> Webservice
API_KEY = '51VR8T48Q9QRPFLVC7CIX3R4AWI8DTAN'  
DEBUG = True

class PrestaShopImporter:
    def __init__(self, api_url, api_key):
        self.api_url = api_url
        self.session = requests.Session()
        self.session.auth = (api_key, '')
        self.session.verify = False  # Bez ssl
        
        # wylaczenie ostrzezenia
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        self.category_cache = {} 
        self.features_cache = {} 
        self.feature_values_cache = {} 

    def _get_schema(self, resource) -> ET.Element:
        """pobiera schemat XML"""
        url = f"{self.api_url}/{resource}?schema=blank"
        response = self.session.get(url)
        if response.status_code != 200:
            raise Exception(f"Błąd pobierania schematu dla {resource}: {response.text}")
        return ET.fromstring(response.content)

    def _slugify(self, text):
        text = text.lower()
        text = re.sub(r'[^a-z0-9]+', '-', text).strip('-')
        return text if text else 'produkt'

    def get_or_create_feature(self, name):
        """Zwraca ID feature o danej nazwie lub tworzy feautre"""
        if name in self.features_cache:
            return self.features_cache[name]

        print(f" -> Tworzenie nowej cechy: {name}")
        root = self._get_schema('product_features')
        feature = root.find('product_feature')
        feature.find('name').find('language').text = name
        
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
        """Zwraca ID wartości feature"""
        if feature_id in self.feature_values_cache:
            if value_text in self.feature_values_cache[feature_id]:
                return self.feature_values_cache[feature_id][value_text]

        print(f" -> Dodawanie wartości cechy: '{value_text}' (ID cechy: {feature_id})")
        root = self._get_schema('product_feature_values')
        f_val = root.find('product_feature_value')
        f_val.find('id_feature').text = str(feature_id)
        f_val.find('value').find('language').text = value_text
        
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
        category.find('link_rewrite').find('language').text = self._slugify(name)
        category.find('name').find('language').text = name
        
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
        print(f"Dodawanie produktu: {product_data.get('name', 'Bez nazwy')}")
        
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
        if position_node is not None:
            product.remove(position_node)

        product.find('price').text = str(price)
        product.find('active').text = '1'
        product.find('state').text = '1'
        product.find('id_category_default').text = str(category_id)
        product.find('id_tax_rules_group').text = '1' 
        product.find('type').text = 'simple'
        
        product.find('name').find('language').text = product_data.get('name', 'Produkt')
        product.find('link_rewrite').find('language').text = self._slugify(product_data.get('name', 'produkt'))
        
        desc_html = ""
        for section in product_data.get('description_sections', []):
            desc_html += f"<h3>{section.get('header','')}</h3><p>{section.get('content','')}</p>"
        product.find('description').find('language').text = desc_html

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
        
        if response.status_code != 200:
            print(f" -> BŁĄD pobierania stocku: {response.text}")
            return

        root = ET.fromstring(response.content)
        stock_node = root.find('stock_availables/stock_available')
        
        if stock_node is not None:
            stock_id = stock_node.find('id').text
            
            stock_node.find('quantity').text = str(quantity)
            
            if stock_node.find('depends_on_stock') is not None:
                stock_node.find('depends_on_stock').text = '0'
            else:
                dos = ET.SubElement(stock_node, 'depends_on_stock')
                dos.text = '0'
            
            new_root = ET.Element('prestashop')
            new_root.set('xmlns:xlink', "http://www.w3.org/1999/xlink")
            new_root.append(stock_node)
            
            put_response = self.session.put(f"{self.api_url}/stock_availables/{stock_id}", data=ET.tostring(new_root))
            
            if put_response.status_code == 200:
                print(f" -> Zaktualizowano stock do: {quantity} szt.")
            else:
                print(f" -> BŁĄD aktualizacji stocku (Kod {put_response.status_code}): {put_response.text}")
        else:
            print(" -> Nie znaleziono wpisu stock_available dla tego produktu.")


    def _upload_image(self, product_id, image_path):
        if not os.path.exists(image_path):
            return
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
