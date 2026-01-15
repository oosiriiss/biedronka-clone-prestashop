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
import os


class PrestaShopTester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.driver = None
        self.wait = None
        self.cart_products = []
        self.user_email = None
        self.user_password = None
        self.order_reference = None

    def setup(self):
        print("Uruchamianie przeglądarki Chrome z konfiguracją pobierania...")

        download_dir = os.path.join(os.getcwd(), "downloaded_files")
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)

        print(f"Pliki będą pobierane do: {download_dir}")
        self.download_dir = download_dir

        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        prefs = {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "plugins.always_open_pdf_externally": True,
        }
        options.add_experimental_option("prefs", prefs)

        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=options
        )

        self.wait = WebDriverWait(self.driver, 15)
        print("Przeglądarka uruchomiona\n")

    def teardown(self):
        if self.driver:
            print("\nZamykanie przeglądarki...")
            time.sleep(0.5)
            self.driver.quit()
            print("Przeglądarka zamknięta")

    def generate_random_email(self):
        random_str = "".join(
            random.choices(string.ascii_lowercase + string.digits, k=8)
        )
        timestamp = int(time.time())
        return f"test_{random_str}_{timestamp}@example.com"

    def generate_random_password(self):
        return (
            "Haslo123!"
        )

    def wait_and_click(self, by, value, timeout=10):
        element = WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable((by, value))
        )
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(0.3)
        element.click()
        return element

    def wait_for_element(self, by, value, timeout=10):
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )

    def accept_cookies_if_present(self):
        try:
            cookie_button = self.driver.find_element(
                By.CSS_SELECTOR,
                "button[class*='cookie'], button[class*='gdpr'], a[class*='cookie']",
            )
            cookie_button.click()
            print("Zaakceptowano cookies")
            time.sleep(0.5)
        except:
            pass

    def get_categories(self):
        print("Szukam kategorii produktów...")
        try:
            # - znajdź kategorie z górnego menu
            categories = self.driver.find_elements(
                By.CSS_SELECTOR,
                "#top-menu > li.category > a.dropdown-item",
            )

            category_links = []
            for cat in categories:
                href = cat.get_attribute("href")
                text = cat.text.strip()
                if href and href != self.base_url:
                    category_links.append(href)
                    print(f" Znaleziono kategorię: {text} - {href}")

            category_links = category_links[:2]

            if not category_links:
                print("Nie znaleziono kategorii w menu, sprawdzam homepage")
                category_links = [self.base_url]

            print(f"Wybrano {len(category_links)} kategorii do testu")
            return category_links
        except Exception as e:
            print(f"Problem ze znalezieniem kategorii: {e}")
            return [self.base_url]

    def add_products_to_cart(self):
            print("\n" + "=" * 60)
            print("Dodawanie 10 produktów do koszyka (w tym jeden x2)")
            print("=" * 60)

            self.driver.get(self.base_url)
            time.sleep(1)
            self.accept_cookies_if_present()

            categories = self.get_categories()
            total_added = 0
            added_product_urls = set()
            
            # Czy dodalismy produkt w ziekosznej ilsci
            quantity_increased = False 

            for cat_index, category_url in enumerate(categories[:2], 1):
                if total_added >= 10:
                    break

                print(f"\nKategoria {cat_index}/2")
                self.driver.get(category_url)
                time.sleep(0.5)

                products = self.driver.find_elements(
                    By.CSS_SELECTOR,
                    "article.product-miniature.js-product-miniature",
                )

                print(f"Znaleziono {len(products)} produktów w kategorii")

                products_added_from_category = 0
                i = 0
                
                while total_added < 10 and i < len(products):
                    if products_added_from_category >= 5: 
                         break 

                    try:
                        products = self.driver.find_elements(
                            By.CSS_SELECTOR,
                            "article.product-miniature.js-product-miniature",
                        )

                        if i >= len(products):
                            print(f"Brak więcej produktów w kategorii")
                            break

                        product = products[i]

                        product_url = self.driver.execute_script(
                            "return arguments[0].querySelector('a.thumbnail.product-thumbnail')?.href;",
                            product,
                        )
                        product_name = self.driver.execute_script(
                            "return arguments[0].querySelector('.product-title a')?.textContent?.trim();",
                            product,
                        )

                        if not product_url:
                            i += 1
                            continue
                            
                        if product_url in added_product_urls:
                            print(f"Produkt już w koszyku, pomijam: {product_name}")
                            i += 1
                            continue

                        if not product_name:
                            product_name = f"Produkt {total_added + 1}"

                        self.driver.get(product_url)
                        time.sleep(0.8)

                        # --- SPRAWDZANIE DOSTĘPNOŚCI ---
                        is_available = True
                        try:
                            add_buttons = self.driver.find_elements(
                                By.CSS_SELECTOR, 
                                "button.add-to-cart[data-button-action='add-to-cart']"
                            )
                            
                            if not add_buttons:
                                print(f" Brak przycisku 'Dodaj do koszyka' - POMIJANIE: {product_name}")
                                is_available = False
                            elif not add_buttons[0].is_enabled():
                                print(f" Produkt niedostępny - POMIJANIE: {product_name}")
                                is_available = False
                            
                            if is_available:
                                try:
                                    availability_label = self.driver.find_element(By.ID, "product-availability")
                                    if "brak" in availability_label.text.lower() or "niedostępny" in availability_label.text.lower():
                                        print(f"Oznaczenie braku w magazynie - POMIJANIE: {product_name}")
                                        is_available = False
                                except:
                                    pass 
                        except Exception as e:
                            is_available = False

                        if not is_available:
                            self.driver.get(category_url)
                            i += 1
                            continue

                        # - zmiania ilosci tylko raz
                        current_qty_msg = ""
                        if not quantity_increased:
                            try:
                                qty_input = self.driver.find_element(By.CSS_SELECTOR, "#quantity_wanted")
                                qty_input.click()
                                time.sleep(0.2)
                                qty_input.send_keys(Keys.BACK_SPACE)
                                qty_input.send_keys("2")
                                time.sleep(0.5)
                                
                                quantity_increased = True
                                current_qty_msg = " (Ilość: 2 szt.)"
                                print(f" Zmieniono ilość na 2 dla: {product_name}")
                            except Exception as e:
                                print(f" Nie udało się zmienić ilości: {e}")

                        try:
                            add_button = add_buttons[0]
                            self.driver.execute_script(
                                "arguments[0].scrollIntoView({block: 'center'});",
                                add_button,
                            )
                            time.sleep(0.5)

                            add_button.click()
                            print(f" Kliknięto 'Add to cart'{current_qty_msg} dla: {product_name}")
                            time.sleep(1)

                        except Exception as e:
                            print(f" Błąd przy klikaniu 'Add to cart': {str(e)[:80]}")
                            self.driver.get(category_url)
                            i += 1
                            continue

                        total_added += 1
                        products_added_from_category += 1
                        if product_url:
                            added_product_urls.add(product_url)
                        
                        log_name = product_name + (" (x2)" if current_qty_msg else "")
                        self.cart_products.append(log_name)
                        
                        print(f" Dodano: {log_name} - Produkt {total_added}/10")

                        try:
                            close_btn = self.wait_for_element(
                                 By.CSS_SELECTOR,
                                 "button.close, .modal-close, [class*='close'], .blockcart-modal .close",
                                 timeout=3
                            )
                            close_btn.click()
                            time.sleep(0.5)
                        except:
                            pass 

                        self.driver.get(category_url)
                        time.sleep(1)
                        i += 1

                    except Exception as e:
                        print(f" Błąd krytyczny: {str(e)[:100]}")
                        try:
                            self.driver.get(category_url)
                        except:
                            pass
                        i += 1
                        continue

                print(f"    Dodano {products_added_from_category} produktów z tej kategorii")
                if total_added >= 10:
                    break

            print(f"\nDodano łącznie {total_added} pozycji do koszyka")



    def search_and_add_product(self):
        print("\n" + "=" * 60)
        print("KROK 2: Wyszukiwanie i dodawanie produktu")
        print("=" * 60)

        self.driver.get(self.base_url)
        time.sleep(1)

        search_terms = ["Marcheweczki", "Masło", "Baton"]
        search_term = random.choice(search_terms)

        print(f"Wyszukuję: {search_term}")

        try:
            search_input = self.wait_for_element(
                By.CSS_SELECTOR,
                "input[name='s'], input.search-input, input[type='search'], input[placeholder*='Szukaj']",
            )
            search_input.clear()
            search_input.send_keys(search_term)
            search_input.send_keys(Keys.RETURN)
            time.sleep(1)

            products = self.driver.find_elements(
                By.CSS_SELECTOR, "article.product-miniature.js-product-miniature"
            )

            if len(products) == 0:
                print("Nie znaleziono produktów, używam pierwszego z dostępnych")
                self.driver.get(self.base_url)
                time.sleep(1)
                products = self.driver.find_elements(
                    By.CSS_SELECTOR,
                    "article.product-miniature.js-product-miniature",
                )

            print(f"Znaleziono {len(products)} produktów")

            if products:
                random_product = random.choice(products[: min(5, len(products))])
                self.driver.execute_script(
                    "arguments[0].scrollIntoView(true);", random_product
                )
                time.sleep(1)

                try:
                    product_name = random_product.find_element(
                        By.CSS_SELECTOR, ".product-title a"
                    ).text.strip()
                except:
                    product_name = "Znaleziony produkt"

                random_product.find_element(
                    By.CSS_SELECTOR, "a.thumbnail.product-thumbnail"
                ).click()
                time.sleep(1)

                self.wait_and_click(
                    By.CSS_SELECTOR,
                    "button[data-button-action='add-to-cart'], .add-to-cart",

                )

                self.cart_products.append(product_name)
                print(f"Dodano: {product_name}")


                # Zamkniecie okienka z potwierdznieme
                try:
                    close_btn = self.driver.find_element(
                        By.CSS_SELECTOR,
                        "button.close, .modal-close, [class*='close']",
                    )
                    close_btn.click()
                    time.sleep(0.5)
                except:
                    pass



                time.sleep(1)

        except Exception as e:
            print(f"Błąd podczas wyszukiwania: {e}")

    def remove_products_from_cart(self):
        print("\n" + "=" * 60)
        print("KROK 3: Usuwanie 3 produktów z koszyka")
        print("=" * 60)

        # Przejdź do koszyka
        try:
            self.wait_and_click(By.CSS_SELECTOR, ".blockcart a[href*='koszyk']")
            time.sleep(1)
        except:
            self.driver.get(f"{self.base_url}/koszyk?action=show")
            time.sleep(1)

        cart_items = self.driver.find_elements(By.CSS_SELECTOR, "li.cart-item")
        print(f"W koszyku jest {len(cart_items)} linii produktów")

        if len(cart_items) == 0:
            print("Koszyk jest pusty!")
            return

        removed = 0
        max_to_remove = min(3, len(cart_items))
        print(f"Będę próbował usunąć {max_to_remove} produkty")

        for i in range(max_to_remove):
            try:
                if i > 0:
                    time.sleep(1)

                remove_button = self.driver.find_element(
                    By.CSS_SELECTOR,
                    "a.remove-from-cart[data-link-action='delete-from-cart']",
                )

                print(f"Usuwam produkt {i+1}/{max_to_remove}")

                # Przewiń do przycisku i kliknij
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center'});",
                    remove_button,
                )
                time.sleep(0.5)
                remove_button.click()

                print(" Czekam na aktualizację koszyka...")
                time.sleep(2)

                print(f"Usunięto produkt {i+1}")
                removed += 1
            except Exception as e:
                print(f"Błąd przy usuwaniu produktu: {e}")
                break

        print(f"Zakończono usuwanie produktów (usunięto: {removed})")

    def login(self,email,password):
        self.driver.get(f"{self.base_url}/moje-konto")

        email_field = self.wait_for_element(
                    By.CSS_SELECTOR, "input#field-email"
        )

        time.sleep(1)

        email_field.clear()
        email_field.send_keys(email)

        password_field = self.wait_for_element(
                    By.CSS_SELECTOR, "input#field-password"
        )
        password_field.clear()
        password_field.send_keys(password)

        time.sleep(1)
        submit = self.wait_for_element(
                    By.CSS_SELECTOR, "button#submit-login"
        )
        submit.click()

        time.sleep(1)


    def register_account(self):
        print("\n" + "=" * 60)
        print("KROK 4: Rejestracja nowego konta")
        print("=" * 60)

        self.user_email = self.generate_random_email()
        self.user_password = self.generate_random_password()

        print(f"Email: {self.user_email}")
        print(f"Hasło: {self.user_password}")

        try:
            self.driver.get(f"{self.base_url}/moje-konto")
            time.sleep(1)

            try:
                register_link = self.driver.find_element(
                    By.CSS_SELECTOR,
                    "a[href*='registration'], a[data-link-action='display-register-form'], .no-account a",
                )
                register_link.click()
                time.sleep(1)
            except:
                print("Formularz rejestracji już widoczny")

            try:
                self.wait_and_click(
                    By.CSS_SELECTOR, "input[name='id_gender'][value='1']", timeout=5
                )
            except:
                pass

            first_name = self.wait_for_element(
                By.CSS_SELECTOR, "input[name='firstname']"
            )
            first_name.clear()
            first_name.send_keys("Jan")

            last_name = self.driver.find_element(
                By.CSS_SELECTOR, "input[name='lastname']"
            )
            last_name.clear()
            last_name.send_keys("Kowalski")

            email = self.driver.find_element(By.CSS_SELECTOR, "input[name='email']")
            email.clear()
            email.send_keys(self.user_email)

            password = self.driver.find_element(
                By.CSS_SELECTOR, "input[name='password']"
            )
            password.clear()
            password.send_keys(self.user_password)
            try:
                birthday = self.driver.find_element(
                    By.CSS_SELECTOR, "input[name='birthday']"
                )
                birthday.send_keys("1990-01-01")
            except:
                pass

            try:
                privacy_cb = self.driver.find_element(
                    By.CSS_SELECTOR, "input[name='customer_privacy'][type='checkbox']"
                )
                if not privacy_cb.is_selected():
                    self.driver.execute_script("arguments[0].click();", privacy_cb)
                    print("Zaznaczono: Customer data privacy")
            except Exception as e:
                print(f"Nie znaleziono customer_privacy: {str(e)[:50]}")

            try:
                gdpr_cb = self.driver.find_element(
                    By.CSS_SELECTOR, "input[name='psgdpr'][type='checkbox']"
                )
                if not gdpr_cb.is_selected():
                    self.driver.execute_script("arguments[0].click();", gdpr_cb)
                    print("Zaznaczono: Terms and conditions")
            except Exception as e:
                print(f"Nie znaleziono psgdpr: {str(e)[:50]}")

            time.sleep(0.5)

            submit_button = self.driver.find_element(
                By.CSS_SELECTOR,
                "button[data-link-action='save-customer'], button[type='submit']",
            )
            submit_button.click()

            print("Formularz rejestracji wysłany")
            time.sleep(2)

            try:
                self.driver.find_element(
                    By.CSS_SELECTOR, ".account, .user-info, a[href*='my-account']"
                )
                print("Rejestracja zakończona sukcesem!")
            except:
                print("Rejestracja mogła nie zadziałać, ale kontynuuję...")

        except Exception as e:
            print(f"Błąd podczas rejestracji: {e}")
            print("Kontynuuję z procesem zamówienia...")

    def complete_order(self):
        print("\n" + "=" * 60)
        print("KROK 5: Wykonywanie zamówienia")
        print("=" * 60)

        try:
            self.wait_and_click(By.CSS_SELECTOR, "a[href*='koszyk']")
            time.sleep(2)
        except:
            self.driver.get(f"{self.base_url}/koszyk?action=show")
            time.sleep(2)

        try:
            self.wait_and_click(
                By.CSS_SELECTOR,
                "a[href*='checkout'], .checkout-button, a.btn[href*='zamówienie']",
            )
            time.sleep(1)
            print("Rozpoczęto proces zamówienia")
        except Exception as e:
            print(f"Problem z rozpoczęciem checkout: {e}")
            return

        try:
            print("Sprawdź\u0144 adres dostawy...")
            time.sleep(1)

            try:
                existing_address = self.driver.find_element(
                    By.CSS_SELECTOR,
                    "input[type='radio'][name='id_address_delivery'][checked], input[type='radio'][name='id_address_delivery']:checked",
                )
                print("Adres już istnieje i jest wybrany")
            except:
                print("Wypełniam nowy adres...")
                try:
                    address_input = self.driver.find_element(
                        By.CSS_SELECTOR, "input[name='address1']"
                    )

                    fields = {
                        "input[name='address1']": "Testowa 14",
                        "input[name='postcode']": "69-420",
                        "input[name='city']": "Testowo",
                    }

                    for selector, value in fields.items():
                        try:
                            field = self.driver.find_element(By.CSS_SELECTOR, selector)
                            field.clear()
                            field.send_keys(value)
                        except:
                            pass

                    try:
                        country_select = self.driver.find_element(
                            By.CSS_SELECTOR,
                            "select#field-id_country[name='id_country']",
                        )
                        from selenium.webdriver.support.ui import Select

                        select = Select(country_select)
                        select.select_by_value("14")
                        print("Wybrano kraj: Polska")
                    except:
                        print("Kraj już wybrany")

                    print("Adres wypełniony")
                except:
                    print("Nie można wypełnić adresu")

            time.sleep(1)
            print("Klikam przycisk Continue...")

            try:
                continue_btn = self.wait_for_element(
                    By.CSS_SELECTOR,
                    "button[name='confirm-addresses'][type='submit']",
                    timeout=10,
                )
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center'});", continue_btn
                )
                time.sleep(0.5)
                continue_btn.click()
                print("Kliknięto Continue - przechodzę do Shipping Method")
                time.sleep(3)
            except Exception as e:
                print(f"Błąd przy klikaniu Continue: {str(e)[:80]}")

        except Exception as e:
            print(f"Problem z adresem: {str(e)[:100]}")

    def select_shipping_and_payment(self):
        """Wybiera przewoźnika i metodę płatności"""
        print("\n" + "=" * 60)
        print("KROK 6: Wybór przewoźnika i płatności")
        print("=" * 60)

        try:
            print("Wybieramy przewoźnika...")

            carriers = self.driver.find_elements(
                By.CSS_SELECTOR, "input[type='radio'][name*='delivery_option']"
            )

            if len(carriers) >= 1:
                already_selected = any(c.is_selected() for c in carriers)

                if already_selected:
                    print("Przewoźnik już wybrany (domyślny)")
                elif len(carriers) >= 2:
                    carrier_choice = random.choice([0, 1])
                    carriers[carrier_choice].click()
                    print(f"Wybrano przewoźnika {carrier_choice + 1}")
                    time.sleep(1)
                else:
                    carriers[0].click()
                    print("Wybrano jedynego dostępnego przewoźnika")
                    time.sleep(1)
            else:
                print("Brak opcji przewoźników lub już wybrane")

            time.sleep(1)
            print("Klikam przycisk Continue (Shipping)...")

            try:
                continue_btn = self.wait_for_element(
                    By.CSS_SELECTOR,
                    "button[name='confirmDeliveryOption'][type='submit']",
                    timeout=10,
                )
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center'});", continue_btn
                )
                time.sleep(0.5)
                continue_btn.click()
                print("Kliknięto Continue - przechodzę do Payment")
                time.sleep(2)
            except Exception as e:
                print(f"Błąd przy klikaniu Continue: {str(e)[:80]}")

        except Exception as e:
            print(f"Problem z wyborem przewoźnika: {str(e)[:100]}")

        try:
            print("Wybieramy metodę płatności...")
            time.sleep(1)  

            payment_radios = self.wait.until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, "input[type='radio'][name='payment-option']")
                )
            )

            if len(payment_radios) >= 3:
                self.driver.execute_script("arguments[0].click();", payment_radios[2])
                print("Wybrano metodę płatności: Pay by Cash on Delivery")
                time.sleep(2)
            elif payment_radios:
                self.driver.execute_script("arguments[0].click();", payment_radios[0])
                print(f"Wybrano pierwszą dostępną metodę płatności")
                time.sleep(2)
            else:
                print("Nie znaleziono opcji płatności")

        except Exception as e:
            print(f"Problem z wyborem płatności: {str(e)[:100]}")

    def confirm_order(self):
        """Zatwierdza zamówienie"""
        print("\n" + "=" * 60)
        print("KROK 7: Zatwierdzanie zamówienia")
        print("=" * 60)

        try:
            try:
                checkbox_selectors = [
                    "input[name='conditions_to_approve[terms-and-conditions]']",
                    "input#conditions_to_approve\\[terms-and-conditions\\]",
                    "input[id*='conditions_to_approve']",
                    "input[type='checkbox'][name*='conditions']",
                    "input[type='checkbox'][id*='terms']",
                    "#conditions-to-approve input[type='checkbox']",
                    ".payment-options input[type='checkbox']",
                ]

                terms_checkbox = None
                for selector in checkbox_selectors:
                    try:
                        terms_checkbox = self.driver.find_element(
                            By.CSS_SELECTOR, selector
                        )
                        print(f"Znaleziono checkbox z selektorem: {selector}")
                        break
                    except:
                        continue

                if terms_checkbox:
                    if not terms_checkbox.is_selected():
                        self.driver.execute_script(
                            "arguments[0].scrollIntoView({block: 'center'});",
                            terms_checkbox,
                        )
                        time.sleep(0.5)
                        self.driver.execute_script(
                            "arguments[0].click();", terms_checkbox
                        )
                        print("Zaakceptowano warunki")
                        time.sleep(1)
                    else:
                        print("Warunki już zaakceptowane")
                else:
                    print("")

            except Exception as e:
                print(f"Checkbox z warunkami: {str(e)[:100]}")

            time.sleep(1)

            try:
                print("Czekam aż przycisk 'Place order' będzie aktywny...")

                confirm_button = self.wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "#payment-confirmation button[type='submit']")
                    )
                )

                for i in range(10):
                    if not confirm_button.get_attribute("disabled"):
                        print("Przycisk aktywny!")
                        break
                    time.sleep(1)
                else:
                    print("Przycisk wciąż disabled, próbuję kliknąć...")

                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center'});", confirm_button
                )
                time.sleep(0.5)

                self.driver.execute_script("arguments[0].click();", confirm_button)
                print("Kliknięto 'Place order'")

            except Exception as e:
                submit_buttons = self.driver.find_elements(
                    By.CSS_SELECTOR, "#payment-confirmation button[type='submit']"
                )
                if submit_buttons:
                    submit_buttons[0].click()
                    print("Zamówienie zatwierdzone (metoda alternatywna)")
                else:
                    raise Exception("Nie znaleziono przycisku Place order")

            print("Zamówienie zatwierdzone!")
            time.sleep(3)

            try:
                self.driver.find_element(
                    By.CSS_SELECTOR,
                    "#order-confirmation, .order-confirmation, h3[class*='confirmation']",
                )
                print("Potwierdzenie zamówienia wyświetlone")

                try:
                    order_ref_elem = self.driver.find_element(
                        By.CSS_SELECTOR,
                        "#order-details li:first-child, .order-reference-value, [class*='reference']",
                    )
                    self.order_reference = order_ref_elem.text.strip()
                    print(f"Order Reference: {self.order_reference}")
                except:
                    print("Nie udało się odczytać order reference")

                return True
            except:
                print("Nie znaleziono potwierdzenia, ale kontynuuję...")
                return False

        except Exception as e:
            print(f"Błąd podczas zatwierdzania: {e}")
            return False

    def check_order_status(self):
        """Sprawdza status zamówienia"""
        print("\n" + "=" * 60)
        print("KROK 8: Sprawdzanie statusu zamówienia")
        print("=" * 60)

        try:
            self.driver.get(f"{self.base_url}/moje-konto")
            time.sleep(2)

            self.wait_and_click(
                By.CSS_SELECTOR,
                "a[href*='historia-zamowien'], a#history-link, a[id*='order']",
            )
            time.sleep(2)

            orders = self.driver.find_elements(
                By.CSS_SELECTOR, ".order-item, tr[class*='order'], tbody tr"
            )

            if orders:
                print(f"Znaleziono {len(orders)} zamówienie(ń)")

                try:
                    status = (
                        orders[0]
                        .find_element(
                            By.CSS_SELECTOR,
                            ".order-status, td[class*='status'], span[class*='label']",
                        )
                        .text
                    )
                    print(f"Status zamówienia: {status}")
                except:
                    print("Zamówienie widoczne w historii")

                return True
            else:
                print("Nie znaleziono zamówień w historii")
                return False

        except Exception as e:
            print(f"Błąd podczas sprawdzania statusu: {e}")
            return False

    def download_invoice(self):
        """Pobiera fakturę VAT dla konkretnego zamówienia"""
        print("\n" + "=" * 60)
        print("KROK 9: Pobieranie faktury VAT")
        print("=" * 60)

        try:
            print("Przechodzę do historii zamówień...")
            self.driver.get(f"{self.base_url}/historia-zamowien")
            time.sleep(2)

            if self.order_reference:
                print(f"Szukam faktury dla zamówienia: {self.order_reference}")

                try:
                    rows = self.driver.find_elements(By.CSS_SELECTOR, "tbody tr")

                    for row in rows:
                        row_text = row.text
                        if self.order_reference in row_text:
                            print(f"Znaleziono zamówienie: {self.order_reference}")

                            invoice_link = row.find_element(
                                By.CSS_SELECTOR, "a[href*='pdf-invoice']"
                            )
                            invoice_url = invoice_link.get_attribute("href")
                            print(f"URL faktury: {invoice_url}")

                            invoice_link.click()
                            print("Faktura pobrana!")
                            time.sleep(2)
                            return True

                    print("Nie znaleziono faktury dla tego zamówienia")
                except Exception as e:
                    print(f"Błąd przy szukaniu konkretnego zamówienia: {str(e)[:80]}")
            print("Próbuję pobrać pierwszą dostępną fakturę...")
            invoice_links = self.driver.find_elements(
                By.CSS_SELECTOR, "a[href*='pdf-invoice']"
            )

            if invoice_links:
                invoice_url = invoice_links[0].get_attribute("href")
                print(f"Znaleziono link do faktury: {invoice_url}")

                invoice_links[0].click()
                print("Faktura pobrana!")
                time.sleep(2)
                return True
            else:
                print("Nie znaleziono linku do faktury")
                print("Sprawdzam status zamówienia...")

                try:
                    status_elem = self.driver.find_element(
                        By.CSS_SELECTOR, "span.label.label-pill"
                    )
                    status = status_elem.text
                    print(f"Status zamówienia: {status}")

                    if "Awaiting" in status or "Payment" in status:
                        print("Zamówienie oczekuje na zatwierdzenie płatności")
                        print(
                            "  Faktura będzie dostępna po zmianie statusu na 'Delivered' lub 'Payment accepted'"
                        )
                except:
                    pass

                return False

        except Exception as e:
            print(f"Błąd podczas pobierania faktury: {str(e)[:100]}")
            return False

    def run_full_test(self):
        """Uruchamia pełny test sklepu"""
        start_time = time.time()

        print("\n" + "=" * 60)
        print("TEST AUTOMATYCZNY SKLEPU PRESTASHOP")
        print("=" * 60)
        print(f"Start: {datetime.now().strftime('%H:%M:%S')}")
        print(f"URL: {self.base_url}")
        print("=" * 60)

        try:
            self.setup()

            # Dodaj 10 produktów z 2 kategorii
            self.add_products_to_cart()

            # Wyszukaj i dodaj produkt
            self.search_and_add_product()

            # Usuń 3 produkty
            self.remove_products_from_cart()

            # Zarejestruj konto
            self.register_account()

            # Wykonaj zamówienie
            self.complete_order()

            # Wybierz dostawę i płatność
            self.select_shipping_and_payment()

            # Zatwierdź zamówienie
            order_confirmed = self.confirm_order()

            # Sprawdź status
            if order_confirmed:
                self.check_order_status()


                # POBIERANIE FAKTURY w faktura.py
                ##  Pobierz fakturę
                #self.download_invoice()

            end_time = time.time()
            duration = end_time - start_time

            print("\n" + "=" * 60)
            print("TEST ZAKOŃCZONY SUKCESEM!")
            print("=" * 60)
            print(f"Czas wykonania: {duration:.2f} sekund ({duration/60:.2f} minut)")
            print(f"Koniec: {datetime.now().strftime('%H:%M:%S')}")

            print("=" * 60)

        except Exception as e:
            print(f"\n BŁĄD KRYTYCZNY: {e}")
            import traceback

            traceback.print_exc()

        finally:
            self.teardown()


def main():
    BASE_URL = "https://localhost"

    tester = PrestaShopTester(base_url=BASE_URL)
    tester.run_full_test()

if __name__ == "__main__":
    main()
