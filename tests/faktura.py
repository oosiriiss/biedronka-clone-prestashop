import time
import main

EMAIL="test_ciex15mq_1769679106@example.com"
PASSWORD="Haslo123!"
BASE_URL = "https://localhost:19776"

def main_fn():

    tester = main.PrestaShopTester(base_url=BASE_URL)

    print("Test pobierania faktury")

    try:
        tester.setup()

        time.sleep(1)

        tester.login(EMAIL,PASSWORD)

        time.sleep(1)

        tester.download_invoice()

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback

        traceback.print_exc()

    finally:
        tester.teardown()

if __name__ == "__main__":
    main_fn()
