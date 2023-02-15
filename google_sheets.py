import gspread
from typing import List

HEADER = [
"AmazonOrderId",
"PurchaseDate",
"OrderStatus",
"sku", 
"asin",
"QuantityOrdered",
"CurrencyCode",
"SalesChannel",
"FulfillmentChannel",
"ItemPrice",
"ItemTax",
"ShippingPrice",
"ShippingTax",
"PromotionDiscount",
"ShippingDiscount",
"ShippingAddress",
"IsBusinessOrder",
"IsGift",
"GiftWrapPrice",
"GiftWrapTax"
]

class GoogleSheets:
    def __init__(self, credentials, name: str):
        self.credentials = credentials
        self.name = name
        self.sheet_object = self._create_sheet_file()

    def _create_sheet_file(self) -> gspread.Spreadsheet:
        client = gspread.authorize(self.credentials)
        print("-----" + "CREATING GOOGLE SHEET FILE" + "-----")
        sheet_object = client.create(title=self.name, folder_id='1IXCU-4F4kObBHIRj0Y7-oGGX0yedlmWw')
        sheet_object.fetch_sheet_metadata
        return sheet_object

    def add_worksheet(self, name: str, index: int) -> gspread.Worksheet:
        worksheet = self.sheet_object.add_worksheet(title=name, rows=400, cols=10, index=index)
        print("-----" + "Adding worksheet named " + name + "-----")
        self.write_header_if_doesnt_exist(worksheet=worksheet, columns=HEADER)
        return worksheet
    
    def write_header_if_doesnt_exist(self, worksheet, columns: List[str]) -> None:
        data = worksheet.get_all_values()
        if not data:
            worksheet.insert_row(columns)

    def append_rows(self, rows: List[List]) -> None:
        last_row_number = len(self.sheet_object.col_values(1)) + 1
        self.sheet_object.insert_rows(rows, last_row_number)
