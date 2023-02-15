from dataclasses import dataclass, asdict
from sp_api.base import Marketplaces
import const

@dataclass
class CountryConfig:
    marketplace: Marketplaces
    google_worksheet_name: str
    refresh_token: str

configs = [
CountryConfig(Marketplaces.BE, const.GOOGLE_WORKSHEET_NAME_BE, const.REFRESH_TOKEN_BE),
CountryConfig(Marketplaces.SE, const.GOOGLE_WORKSHEET_NAME_SE, const.REFRESH_TOKEN_SE),
CountryConfig(Marketplaces.NL, const.GOOGLE_WORKSHEET_NAME_NL, const.REFRESH_TOKEN_NL),
CountryConfig(Marketplaces.ES, const.GOOGLE_WORKSHEET_NAME_ES, const.REFRESH_TOKEN_ES), 
CountryConfig(Marketplaces.IT, const.GOOGLE_WORKSHEET_NAME_IT, const.REFRESH_TOKEN_IT),
CountryConfig(Marketplaces.FR, const.GOOGLE_WORKSHEET_NAME_FR, const.REFRESH_TOKEN_FR), 
CountryConfig(Marketplaces.DE, const.GOOGLE_WORKSHEET_NAME_DE, const.REFRESH_TOKEN_DE), 
CountryConfig(Marketplaces.UK, const.GOOGLE_WORKSHEET_NAME_UK, const.REFRESH_TOKEN_UK)
]