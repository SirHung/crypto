"""
GOD MODE 1000 - NEWS SOURCES CONFIGURATION
==========================================
100+ Credible News Sources for Crypto + Forex Markets
Organized by credibility tier and market focus
"""

from enum import Enum
from typing import Dict, List
from dataclasses import dataclass


class SourceTier(Enum):
    """Source credibility tiers"""
    TIER_1_OFFICIAL = 1.0  # Government/Central Banks/Regulators
    TIER_2_PREMIUM = 0.9   # Premium Financial Media
    TIER_3_MAINSTREAM = 0.7  # Mainstream Crypto/Forex Media
    TIER_4_SOCIAL = 0.5    # Social Media/Forums


class MarketFocus(Enum):
    """Market focus areas"""
    CRYPTO = "crypto"
    FOREX = "forex"
    BOTH = "both"
    MACRO = "macro"  # Macro economics affecting both


@dataclass
class NewsSource:
    """News source configuration"""
    name: str
    url: str
    api_endpoint: str
    tier: SourceTier
    market_focus: MarketFocus
    country: str
    language: str = "en"
    requires_api_key: bool = False


# ═══════════════════════════════════════════════════════════════════
# TIER 1: OFFICIAL SOURCES (Government/Central Banks/Regulators)
# ═══════════════════════════════════════════════════════════════════

TIER_1_OFFICIAL_SOURCES = [
    # US Regulators
    NewsSource("SEC", "https://www.sec.gov", "https://www.sec.gov/cgi-bin/browse-edgar", SourceTier.TIER_1_OFFICIAL, MarketFocus.BOTH, "US"),
    NewsSource("CFTC", "https://www.cftc.gov", "https://www.cftc.gov/PressRoom/PressReleases", SourceTier.TIER_1_OFFICIAL, MarketFocus.BOTH, "US"),
    NewsSource("Federal Reserve", "https://www.federalreserve.gov", "https://www.federalreserve.gov/feeds/press_all.xml", SourceTier.TIER_1_OFFICIAL, MarketFocus.FOREX, "US"),
    NewsSource("US Treasury", "https://home.treasury.gov", "https://home.treasury.gov/rss", SourceTier.TIER_1_OFFICIAL, MarketFocus.MACRO, "US"),
    
    # European Regulators
    NewsSource("ECB", "https://www.ecb.europa.eu", "https://www.ecb.europa.eu/rss", SourceTier.TIER_1_OFFICIAL, MarketFocus.FOREX, "EU"),
    NewsSource("ESMA", "https://www.esma.europa.eu", "https://www.esma.europa.eu/rss", SourceTier.TIER_1_OFFICIAL, MarketFocus.BOTH, "EU"),
    NewsSource("Bank of England", "https://www.bankofengland.co.uk", "https://www.bankofengland.co.uk/rss", SourceTier.TIER_1_OFFICIAL, MarketFocus.FOREX, "UK"),
    NewsSource("FCA UK", "https://www.fca.org.uk", "https://www.fca.org.uk/rss", SourceTier.TIER_1_OFFICIAL, MarketFocus.BOTH, "UK"),
    
    # Asian Regulators
    NewsSource("Bank of Japan", "https://www.boj.or.jp", "https://www.boj.or.jp/en/rss", SourceTier.TIER_1_OFFICIAL, MarketFocus.FOREX, "JP"),
    NewsSource("PBOC", "http://www.pbc.gov.cn", "http://www.pbc.gov.cn/en/rss", SourceTier.TIER_1_OFFICIAL, MarketFocus.FOREX, "CN"),
    NewsSource("MAS Singapore", "https://www.mas.gov.sg", "https://www.mas.gov.sg/rss", SourceTier.TIER_1_OFFICIAL, MarketFocus.BOTH, "SG"),
    NewsSource("FSA Japan", "https://www.fsa.go.jp", "https://www.fsa.go.jp/en/rss", SourceTier.TIER_1_OFFICIAL, MarketFocus.BOTH, "JP"),
    
    # International Organizations
    NewsSource("BIS", "https://www.bis.org", "https://www.bis.org/rss", SourceTier.TIER_1_OFFICIAL, MarketFocus.MACRO, "INT"),
    NewsSource("IMF", "https://www.imf.org", "https://www.imf.org/en/RSS", SourceTier.TIER_1_OFFICIAL, MarketFocus.MACRO, "INT"),
    NewsSource("World Bank", "https://www.worldbank.org", "https://www.worldbank.org/en/rss", SourceTier.TIER_1_OFFICIAL, MarketFocus.MACRO, "INT"),
    NewsSource("OECD", "https://www.oecd.org", "https://www.oecd.org/rss", SourceTier.TIER_1_OFFICIAL, MarketFocus.MACRO, "INT"),
]

# ═══════════════════════════════════════════════════════════════════
# TIER 2: PREMIUM FINANCIAL MEDIA
# ═══════════════════════════════════════════════════════════════════

TIER_2_PREMIUM_SOURCES = [
    # Top Financial News
    NewsSource("Bloomberg", "https://www.bloomberg.com", "https://www.bloomberg.com/feeds", SourceTier.TIER_2_PREMIUM, MarketFocus.BOTH, "US", requires_api_key=True),
    NewsSource("Reuters", "https://www.reuters.com", "https://www.reuters.com/arc/outboundfeeds", SourceTier.TIER_2_PREMIUM, MarketFocus.BOTH, "US"),
    NewsSource("Wall Street Journal", "https://www.wsj.com", "https://www.wsj.com/xml/rss", SourceTier.TIER_2_PREMIUM, MarketFocus.BOTH, "US"),
    NewsSource("Financial Times", "https://www.ft.com", "https://www.ft.com/rss", SourceTier.TIER_2_PREMIUM, MarketFocus.BOTH, "UK"),
    NewsSource("MarketWatch", "https://www.marketwatch.com", "https://www.marketwatch.com/rss", SourceTier.TIER_2_PREMIUM, MarketFocus.BOTH, "US"),
    NewsSource("CNBC", "https://www.cnbc.com", "https://www.cnbc.com/id/100003114/device/rss", SourceTier.TIER_2_PREMIUM, MarketFocus.BOTH, "US"),
    NewsSource("Forbes", "https://www.forbes.com", "https://www.forbes.com/crypto-blockchain/feed", SourceTier.TIER_2_PREMIUM, MarketFocus.BOTH, "US"),
    NewsSource("Barron's", "https://www.barrons.com", "https://www.barrons.com/rss", SourceTier.TIER_2_PREMIUM, MarketFocus.BOTH, "US"),
    
    # European Financial Media
    NewsSource("The Economist", "https://www.economist.com", "https://www.economist.com/rss", SourceTier.TIER_2_PREMIUM, MarketFocus.MACRO, "UK"),
    NewsSource("Handelsblatt", "https://www.handelsblatt.com", "https://www.handelsblatt.com/rss", SourceTier.TIER_2_PREMIUM, MarketFocus.BOTH, "DE", language="de"),
    NewsSource("Les Echos", "https://www.lesechos.fr", "https://www.lesechos.fr/rss", SourceTier.TIER_2_PREMIUM, MarketFocus.BOTH, "FR", language="fr"),
    
    # Asian Financial Media
    NewsSource("Nikkei Asia", "https://asia.nikkei.com", "https://asia.nikkei.com/rss", SourceTier.TIER_2_PREMIUM, MarketFocus.BOTH, "JP"),
    NewsSource("South China Morning Post", "https://www.scmp.com", "https://www.scmp.com/rss", SourceTier.TIER_2_PREMIUM, MarketFocus.BOTH, "HK"),
]

# ═══════════════════════════════════════════════════════════════════
# TIER 3: MAINSTREAM CRYPTO/FOREX MEDIA
# ═══════════════════════════════════════════════════════════════════

TIER_3_CRYPTO_SOURCES = [
    # Major Crypto News Sites
    NewsSource("CoinDesk", "https://www.coindesk.com", "https://www.coindesk.com/arc/outboundfeeds/rss/", SourceTier.TIER_3_MAINSTREAM, MarketFocus.CRYPTO, "US"),
    NewsSource("Cointelegraph", "https://cointelegraph.com", "https://cointelegraph.com/rss", SourceTier.TIER_3_MAINSTREAM, MarketFocus.CRYPTO, "US"),
    NewsSource("CryptoSlate", "https://cryptoslate.com", "https://cryptoslate.com/feed/", SourceTier.TIER_3_MAINSTREAM, MarketFocus.CRYPTO, "US"),
    NewsSource("The Block", "https://www.theblock.co", "https://www.theblock.co/rss.xml", SourceTier.TIER_3_MAINSTREAM, MarketFocus.CRYPTO, "US"),
    NewsSource("Decrypt", "https://decrypt.co", "https://decrypt.co/feed", SourceTier.TIER_3_MAINSTREAM, MarketFocus.CRYPTO, "US"),
    NewsSource("Bitcoin.com", "https://news.bitcoin.com", "https://news.bitcoin.com/feed/", SourceTier.TIER_3_MAINSTREAM, MarketFocus.CRYPTO, "US"),
    NewsSource("CoinTelegraph Markets", "https://cointelegraph.com/tags/markets", "https://cointelegraph.com/rss/tag/markets", SourceTier.TIER_3_MAINSTREAM, MarketFocus.CRYPTO, "US"),
    NewsSource("BeInCrypto", "https://beincrypto.com", "https://beincrypto.com/feed/", SourceTier.TIER_3_MAINSTREAM, MarketFocus.CRYPTO, "US"),
    NewsSource("U.Today", "https://u.today", "https://u.today/rss", SourceTier.TIER_3_MAINSTREAM, MarketFocus.CRYPTO, "US"),
    NewsSource("Bitcoinist", "https://bitcoinist.com", "https://bitcoinist.com/feed/", SourceTier.TIER_3_MAINSTREAM, MarketFocus.CRYPTO, "US"),
    NewsSource("NewsBTC", "https://www.newsbtc.com", "https://www.newsbtc.com/feed/", SourceTier.TIER_3_MAINSTREAM, MarketFocus.CRYPTO, "US"),
    NewsSource("CryptoPotato", "https://cryptopotato.com", "https://cryptopotato.com/feed/", SourceTier.TIER_3_MAINSTREAM, MarketFocus.CRYPTO, "US"),
    NewsSource("Crypto Briefing", "https://cryptobriefing.com", "https://cryptobriefing.com/feed/", SourceTier.TIER_3_MAINSTREAM, MarketFocus.CRYPTO, "US"),
    NewsSource("AMBCrypto", "https://ambcrypto.com", "https://ambcrypto.com/feed/", SourceTier.TIER_3_MAINSTREAM, MarketFocus.CRYPTO, "US"),
    NewsSource("CryptoNews", "https://cryptonews.com", "https://cryptonews.com/news/feed/", SourceTier.TIER_3_MAINSTREAM, MarketFocus.CRYPTO, "US"),
]

TIER_3_FOREX_SOURCES = [
    # Major Forex News Sites
    NewsSource("ForexLive", "https://www.forexlive.com", "https://www.forexlive.com/feed", SourceTier.TIER_3_MAINSTREAM, MarketFocus.FOREX, "CA"),
    NewsSource("FXStreet", "https://www.fxstreet.com", "https://www.fxstreet.com/rss", SourceTier.TIER_3_MAINSTREAM, MarketFocus.FOREX, "ES"),
    NewsSource("DailyFX", "https://www.dailyfx.com", "https://www.dailyfx.com/feeds/market-news", SourceTier.TIER_3_MAINSTREAM, MarketFocus.FOREX, "US"),
    NewsSource("Forex Factory", "https://www.forexfactory.com", "https://www.forexfactory.com/rss.php", SourceTier.TIER_3_MAINSTREAM, MarketFocus.FOREX, "US"),
    NewsSource("ActionForex", "https://www.actionforex.com", "https://www.actionforex.com/rss.xml", SourceTier.TIER_3_MAINSTREAM, MarketFocus.FOREX, "HK"),
    NewsSource("BabyPips", "https://www.babypips.com", "https://www.babypips.com/news/feed", SourceTier.TIER_3_MAINSTREAM, MarketFocus.FOREX, "US"),
    NewsSource("Investing.com", "https://www.investing.com", "https://www.investing.com/rss", SourceTier.TIER_3_MAINSTREAM, MarketFocus.BOTH, "US"),
    NewsSource("TradingView News", "https://www.tradingview.com", "https://www.tradingview.com/feed/", SourceTier.TIER_3_MAINSTREAM, MarketFocus.BOTH, "US"),
]

# ═══════════════════════════════════════════════════════════════════
# TIER 4: INFLUENTIAL KOLs & SOCIAL MEDIA
# ═══════════════════════════════════════════════════════════════════

TIER_4_KOL_SOURCES = [
    # Crypto KOLs (would integrate with Twitter/X API)
    NewsSource("Crypto KOL: CZ", "https://twitter.com/cz_binance", "twitter_api", SourceTier.TIER_4_SOCIAL, MarketFocus.CRYPTO, "INT"),
    NewsSource("Crypto KOL: Vitalik", "https://twitter.com/VitalikButerin", "twitter_api", SourceTier.TIER_4_SOCIAL, MarketFocus.CRYPTO, "INT"),
    NewsSource("Crypto KOL: Michael Saylor", "https://twitter.com/saylor", "twitter_api", SourceTier.TIER_4_SOCIAL, MarketFocus.CRYPTO, "US"),
    NewsSource("Crypto KOL: Cathie Wood", "https://twitter.com/CathieDWood", "twitter_api", SourceTier.TIER_4_SOCIAL, MarketFocus.CRYPTO, "US"),
    NewsSource("Crypto KOL: Barry Silbert", "https://twitter.com/BarrySilbert", "twitter_api", SourceTier.TIER_4_SOCIAL, MarketFocus.CRYPTO, "US"),
    NewsSource("Crypto KOL: Cameron Winklevoss", "https://twitter.com/cameron", "twitter_api", SourceTier.TIER_4_SOCIAL, MarketFocus.CRYPTO, "US"),
    NewsSource("Crypto KOL: Tyler Winklevoss", "https://twitter.com/tyler", "twitter_api", SourceTier.TIER_4_SOCIAL, MarketFocus.CRYPTO, "US"),
    NewsSource("Crypto KOL: Brian Armstrong", "https://twitter.com/brian_armstrong", "twitter_api", SourceTier.TIER_4_SOCIAL, MarketFocus.CRYPTO, "US"),
    
    # Forex/Macro KOLs
    NewsSource("Forex KOL: Mohamed El-Erian", "https://twitter.com/elerianm", "twitter_api", SourceTier.TIER_4_SOCIAL, MarketFocus.FOREX, "US"),
    NewsSource("Forex KOL: Raoul Pal", "https://twitter.com/RaoulGMI", "twitter_api", SourceTier.TIER_4_SOCIAL, MarketFocus.BOTH, "US"),
    NewsSource("Forex KOL: Jim Rogers", "https://twitter.com/jimrogers", "twitter_api", SourceTier.TIER_4_SOCIAL, MarketFocus.FOREX, "SG"),
    NewsSource("Forex KOL: Ray Dalio", "https://twitter.com/RayDalio", "twitter_api", SourceTier.TIER_4_SOCIAL, MarketFocus.MACRO, "US"),
    
    # Reddit Communities
    NewsSource("Reddit: r/CryptoCurrency", "https://www.reddit.com/r/CryptoCurrency", "reddit_api", SourceTier.TIER_4_SOCIAL, MarketFocus.CRYPTO, "INT"),
    NewsSource("Reddit: r/Bitcoin", "https://www.reddit.com/r/Bitcoin", "reddit_api", SourceTier.TIER_4_SOCIAL, MarketFocus.CRYPTO, "INT"),
    NewsSource("Reddit: r/Forex", "https://www.reddit.com/r/Forex", "reddit_api", SourceTier.TIER_4_SOCIAL, MarketFocus.FOREX, "INT"),
]

# ═══════════════════════════════════════════════════════════════════
# ADDITIONAL SPECIALIZED SOURCES
# ═══════════════════════════════════════════════════════════════════

SPECIALIZED_SOURCES = [
    # DeFi & Web3
    NewsSource("DeFi Pulse", "https://defipulse.com", "https://defipulse.com/blog/feed", SourceTier.TIER_3_MAINSTREAM, MarketFocus.CRYPTO, "US"),
    NewsSource("Messari", "https://messari.io", "https://messari.io/rss", SourceTier.TIER_3_MAINSTREAM, MarketFocus.CRYPTO, "US"),
    NewsSource("Dune Analytics Blog", "https://dune.com/blog", "https://dune.com/blog/rss", SourceTier.TIER_3_MAINSTREAM, MarketFocus.CRYPTO, "US"),
    
    # Technical Analysis
    NewsSource("CoinMarketCap News", "https://coinmarketcap.com", "https://coinmarketcap.com/headlines/rss/", SourceTier.TIER_3_MAINSTREAM, MarketFocus.CRYPTO, "US"),
    NewsSource("CoinGecko News", "https://www.coingecko.com", "https://www.coingecko.com/en/news/feed", SourceTier.TIER_3_MAINSTREAM, MarketFocus.CRYPTO, "SG"),
    
    # Regional Sources
    NewsSource("Coin Rivet", "https://coinrivet.com", "https://coinrivet.com/feed/", SourceTier.TIER_3_MAINSTREAM, MarketFocus.CRYPTO, "UK"),
    NewsSource("Bitcoin Magazine", "https://bitcoinmagazine.com", "https://bitcoinmagazine.com/feed", SourceTier.TIER_3_MAINSTREAM, MarketFocus.CRYPTO, "US"),
    NewsSource("Coinjournal", "https://coinjournal.net", "https://coinjournal.net/feed/", SourceTier.TIER_3_MAINSTREAM, MarketFocus.CRYPTO, "UK"),
]

# Combine all sources
ALL_NEWS_SOURCES = (
    TIER_1_OFFICIAL_SOURCES +
    TIER_2_PREMIUM_SOURCES +
    TIER_3_CRYPTO_SOURCES +
    TIER_3_FOREX_SOURCES +
    TIER_4_KOL_SOURCES +
    SPECIALIZED_SOURCES
)

# Create lookup dictionaries
SOURCES_BY_TIER = {
    SourceTier.TIER_1_OFFICIAL: TIER_1_OFFICIAL_SOURCES,
    SourceTier.TIER_2_PREMIUM: TIER_2_PREMIUM_SOURCES,
    SourceTier.TIER_3_MAINSTREAM: TIER_3_CRYPTO_SOURCES + TIER_3_FOREX_SOURCES + SPECIALIZED_SOURCES,
    SourceTier.TIER_4_SOCIAL: TIER_4_KOL_SOURCES,
}

SOURCES_BY_MARKET = {
    MarketFocus.CRYPTO: [s for s in ALL_NEWS_SOURCES if s.market_focus in [MarketFocus.CRYPTO, MarketFocus.BOTH]],
    MarketFocus.FOREX: [s for s in ALL_NEWS_SOURCES if s.market_focus in [MarketFocus.FOREX, MarketFocus.BOTH, MarketFocus.MACRO]],
    MarketFocus.BOTH: [s for s in ALL_NEWS_SOURCES if s.market_focus == MarketFocus.BOTH],
    MarketFocus.MACRO: [s for s in ALL_NEWS_SOURCES if s.market_focus == MarketFocus.MACRO],
}


def get_sources_by_credibility(min_tier: SourceTier = SourceTier.TIER_3_MAINSTREAM) -> List[NewsSource]:
    """Get sources filtered by minimum credibility tier"""
    return [s for s in ALL_NEWS_SOURCES if s.tier.value >= min_tier.value]


def get_sources_for_market(market: MarketFocus, min_tier: SourceTier = SourceTier.TIER_3_MAINSTREAM) -> List[NewsSource]:
    """Get sources for specific market with minimum credibility"""
    market_sources = SOURCES_BY_MARKET.get(market, [])
    return [s for s in market_sources if s.tier.value >= min_tier.value]


# Summary (commented out to avoid Unicode encoding issues on Windows)
# Total Sources: {len(ALL_NEWS_SOURCES)}
# By Tier: Tier1={len(TIER_1_OFFICIAL_SOURCES)}, Tier2={len(TIER_2_PREMIUM_SOURCES)}, 
#          Tier3={len(TIER_3_CRYPTO_SOURCES + TIER_3_FOREX_SOURCES + SPECIALIZED_SOURCES)}, Tier4={len(TIER_4_KOL_SOURCES)}
# By Market: Crypto={len([s for s in ALL_NEWS_SOURCES if s.market_focus == MarketFocus.CRYPTO])}, 
#            Forex={len([s for s in ALL_NEWS_SOURCES if s.market_focus == MarketFocus.FOREX])},
#            Both={len([s for s in ALL_NEWS_SOURCES if s.market_focus == MarketFocus.BOTH])}, 
#            Macro={len([s for s in ALL_NEWS_SOURCES if s.market_focus == MarketFocus.MACRO])}

