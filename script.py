from dataclasses import dataclass, asdict
from datetime import date, timedelta
from typing import List
from google.oauth2.credentials import Credentials
import gspread
from sp_api.api import Orders
from sp_api.base import SellingApiException
import time
import const
from google.auth.transport.requests import Request
import os.path
from google_sheets import GoogleSheets
from amazon_order import AmazonOrder
from country_config import configs, CountryConfig

SCOPES = [
    'https://www.googleapis.com/auth/drive', 
]

class AmazonScript:
    def __init__(self, credentials, created_after: date, created_before: date):
        self.credentials = credentials
        self.created_after = created_after
        self.created_before = created_before
        self.fetch_orders()

    def get_orders_data_and_append_to_worksheet(self, worksheet: gspread.Worksheet, config: CountryConfig) -> None:
        try:
            order_data = self.get_orders_from_sp_api(config=config)
            ready_rows = [list(asdict(row).values()) for row in order_data]
            last_row_number = len(worksheet.col_values(1)) + 1
            worksheet.insert_rows(ready_rows, last_row_number)
        except SellingApiException as e:
            print(f"Error: {e}")

    def fetch_orders(self):
        client = gspread.authorize(self.credentials)

        files = client.list_spreadsheet_files(title= ("YY_amazon_orders_" + self.created_after.strftime("%Y-%m-%d")), folder_id='1grQM2tnWM1ip7AgEQ7wEEZZushqIMLId')

        google_sheets = GoogleSheets(self.credentials, name=("YY_amazon_orders_" + self.created_after.strftime("%Y-%m-%d")))
        index = 0
        for config in configs:
            try:
                print("-----" + "Started fetching orders for: " + str(config.marketplace) + "-----")
                order_data = self.get_orders_from_sp_api(config=config)
                ready_rows = [list(asdict(row).values()) for row in order_data]
                worksheet = google_sheets.add_worksheet(name=config.google_worksheet_name, index=index)
                last_row_number = len(worksheet.col_values(1)) + 1
                worksheet.insert_rows(ready_rows, last_row_number)
            except SellingApiException as e:
                print(f"Error: {e}")
                return e
            index+=index
        if len(files) > 0:
            for file in files:
                client.del_spreadsheet(file.get("id"))

    # returns list of amazon orders for given country represented as CountryConfig.
    def get_orders_from_sp_api(self, config: CountryConfig) -> List[AmazonOrder]:
        client_config = dict(
            refresh_token=config.refresh_token,
            lwa_app_id=const.LWA_APP_ID,
            lwa_client_secret=const.CLIENT_SECRET,
            aws_secret_key=const.AWS_SECRET_KEY,
            aws_access_key=const.AWS_ACCESS_KEY,
            role_arn=const.ROLE_ARN,
        )

        res = Orders(credentials=client_config, marketplace=config.marketplace)
        print("Fetching orders from " + str(config.marketplace))
        orders = res.get_orders(CreatedAfter=self.created_after, CreatedBefore=self.created_before).payload.get("Orders", '')
        print("Fetched " + str(len(orders)) + " orders.") 
        order_items_to_sheet = []
        for order in orders:
            order_id = order.get("AmazonOrderId")
            print("fetching order details with id: " + order_id)
            order_items_response = res.get_order_items(order_id = order_id)
            if order_items_response.errors == None:
                order_items = order_items_response.payload.get("OrderItems")
                for order_item in order_items:
                    print(order_item.get("IsGift"))
                    if order_item.get("IsGift") == "true":
                        buyer_info_response = res.get_order_items_buyer_info(order_id=order_id)    
                        print(buyer_info_response)
                    print("Successfully fetched order with ASIN " + order_item.get("ASIN", ""))
                    order_items_to_sheet.append(self.bind_order_with_order_item(
                        order=order,
                        order_item=order_item
                    ))
                print("Applying delay by 1 sec")
                time.sleep(float(1.5))
            else:
                print("ERROR occured!!!")
                break
        print("Converting products to Google Sheet")
        return self.convert_item_list_to_amazon_order_list(order_items_to_sheet)

    @staticmethod
    def bind_order_with_order_item(order: dict, order_item: dict) -> dict:
        result_dict = {}
        result_dict["AmazonOrderId"] = order.get("AmazonOrderId")
        result_dict["PurchaseDate"] = order.get("PurchaseDate", "")
        result_dict["OrderStatus"] = order.get("OrderStatus", "")
        result_dict["ASIN"] = order_item.get("ASIN", "")
        result_dict["SellerSKU"] = order_item.get("SellerSKU", "")
        result_dict["QuantityOrdered"] = order_item.get("QuantityOrdered", "")
        result_dict["ItemPrice"] = order_item.get("CurrencyCode", {})
        result_dict["SalesChannel"] = order.get("SalesChannel", "")
        result_dict["FulfillmentChannel"] = order.get("FulfillmentChannel", "")
        result_dict["ItemPrice"] = order_item.get("ItemPrice", {})
        result_dict["ItemTax"] = order_item.get("ItemTax", {})
        result_dict["ShippingPrice"] = order_item.get("ShippingPrice", {})
        result_dict["ShippingTax"] = order_item.get("ShippingTax", {})
        result_dict["PromotionDiscount"] = order_item.get("PromotionDiscount", {})
        result_dict["ShippingDiscount"] = order_item.get("ShippingDiscount", {})
        result_dict["ShippingAddress"] = order.get("ShippingAddress", {})
        result_dict["IsBusinessOrder"] = order.get("IsBusinessOrder")
        result_dict["IsGift"] = order_item.get("IsGift")
        result_dict["GiftWrapPrice"] = order_item.get("GiftWrapPrice", {})
        result_dict["GiftWrapTax"] = order_item.get("GiftWrapTax", {})
        return result_dict
    
    @staticmethod
    def convert_response_to_amazon_order_list(
            response_payload: dict
    ) -> List[AmazonOrder]:
        amazon_order_list = []
        for item in response_payload.get("Orders"):
            amazon_order_list.append(
                AmazonOrder(
                    order_id=item.get("AmazonOrderId", ''),
                    purchase_date=item.get("PurchaseDate", ''),
                    order_status=item.get("OrderStatus", ''),
                    sales_channel=item.get("SalesChannel", {}).get("Amount", ''),
                    fulfillment_channel=item.get("FulfillmentChannel", {}).get("Amount", ''),
                    is_business_order=item.get("IsBusinessOrder", ''),
                    country_code=item.get("ShippingAddress", {}).get("CountryCode", ''),
                )
            )
        print(amazon_order_list)
        return amazon_order_list

    @staticmethod
    def convert_item_list_to_amazon_order_list(
            item_list: list
    ) -> List[AmazonOrder]:
        amazon_order_list = []
        for item in item_list:
            amazon_order_list.append(
                AmazonOrder(
                    order_id=item.get("AmazonOrderId", ''),
                    purchase_date=item.get("PurchaseDate", ''),
                    order_status=item.get("OrderStatus", ''),
                    sku=item.get("SellerSKU", ''),
                    asin=item.get("ASIN", ''),
                    quantity_ordered=item.get("QuantityOrdered", ''),
                    currency_code=item.get("ItemPrice", {}).get("CurrencyCode", ''),
                    sales_channel=item.get("SalesChannel", ''),
                    fulfillment_channel=item.get("FulfillmentChannel", ''),
                    item_price=item.get("ItemPrice", {}).get("Amount", ''),
                    item_tax=item.get("ItemTax", {}).get("Amount", ''),
                    shipping_price=item.get("ShippingPrice", {}).get("Amount", ''),
                    shipping_tax=item.get("ShippingTax", {}).get("Amount", ''),
                    promotion_discount=item.get("PromotionDiscount", {}).get("Amount", ''),
                    shipping_discount=item.get("ShippingDiscount", {}).get("Amount", ''),
                    country_code=item.get("ShippingAddress", {}).get("CountryCode", ''),
                    is_business_order=item.get("IsBusinessOrder", ''),
                    is_gift=item.get("IsGift", ''),
                    gift_wrap_price=item.get("GiftWrapPrice", {}).get("Amount", ''),
                    gift_wrap_tax=item.get("GiftWrapTax", {}).get("Amount", ''),
                )
            )
        return amazon_order_list

def get_credentials():
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
        return creds
    else:
        print("No token file found!")
        exit()
        


if __name__ == '__main__':
    print("Start script.")

    credentials = get_credentials()
    if credentials == None:
        print("Error with authorization occured.")
        exit()
    # get yesterdays's orders 
    AmazonScript(credentials = credentials,created_after=date.today()-timedelta(days=1),created_before=date.today())
    # update last week's orders 
    AmazonScript(credentials = credentials,created_after=date.today()-timedelta(days=7),created_before=date.today()-timedelta(days=6))
    print("Done.")