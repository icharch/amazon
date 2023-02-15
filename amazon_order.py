from dataclasses import dataclass, asdict

@dataclass
class AmazonOrder:
    order_id: str
    purchase_date: str
    order_status: str
    sku: str
    asin: str
    quantity_ordered: int
    currency_code: str
    sales_channel: str
    fulfillment_channel: str
    item_price: str
    item_tax: str
    shipping_price: str
    shipping_tax: str
    promotion_discount: str
    shipping_discount: str
    country_code: str
    is_business_order: bool
    is_gift: bool
    gift_wrap_price: str
    gift_wrap_tax: str
    