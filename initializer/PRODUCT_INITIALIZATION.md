# Setup

First, go to **Advanced Parameters** and then **Webservice**, check **Enable PrestaShop's webservice** and save.  

Next, click **Add new webservice key**. In this panel, click **Generate** next to **Key** and assign the following permissions:

* **Categories** (POST, GET)
* **Products** (POST)
* **Stock availables** (PUT, GET)
* **Images** (POST)

Create a `.env` file and add:

```
PRESTASHOP_API_KEY=
```

Then paste your recently generated API key.

**Make sure you are in initializer/ folder!**

First, run script.py

### REMEMBER TO DELETE THE KEY AFTER YOU FINISH ADDING PRODUCTS!
