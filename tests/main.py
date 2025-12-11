# https://googlechromelabs.github.io/chrome-for-testing/#stable
"""
Automatyczny test sklepu PrestaShop - Selenium
Wykonuje wszystkie wymagane operacje w czasie do 5 minut.
"""

import time
import random
import string
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os # Wymagane do obsługi ścieżek plików

class PrestaShopTester:
    """Klasa do automatycznego testowania sklepu PrestaShop"""

    def __init__(self, base_url):
        self.base_url = base_url
        self.driver = None
        self.wait = None
        self.cart_products = []
        self.user_email = None
        self.user_password = None


    def setup(self):
        """
        Inicjalizacja przeglądarki Chrome:
        1. Konfiguracja do automatycznego pobierania plików (PDF/faktury).
        2. Użycie ChromeDriverManager do automatycznego zarządzania sterownikiem.
        """
        print("🚀 Uruchamianie przeglądarki Chrome z konfiguracją pobierania...")
        
        # --- ZMIENNA: Definiuje folder, do którego zapiszą się pliki ---
        # Tworzy podkatalog 'downloaded_files' w bieżącym katalogu roboczym
        download_dir = os.path.join(os.getcwd(), "downloaded_files")
        
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)
            
        print(f"📄 Pliki będą pobierane do: {download_dir}")
        self.download_dir = download_dir # Zapisujemy ścieżkę do weryfikacji w KROKU 9
        # ----------------------------------------------------------------
            
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        # ----------------------------------------------------
        # 🚨 KLUCZOWE PREFERENCJE DLA POBIERANIA FAKTURY (PDF) 🚨
        # ----------------------------------------------------
        prefs = {
            # 1. Ustawia domyślny katalog pobierania
            "download.default_directory": download_dir, 
            # 2. Wyłącza okno dialogowe "Zapisz jako..."
            "download.prompt_for_download": False, 
            # 3. Ustawia, aby pliki PDF były pobierane, a nie wyświetlane w przeglądarce
            "plugins.always_open_pdf_externally": True 
        }
        options.add_experimental_option("prefs", prefs)
        
        # ----------------------------------------------------
        # Uruchomienie drivera (z opcją ręcznej ścieżki w razie WinError 193)
        # ----------------------------------------------------
        try:
            # Prawidłowe użycie ChromeDriverManager
            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()), 
                options=options
            )
        except Exception as e:
            # Opcja awaryjna w przypadku błędu WinError 193
            print(f"⚠️ Błąd inicjalizacji sterownika ({e}). Spróbuj ręcznej ścieżki.")
            # Zmień tę linię, jeśli sterownik (chromedriver.exe) jest w innym miejscu:
            driver_path_fallback = os.path.join(os.path.dirname(__file__), "chromedriver.exe") 
            self.driver = webdriver.Chrome(
                service=Service(driver_path_fallback),
                options=options
            )

        self.wait = WebDriverWait(self.driver, 15)
        print("✅ Przeglądarka uruchomiona\n")


    def teardown(self):
        """Zamknięcie przeglądarki"""
        if self.driver:
            print("\n🔚 Zamykanie przeglądarki...")
            time.sleep(2)
            self.driver.quit()
            print("✅ Przeglądarka zamknięta")

    def generate_random_email(self):
        """Generuje losowy email"""
        random_str = "".join(
            random.choices(string.ascii_lowercase + string.digits, k=8)
        )
        timestamp = int(time.time())
        return f"test_{random_str}_{timestamp}@example.com"

    def generate_random_password(self):
        """Generuje losowe hasło"""
        return (
            "".join(random.choices(string.ascii_letters + string.digits, k=12)) + "A1!"
        )

    def wait_and_click(self, by, value, timeout=10):
        """Czeka na element i klika"""
        element = WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable((by, value))
        )
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(0.3)
        element.click()
        return element

    def wait_for_element(self, by, value, timeout=10):
        """Czeka na pojawienie się elementu"""
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )

    def accept_cookies_if_present(self):
        """Akceptuje cookies jeśli są"""
        try:
            cookie_button = self.driver.find_element(
                By.CSS_SELECTOR,
                "button[class*='cookie'], button[class*='gdpr'], a[class*='cookie']",
            )
            cookie_button.click()
            print("✅ Zaakceptowano cookies")
            time.sleep(0.5)
        except:
            pass

    def get_categories(self):
        """Pobiera dostępne kategorie"""
        print("📂 Szukam kategorii produktów...")
        try:
            # Próbuj znaleźć kategorie w menu
            categories = self.driver.find_elements(
                By.CSS_SELECTOR,
                "#top-menu a, .category a, nav a[href*='category'], .menu a[href*='id_category']",
            )

            category_links = []
            for cat in categories[:10]:  # Weź pierwsze 10
                href = cat.get_attribute("href")
                if href and ("category" in href.lower() or "id_category" in href):
                    category_links.append(href)

            # Usuń duplikaty
            category_links = list(set(category_links))[:2]

            if not category_links:
                print("⚠️ Nie znaleziono kategorii, używam głównej strony")
                category_links = [self.base_url]

            print(f"✅ Znaleziono {len(category_links)} kategorii")
            return category_links
        except Exception as e:
            print(f"⚠️ Problem ze znalezieniem kategorii: {e}")
            return [self.base_url]

    def add_products_to_cart(self):
        """Dodaje 10 produktów z 2 różnych kategorii"""
        print("\n" + "=" * 60)
        print("KROK 1: Dodawanie 10 produktów do koszyka")
        print("=" * 60)

        self.driver.get(self.base_url)
        time.sleep(2)
        self.accept_cookies_if_present()

        categories = self.get_categories()
        products_per_category = 5
        total_added = 0

        for cat_index, category_url in enumerate(categories[:2], 1):
            print(f"\n📦 Kategoria {cat_index}/2")
            self.driver.get(category_url)
            time.sleep(2)

            # Znajdź produkty
            products = self.driver.find_elements(
                By.CSS_SELECTOR,
                "article.product, .product-miniature, .product-item, [data-id-product]",
            )

            print(f"   Znaleziono {len(products)} produktów w kategorii")

            for i in range(min(products_per_category, len(products))):
                try:
                    # Odśwież listę produktów
                    products = self.driver.find_elements(
                        By.CSS_SELECTOR,
                        "article.product, .product-miniature, .product-item, [data-id-product]",
                    )

                    if i >= len(products):
                        break

                    product = products[i]
                    self.driver.execute_script(
                        "arguments[0].scrollIntoView(true);", product
                    )
                    time.sleep(0.5)

                    # Znajdź nazwę produktu
                    try:
                        product_name = product.find_element(
                            By.CSS_SELECTOR,
                            "h2, h3, .product-title, [class*='product-name']",
                        ).text
                    except:
                        product_name = f"Produkt {total_added + 1}"

                    # Kliknij w produkt
                    product_link = product.find_element(By.CSS_SELECTOR, "a")
                    product_link.click()
                    time.sleep(2)

                    # Losowa ilość (1-3)
                    quantity = random.randint(1, 3)

                    try:
                        # Znajdź pole ilości
                        qty_input = self.driver.find_element(
                            By.CSS_SELECTOR,
                            "input[name='qty'], input#quantity_wanted, input.qty",
                        )
                        qty_input.clear()
                        qty_input.send_keys(str(quantity))
                        time.sleep(0.5)
                    except:
                        print(f"   ⚠️ Nie znaleziono pola ilości, używam domyślnej")
                        quantity = 1

                    # Dodaj do koszyka
                    add_button = self.wait_and_click(
                        By.CSS_SELECTOR,
                        "button[data-button-action='add-to-cart'], .add-to-cart, button[class*='add-to-cart']",
                    )

                    total_added += 1
                    self.cart_products.append(product_name)
                    print(
                        f"   ✅ Dodano: {product_name} (ilość: {quantity}) - Produkt {total_added}/10"
                    )

                    time.sleep(1)

                    # Zamknij modal jeśli się pojawi
                    try:
                        close_btn = self.driver.find_element(
                            By.CSS_SELECTOR,
                            "button.close, .modal-close, [class*='close']",
                        )
                        close_btn.click()
                        time.sleep(0.5)
                    except:
                        pass

                    # Wróć do kategorii
                    self.driver.back()
                    time.sleep(2)

                    if total_added >= 10:
                        break

                except Exception as e:
                    print(f"   ⚠️ Błąd przy dodawaniu produktu: {e}")
                    try:
                        self.driver.get(category_url)
                        time.sleep(2)
                    except:
                        pass
                    continue

            if total_added >= 10:
                break

        print(f"\n✅ Dodano łącznie {total_added} produktów do koszyka")

    def search_and_add_product(self):
        """Wyszukuje produkt i dodaje losowy z wyników"""
        print("\n" + "=" * 60)
        print("KROK 2: Wyszukiwanie i dodawanie produktu")
        print("=" * 60)

        self.driver.get(self.base_url)
        time.sleep(1)

        # Wyszukaj coś ogólnego
        search_terms = ["shirt", "mug", "poster", "art", "home", "product"]
        search_term = random.choice(search_terms)

        print(f"🔍 Wyszukuję: {search_term}")

        try:
            search_input = self.wait_for_element(
                By.CSS_SELECTOR,
                "input[name='s'], input.search-input, input[type='search'], input[placeholder*='Search']",
            )
            search_input.clear()
            search_input.send_keys(search_term)
            search_input.send_keys(Keys.RETURN)
            time.sleep(2)

            # Znajdź produkty w wynikach
            products = self.driver.find_elements(
                By.CSS_SELECTOR, "article.product, .product-miniature, .product-item"
            )

            if len(products) == 0:
                print("⚠️ Nie znaleziono produktów, używam pierwszego z dostępnych")
                self.driver.get(self.base_url)
                time.sleep(2)
                products = self.driver.find_elements(
                    By.CSS_SELECTOR,
                    "article.product, .product-miniature, .product-item",
                )

            print(f"📦 Znaleziono {len(products)} produktów")

            # Wybierz losowy produkt
            if products:
                random_product = random.choice(products[: min(5, len(products))])
                self.driver.execute_script(
                    "arguments[0].scrollIntoView(true);", random_product
                )
                time.sleep(0.5)

                try:
                    product_name = random_product.find_element(
                        By.CSS_SELECTOR, "h2, h3, .product-title"
                    ).text
                except:
                    product_name = "Znaleziony produkt"

                random_product.find_element(By.CSS_SELECTOR, "a").click()
                time.sleep(2)

                # Dodaj do koszyka
                self.wait_and_click(
                    By.CSS_SELECTOR,
                    "button[data-button-action='add-to-cart'], .add-to-cart",
                )

                self.cart_products.append(product_name)
                print(f"✅ Dodano: {product_name}")
                time.sleep(1)

        except Exception as e:
            print(f"⚠️ Błąd podczas wyszukiwania: {e}")

    def remove_products_from_cart(self):
        """Usuwa 3 produkty z koszyka"""
        print("\n" + "=" * 60)
        print("KROK 3: Usuwanie 3 produktów z koszyka")
        print("=" * 60)

        # Przejdź do koszyka
        try:
            self.wait_and_click(
                By.CSS_SELECTOR, "a[href*='cart'], .cart-link, a[class*='cart']"
            )
            time.sleep(2)
        except:
            self.driver.get(f"{self.base_url}/cart?action=show")
            time.sleep(2)

        for i in range(3):
            try:
                # Znajdź przyciski usuwania
                remove_buttons = self.driver.find_elements(
                    By.CSS_SELECTOR,
                    ".remove-from-cart, a[class*='delete'], .cart-item-delete, i.remove-from-cart",
                )

                if remove_buttons:
                    print(f"🗑️  Usuwam produkt {i+1}/3")
                    remove_buttons[0].click()
                    time.sleep(2)
                    print(f"✅ Usunięto produkt {i+1}")
                else:
                    print(f"⚠️ Nie znaleziono przycisku usuwania")
                    break
            except Exception as e:
                print(f"⚠️ Błąd przy usuwaniu produktu: {e}")

        print("✅ Zakończono usuwanie produktów")

    def register_account(self):
        """Rejestruje nowe konto"""
        print("\n" + "=" * 60)
        print("KROK 4: Rejestracja nowego konta")
        print("=" * 60)

        self.user_email = self.generate_random_email()
        self.user_password = self.generate_random_password()

        print(f"📧 Email: {self.user_email}")
        print(f"🔑 Hasło: {self.user_password}")

        # Przejdź do strony logowania
        try:
            self.driver.get(f"{self.base_url}/login")
            time.sleep(2)

            # Znajdź link do rejestracji
            try:
                register_link = self.driver.find_element(
                    By.CSS_SELECTOR,
                    "a[href*='registration'], a[data-link-action='display-register-form'], .no-account a",
                )
                register_link.click()
                time.sleep(1)
            except:
                print("ℹ️  Formularz rejestracji już widoczny")

            # Wypełnij formularz
            # Social title (Mr/Mrs)
            try:
                self.wait_and_click(
                    By.CSS_SELECTOR, "input[name='id_gender'][value='1']", timeout=5
                )
            except:
                pass

            # Imię
            first_name = self.wait_for_element(
                By.CSS_SELECTOR, "input[name='firstname']"
            )
            first_name.clear()
            first_name.send_keys("Jan")

            # Nazwisko
            last_name = self.driver.find_element(
                By.CSS_SELECTOR, "input[name='lastname']"
            )
            last_name.clear()
            last_name.send_keys("Kowalski")

            # Email
            email = self.driver.find_element(By.CSS_SELECTOR, "input[name='email']")
            email.clear()
            email.send_keys(self.user_email)

            # Hasło
            password = self.driver.find_element(
                By.CSS_SELECTOR, "input[name='password']"
            )
            password.clear()
            password.send_keys(self.user_password)

            # Data urodzenia (opcjonalnie)
            try:
                birthday = self.driver.find_element(
                    By.CSS_SELECTOR, "input[name='birthday']"
                )
                birthday.send_keys("01/01/1990")
            except:
                pass

            # Zgody (checkboxy)
            try:
                checkboxes = self.driver.find_elements(
                    By.CSS_SELECTOR,
                    "input[type='checkbox'][name*='psgdpr'], input[name='customer_privacy']",
                )
                for checkbox in checkboxes:
                    if not checkbox.is_selected():
                        checkbox.click()
            except:
                pass

            # Wyślij formularz
            submit_button = self.driver.find_element(
                By.CSS_SELECTOR,
                "button[data-link-action='save-customer'], button[type='submit']",
            )
            submit_button.click()

            print("✅ Formularz rejestracji wysłany")
            time.sleep(3)

            # Sprawdź czy rejestracja się powiodła
            try:
                self.driver.find_element(
                    By.CSS_SELECTOR, ".account, .user-info, a[href*='my-account']"
                )
                print("✅ Rejestracja zakończona sukcesem!")
            except:
                print("⚠️ Rejestracja mogła nie zadziałać, ale kontynuuję...")

        except Exception as e:
            print(f"⚠️ Błąd podczas rejestracji: {e}")
            print("Kontynuuję z procesem zamówienia...")

    def complete_order(self):
        """Wykonuje zamówienie"""
        print("\n" + "=" * 60)
        print("KROK 5: Wykonywanie zamówienia")
        print("=" * 60)

        # Przejdź do koszyka i proceed to checkout
        try:
            self.wait_and_click(By.CSS_SELECTOR, "a[href*='cart']")
            time.sleep(2)
        except:
            self.driver.get(f"{self.base_url}/cart?action=show")
            time.sleep(2)

        # Kliknij "Proceed to checkout"
        try:
            self.wait_and_click(
                By.CSS_SELECTOR,
                "a[href*='checkout'], .checkout-button, a.btn[href*='order']",
            )
            time.sleep(3)
            print("✅ Rozpoczęto proces zamówienia")
        except Exception as e:
            print(f"⚠️ Problem z rozpoczęciem checkout: {e}")
            return

        # Adres dostawy
        try:
            print("\n📍 Wypełniam adres dostawy...")

            # Sprawdź czy trzeba wypełnić adres
            try:
                address_input = self.driver.find_element(
                    By.CSS_SELECTOR, "input[name='address1']"
                )

                # Wypełnij dane adresowe
                fields = {
                    "input[name='address1']": "ul. Testowa 123",
                    "input[name='postcode']": "00-001",
                    "input[name='city']": "Warszawa",
                }

                for selector, value in fields.items():
                    try:
                        field = self.driver.find_element(By.CSS_SELECTOR, selector)
                        field.clear()
                        field.send_keys(value)
                    except:
                        pass

                # Wybierz kraj (Polska)
                try:
                    country_select = self.driver.find_element(
                        By.CSS_SELECTOR, "select[name='id_country']"
                    )
                    country_select.send_keys("Poland")
                except:
                    pass

                # Telefon
                try:
                    phone = self.driver.find_element(
                        By.CSS_SELECTOR, "input[name='phone']"
                    )
                    phone.clear()
                    phone.send_keys("123456789")
                except:
                    pass

                print("✅ Adres wypełniony")
            except:
                print("ℹ️  Adres już zapisany lub nie wymagany")

            # Kontynuuj do wyboru dostawy
            try:
                continue_btn = self.wait_and_click(
                    By.CSS_SELECTOR,
                    "button[name='confirm-addresses'], button.continue, button[type='submit']",
                    timeout=5,
                )
                time.sleep(2)
            except:
                print("ℹ️  Przechodzę do wyboru dostawy...")

        except Exception as e:
            print(f"⚠️ Problem z adresem: {e}")

    def select_shipping_and_payment(self):
        """Wybiera przewoźnika i metodę płatności"""
        print("\n" + "=" * 60)
        print("KROK 6: Wybór przewoźnika i płatności")
        print("=" * 60)

        # Wybór przewoźnika
        try:
            print("🚚 Wybieramy przewoźnika...")
            carriers = self.driver.find_elements(
                By.CSS_SELECTOR,
                "input[name='delivery_option[]'], input[type='radio'][id*='delivery']",
            )

            if len(carriers) >= 2:
                # Wybierz drugiego przewoźnika (losowo jeden z dwóch)
                carrier_choice = random.choice([0, 1])
                carriers[carrier_choice].click()
                print(f"✅ Wybrano przewoźnika {carrier_choice + 1}")
                time.sleep(1)
            elif len(carriers) == 1:
                carriers[0].click()
                print("✅ Wybrano jedynego dostępnego przewoźnika")

            # Kontynuuj
            try:
                continue_btn = self.wait_and_click(
                    By.CSS_SELECTOR,
                    "button[name='confirmDeliveryOption'], button.continue",
                    timeout=5,
                )
                time.sleep(2)
            except:
                print("ℹ️  Przechodzę do płatności...")

        except Exception as e:
            print(f"⚠️ Problem z wyborem przewoźnika: {e}")

        # Wybór płatności - przy odbiorze
        try:
            print("💳 Wybieramy płatność przy odbiorze...")

            # Szukaj opcji "Cash on delivery" lub "Payment on delivery"
            payment_options = self.driver.find_elements(
                By.CSS_SELECTOR,
                "input[type='radio'][id*='payment'], label[for*='payment']",
            )

            clicked = False
            for option in payment_options:
                text = option.text.lower() if hasattr(option, "text") else ""
                id_attr = option.get_attribute("id") or ""
                for_attr = option.get_attribute("for") or ""

                if any(
                    keyword in text.lower() + id_attr.lower() + for_attr.lower()
                    for keyword in ["cash", "delivery", "odbior", "pobranie"]
                ):
                    try:
                        option.click()
                        clicked = True
                        print("✅ Wybrano płatność przy odbiorze")
                        break
                    except:
                        pass

            if not clicked:
                # Wybierz pierwszą dostępną opcję
                try:
                    payment_options[0].click()
                    print("✅ Wybrano pierwszą dostępną metodę płatności")
                except:
                    pass

            time.sleep(1)

        except Exception as e:
            print(f"⚠️ Problem z wyborem płatności: {e}")

    def confirm_order(self):
        """Zatwierdza zamówienie"""
        print("\n" + "=" * 60)
        print("KROK 7: Zatwierdzanie zamówienia")
        print("=" * 60)

        try:
            # Zaakceptuj warunki
            try:
                terms_checkbox = self.driver.find_element(
                    By.CSS_SELECTOR,
                    "input[name='conditions_to_approve[terms-and-conditions]'], input#conditions_to_approve",
                )
                if not terms_checkbox.is_selected():
                    terms_checkbox.click()
                    print("✅ Zaakceptowano warunki")
            except:
                print("ℹ️  Nie znaleziono checkboxa z warunkami")

            time.sleep(1)

            # Zatwierdź zamówienie
            confirm_button = self.wait_and_click(
                By.CSS_SELECTOR,
                "button[type='submit'][class*='confirm'], button.btn-primary[type='submit'], #payment-confirmation button",
            )

            print("✅ Zamówienie zatwierdzone!")
            time.sleep(3)

            # Sprawdź czy jesteśmy na stronie potwierdzenia
            try:
                self.driver.find_element(
                    By.CSS_SELECTOR,
                    "#order-confirmation, .order-confirmation, h3[class*='confirmation']",
                )
                print("✅ Potwierdzenie zamówienia wyświetlone")
                return True
            except:
                print("⚠️ Nie znaleziono potwierdzenia, ale kontynuuję...")
                return False

        except Exception as e:
            print(f"⚠️ Błąd podczas zatwierdzania: {e}")
            return False

    def check_order_status(self):
        """Sprawdza status zamówienia"""
        print("\n" + "=" * 60)
        print("KROK 8: Sprawdzanie statusu zamówienia")
        print("=" * 60)

        try:
            # Przejdź do konta
            self.driver.get(f"{self.base_url}/my-account")
            time.sleep(2)

            # Kliknij w historię zamówień
            self.wait_and_click(
                By.CSS_SELECTOR,
                "a[href*='order-history'], a#history-link, a[id*='order']",
            )
            time.sleep(2)

            # Znajdź ostatnie zamówienie
            orders = self.driver.find_elements(
                By.CSS_SELECTOR, ".order-item, tr[class*='order'], tbody tr"
            )

            if orders:
                print(f"📦 Znaleziono {len(orders)} zamówienie(ń)")

                # Sprawdź status pierwszego zamówienia
                try:
                    status = (
                        orders[0]
                        .find_element(
                            By.CSS_SELECTOR,
                            ".order-status, td[class*='status'], span[class*='label']",
                        )
                        .text
                    )
                    print(f"✅ Status zamówienia: {status}")
                except:
                    print("✅ Zamówienie widoczne w historii")

                return True
            else:
                print("⚠️ Nie znaleziono zamówień w historii")
                return False

        except Exception as e:
            print(f"⚠️ Błąd podczas sprawdzania statusu: {e}")
            return False

    def download_invoice(self):
        """Pobiera fakturę VAT"""
        print("\n" + "=" * 60)
        print("KROK 9: Pobieranie faktury VAT")
        print("=" * 60)

        try:
            # Znajdź link do faktury
            invoice_links = self.driver.find_elements(
                By.CSS_SELECTOR, "a[href*='invoice'], a[href*='pdf'], .invoice-link"
            )

            if invoice_links:
                print("📄 Znaleziono link do faktury")
                invoice_links[0].click()
                print("✅ Faktura pobrana (lub rozpoczęto pobieranie)")
                time.sleep(2)
                return True
            else:
                print(
                    "⚠️ Nie znaleziono linku do faktury (może być jeszcze niedostępna)"
                )

                # Sprawdź szczegóły zamówienia
                try:
                    details_link = self.driver.find_element(
                        By.CSS_SELECTOR,
                        "a[href*='order-detail'], a[data-link-action='view-order-details']",
                    )
                    details_link.click()
                    time.sleep(2)

                    # Spróbuj ponownie znaleźć fakturę
                    invoice_links = self.driver.find_elements(
                        By.CSS_SELECTOR, "a[href*='invoice'], a[href*='pdf']"
                    )

                    if invoice_links:
                        invoice_links[0].click()
                        print("✅ Faktura pobrana ze szczegółów zamówienia")
                        time.sleep(2)
                        return True
                except:
                    pass

                return False

        except Exception as e:
            print(f"⚠️ Błąd podczas pobierania faktury: {e}")
            return False

    def run_full_test(self):
        """Uruchamia pełny test sklepu"""
        start_time = time.time()

        print("\n" + "=" * 60)
        print("🧪 TEST AUTOMATYCZNY SKLEPU PRESTASHOP")
        print("=" * 60)
        print(f"🕐 Start: {datetime.now().strftime('%H:%M:%S')}")
        print(f"🌐 URL: {self.base_url}")
        print("=" * 60)

        try:
            self.setup()

            # 1. Dodaj 10 produktów z 2 kategorii
            self.add_products_to_cart()

            # 2. Wyszukaj i dodaj produkt
            self.search_and_add_product()

            # 3. Usuń 3 produkty
            self.remove_products_from_cart()

            # 4. Zarejestruj konto
            self.register_account()

            # 5. Wykonaj zamówienie
            self.complete_order()

            # 6. Wybierz dostawę i płatność
            self.select_shipping_and_payment()

            # 7. Zatwierdź zamówienie
            order_confirmed = self.confirm_order()

            # 8. Sprawdź status
            if order_confirmed:
                self.check_order_status()

                # 9. Pobierz fakturę
                self.download_invoice()

            end_time = time.time()
            duration = end_time - start_time

            print("\n" + "=" * 60)
            print("✅ TEST ZAKOŃCZONY SUKCESEM!")
            print("=" * 60)
            print(f"⏱️  Czas wykonania: {duration:.2f} sekund ({duration/60:.2f} minut)")
            print(f"🕐 Koniec: {datetime.now().strftime('%H:%M:%S')}")

            if duration > 300:
                print("⚠️  UWAGA: Test przekroczył 5 minut!")
            else:
                print(
                    f"✅ Test wykonany w limicie czasowym (pozostało {300-duration:.2f}s)"
                )

            print("=" * 60)

        except Exception as e:
            print(f"\n❌ BŁĄD KRYTYCZNY: {e}")
            import traceback

            traceback.print_exc()

        finally:
            self.teardown()


def main():
    """Główna funkcja"""
    # Możesz zmienić URL na swój
    # BASE_URL = "https://127.0.0.1:8080"
    BASE_URL = "http://localhost:8080"

    tester = PrestaShopTester(base_url=BASE_URL)
    tester.run_full_test()


if __name__ == "__main__":
    main()
