from dataclasses import dataclass, asdict
from datetime import date
from typing import List

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from sp_api.api import Orders
from sp_api.base import SellingApiException, Marketplaces
import time
import const

class GoogleSheets:
    def __init__(self, credentials_file: str, sheet_key: str, worksheet_name: str):
        self.credentials_file = credentials_file
        self.sheet_key = sheet_key
        self.worksheet_name = worksheet_name
        self.scope = [
            "https://spreadsheets.google.com/feeds",
        ]
        self.sheet_object = self._get_sheet_object()

    def _get_sheet_object(self) -> gspread.Worksheet:
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            self.credentials_file, self.scope
        )
        client = gspread.authorize(credentials)
        return client.open_by_key(self.sheet_key).worksheet(self.worksheet_name)

    def write_header_if_doesnt_exist(self, columns: List[str]) -> None:
        data = self.sheet_object.get_all_values()
        if not data:
            self.sheet_object.insert_row(columns)

    def append_rows(self, rows: List[List]) -> None:
        last_row_number = len(self.sheet_object.col_values(1)) + 1
        self.sheet_object.insert_rows(rows, last_row_number)

@dataclass
class AmazonOrder:
    order_id: str
    purchase_date: str
    order_status: str
    order_total: str
    sku: str
    asin: str

HEADER = [
"AmazonOrderId",
"PurchaseDate",
"OrderStatus",
"OrderTotal",
"sku", 
"asin"
]

@dataclass
class CountryConfig:
    marketplace: Marketplaces
    google_worksheet_name: str
    refresh_token: str

configs = [CountryConfig(Marketplaces.UK, const.GOOGLE_WORKSHEET_NAME_UK, const.REFRESH_TOKEN_UK), CountryConfig(Marketplaces.DE, const.GOOGLE_WORKSHEET_NAME_DE, const.REFRESH_TOKEN_DE)]

class AmazonScript:
    def __init__(self):
        for config in configs:
            print("-----" + "Started fetching orders for: " + str(config.marketplace) + "-----")
            self.fetch_orders(config)

    def get_orders_data_and_append_to_gs(self, google_sheets: GoogleSheets, config: CountryConfig) -> None:
        try:
            order_data = self.get_orders_from_sp_api(config=config)
            ready_rows = [list(asdict(row).values()) for row in order_data]
            google_sheets.append_rows(ready_rows)
        except SellingApiException as e:
            print(f"Error: {e}")

    def fetch_orders(self, config: CountryConfig):
        google_sheets = GoogleSheets("keys.json", const.GOOGLE_SHEETS_ID, config.google_worksheet_name)
        google_sheets.write_header_if_doesnt_exist(HEADER)
        self.get_orders_data_and_append_to_gs(google_sheets=google_sheets, config=config)

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
        orders = res.get_orders(CreatedAfter='2023-01-09', CreatedBefore=date.today().isoformat()).payload.get("Orders", '')
        print("Fetched " + str(len(orders)) + " orders.") 
        order_items_to_sheet = []
        for order in orders:
            order_id = order.get("AmazonOrderId")
            print("fetching order details with id: " + order_id)
            order_items_response = res.get_order_items(order_id = order_id) 
            if order_items_response.errors == None:
                order_items = order_items_response.payload.get("OrderItems")
                for order_item in order_items:
                    print("Successfully fetched order with ASIN " + order_item.get("ASIN", ""))
                    order_items_to_sheet.append(self.bind_order_with_order_item(
                        order=order,
                        order_item=order_item
                    ))
                print("Applying delay by 1 sec")
                time.sleep(float(1))
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
        result_dict["OrderTotal"] = order.get("OrderTotal", {})
        result_dict["ASIN"] = order_item.get("ASIN", "")
        result_dict["SellerSKU"] = order_item.get("SellerSKU", "")
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
                    order_total=item.get("OrderTotal", {}).get("Amount", ""),
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
                    order_total=item.get("OrderTotal", {}).get("Amount", ''),
                    sku=item.get("SellerSKU", ''),
                    asin=item.get("ASIN", ''),
                )
            )
        return amazon_order_list

if __name__ == '__main__':
    print("Start script.")
    am = AmazonScript()
    print("Done.")