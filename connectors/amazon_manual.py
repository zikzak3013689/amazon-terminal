"""
Amazon India Manual Research & URL Parser Connector.
Generates compliant, verified direct research links for amazon.in without automated scraping.
"""

import re
from urllib.parse import quote_plus
from typing import Dict, Any, Optional

class AmazonManualConnector:
    """Provides safe research link generators and ASIN extraction."""

    ASIN_REGEX = re.compile(r"(?:/dp/|/gp/product/|/gp/aw/d/|/asin/|^)([B0-9][A-Z0-9]{9})(?:[/?&]|$)", re.IGNORECASE)

    @classmethod
    def extract_asin(cls, url_or_text: str) -> Optional[str]:
        """Extracts a valid 10-character Amazon ASIN from a URL or raw text."""
        if not url_or_text:
            return None
        text = url_or_text.strip()
        # Direct 10-char ASIN check
        if len(text) == 10 and re.match(r"^[B0-9][A-Z0-9]{9}$", text, re.IGNORECASE):
            return text.upper()
        match = cls.ASIN_REGEX.search(text)
        return match.group(1).upper() if match else None

    @staticmethod
    def build_amazon_in_product_url(asin: str) -> str:
        """Constructs canonical Amazon India listing link."""
        return f"https://www.amazon.in/dp/{asin.strip().upper()}"

    @staticmethod
    def build_amazon_in_search_url(keyword: str) -> str:
        """Constructs search results page on amazon.in."""
        return f"https://www.amazon.in/s?k={quote_plus(keyword.strip())}"

    @staticmethod
    def build_amazon_bestsellers_url(category_slug: Optional[str] = None) -> str:
        """Generates Amazon India Best Sellers directory link."""
        if category_slug:
            return f"https://www.amazon.in/gp/bestsellers/{category_slug}"
        return "https://www.amazon.in/gp/bestsellers"

    @staticmethod
    def build_amazon_movers_url(category_slug: Optional[str] = None) -> str:
        """Generates Amazon India Movers & Shakers link."""
        if category_slug:
            return f"https://www.amazon.in/gp/movers-and-shakers/{category_slug}"
        return "https://www.amazon.in/gp/movers-and-shakers"

    @staticmethod
    def build_amazon_new_releases_url(category_slug: Optional[str] = None) -> str:
        """Generates Amazon India Hot New Releases link."""
        if category_slug:
            return f"https://www.amazon.in/gp/new-releases/{category_slug}"
        return "https://www.amazon.in/gp/new-releases"

    @staticmethod
    def build_keepa_web_url(asin: str) -> str:
        """Generates Keepa web price/BSR chart link for Amazon India (Domain 10)."""
        return f"https://keepa.com/#!product/10-{asin.strip().upper()}"

    @staticmethod
    def build_indiamart_search_url(keyword: str) -> str:
        """Generates domestic supplier search on IndiaMART."""
        return f"https://dir.indiamart.com/search.mp?ss={quote_plus(keyword.strip())}"

    @staticmethod
    def build_ip_india_trademark_url() -> str:
        """Link to official Indian Intellectual Property trademark database."""
        return "https://ipindiaonline.gov.in/tmrpublicsearch/frmmain.aspx"

    @classmethod
    def get_research_toolkit_links(cls, keyword: str, asin: Optional[str] = None) -> Dict[str, str]:
        """Returns structured research deep links for any product or keyword."""
        links = {
            "Amazon.in Search": cls.build_amazon_in_search_url(keyword),
            "Amazon.in Best Sellers": cls.build_amazon_bestsellers_url(),
            "Amazon.in Movers & Shakers": cls.build_amazon_movers_url(),
            "Amazon.in Hot New Releases": cls.build_amazon_new_releases_url(),
            "IndiaMART Sourcing": cls.build_indiamart_search_url(keyword),
            "India IP Trademark Portal": cls.build_ip_india_trademark_url(),
        }
        if asin:
            links["Amazon.in Listing"] = cls.build_amazon_in_product_url(asin)
            links["Keepa India Price Chart"] = cls.build_keepa_web_url(asin)
        return links
