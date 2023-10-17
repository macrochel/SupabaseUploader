import requests, base64, random, string, json, os
from datetime import datetime, timedelta
from requests.auth import HTTPBasicAuth
from supabase import create_client, Client
from supabase.lib.client_options import ClientOptions

#Supabase
url = "supabaseURL"
key = "supabaseToken"
client_options = ClientOptions(postgrest_client_timeout=None)
supabase: Client = create_client(url, key, options=client_options)

#1C
username = ""  
password = ""  
credentials = f"{username}:{password}"
encoded_credentials = credentials.encode("utf-8")
base64_credentials = base64.b64encode(encoded_credentials).decode("utf-8")
headers = {"Authorization": f"Basic {base64_credentials}"}

def generate_random_string(length):
    characters = string.ascii_letters + string.digits
    random_string = "".join(random.choice(characters) for _ in range(length))
    return random_string

def start(response):
    #Get warehouses
    data = supabase.table("warehouse").select("*").execute()

    #Warehouse check
    exist_warehouces = []
    new_warehouces = []
    data = data.model_dump_json()
    data = json.loads(data)["data"]
    for i in range(0 ,len(data), 1):
        exist_warehouces.append(data[i]["name"])
    
    for i in range(0, len(response), 1):
        if response[i]["warehouse"] not in exist_warehouces:
            new_warehouces.append(response[i]["warehouse"]) 

    if new_warehouces:
        for i in range(0, len(new_warehouces), 1):
            supabase.table("warehouse").insert({"name":f"{new_warehouces[i]}"}).execute()
        data = supabase.table("warehouse").select("*").execute()
        data = data.model_dump_json()
        data = json.loads(data)["data"]

    #Correct all fields + match warehouses
    warehouces = {}
    for d in data:
        warehouces[d["name"]] = {
            "name": d["name"],
            "warehouse_id": d["id"]
        }
    return_products = []
    for i in range(0, len(response), 1):
        response_item = response[i]
        if not response_item.get("sales_item_category1"):
            response_item["sales_item_category1"] = "Не указано"
        if not response_item.get("sales_item_category2"):
            response_item["sales_item_category2"] = "Не указано"
        if not response_item.get("sales_item_category3"):
            response_item["sales_item_category3"] = "Не указано"
        if not response_item.get("sales_item_category4"):
            response_item["sales_item_category4"] = "Не указано"
        if not response_item.get("sales_item_category5"):
            response_item["sales_item_category5"] = "Не указано"
        if response_item.get("sales_item_category6"):
            response_item["sales_item_category6"] = response_item["sales_item_category5"]
        if not response_item.get("payment_method"):
            response_item["payment_method"] = "Не указано"
        if not response_item.get("additional_description"):
            response_item["additional_description"] = "Не указано"
        if not response_item.get("quantity_confirmed"):
            response_item["quantity_confirmed"] = "1,00"

        if response_item.get("sales_order_time"):
            response_item["sales_order_time"] = response_item["sales_order_time"].split(':')[0]
        else:
            product.json.sales_order_time = "Не указано"

        if not response_item.get("sales_order"):
            response_item["sales_order"] = "_" + generate_random_string(9)
        if not response_item.get("sales_item"):
            response_item["sales_item"] = "Без имени"
        if not response_item.get("delivery_method"):
            response_item["delivery_method"] = "Самовывоз"
        if not response_item.get("total"):
            continue
        if response_item.get("warehouse"):
            response_item["warehouse_id"] = warehouces[response_item["warehouse"]]["warehouse_id"]
            return_products.append(response_item)
    del warehouces, data

    #Key mapping
    renamed_products = []
    key_mapping = {
        "sales_order": "order_id",
        "sales_item": "product_name",
        "warehouse_id": "warehouce",
        "sales_item_category2": "category1",
        "sales_item_category3": "category2",
        "sales_item_category4": "category3",
        "sales_item_category5": "category4",
        "sales_order_date": "date",
        "sales_order_time": "order_hour",
        "quantity_confirmed": "quantity"
    }
    for i in range(0, len(return_products), 1):
        product = return_products[i]
        product["total"] = int(product["total"].split(',')[0].translate(str.maketrans('', '', '.')))
        product["quantity_confirmed"] = int(product["quantity_confirmed"].split(',')[0].translate(str.maketrans('', '', '.')))
        del product["additional_description"]
        del product["payment_method"]
        del product["warehouse"]
        del product["sales_date"]
        del product["sales_item_category1"]
        renamed_dict = {key_mapping.get(old_key, old_key): value for old_key, value in product.items()}
        renamed_products.append(renamed_dict)
    del return_products, key_mapping

    #Inserting into DB
    products = []
    for i in range(0, len(renamed_products), 1):
        item = renamed_products[i]
        products.append({"product_name": item["product_name"], "order_id": item["order_id"], "delivery_method": item["delivery_method"], "warehouce": item["warehouce"], "category1": item["category1"], "category2": item["category2"], "category3": item["category3"], "category4": item["category4"], "total": item["total"], "quantity": item["quantity"], "date": item["date"], "order_hour": item["order_hour"]})
    supabase.table("1S_orders_all").insert(products).execute()
    del products, renamed_products

#Date loop
start_date = datetime(2023, 4, 1)
end_date = datetime(2023, 8, 28)
current_date = start_date
while current_date <= end_date:
    os.system("clear")
    date = current_date.strftime('%d-%m-%Y')
    print(date)
    current_date += timedelta(days=1)
    # Get sales
    URL = f"your 1C API URL/{date}" 
    response = requests.get(URL, headers=headers, timeout=None)
    response = response.json()
    if response:
        start(response)