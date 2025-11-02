"""
GOD MODE 10000 - CROSS-CHAIN ANALYZER
======================================
Multi-chain price monitoring and arbitrage detection

Features:
- Monitor prices across ETH, BSC, Polygon, Arbitrum, Optimism
- Cross-chain arbitrage opportunities
- Bridge fee analysis
- Multi-chain portfolio tracking
- Layer 2 analytics
"""

import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import asyncio

try:
    from .unified_logging_manager import unified_logging
except ImportError:
    import logging
    unified_logging = logging

try:
    from web3 import Web3
except ImportError:
    Web3 = None


class Chain(Enum):
    """Supported blockchain networks"""
    ETHEREUM = "ethereum"
    BSC = "bsc"
    POLYGON = "polygon"
    ARBITRUM = "arbitrum"
    OPTIMISM = "optimism"
    AVALANCHE = "avalanche"
    FANTOM = "fantom"


@dataclass
class ChainInfo:
    """Blockchain network information"""
    chain: Chain
    chain_id: int
    rpc_url: str
    explorer_url: str
    native_token: str
    bridge_addresses: List[str]


@dataclass
class CrossChainPrice:
    """Price data across chains"""
    token_symbol: str
    token_address_by_chain: Dict[Chain, str]
    prices_by_chain: Dict[Chain, float]
    volumes_by_chain: Dict[Chain, float]
    liquidity_by_chain: Dict[Chain, float]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class CrossChainArbitrage:
    """Cross-chain arbitrage opportunity"""
    token_symbol: str
    buy_chain: Chain
    sell_chain: Chain
    buy_price: float
    sell_price: float
    price_diff_pct: float
    bridge_fee: float
    bridge_time_minutes: int
    net_profit_pct: float
    min_amount_usd: float  # Minimum profitable amount
    confidence: float  # 0-1


@dataclass
class BridgeInfo:
    """Bridge information"""
    name: str
    from_chain: Chain
    to_chain: Chain
    fee_pct: float
    fixed_fee_usd: float
    avg_time_minutes: int
    max_amount: float


class CrossChainAnalyzer:
    """Cross-Chain Analysis System - God Mode 10000"""
    
    def __init__(self):
        """Initialize cross-chain analyzer"""
        self.logger = unified_logging.get_logger("cross_chain_analyzer") if hasattr(unified_logging, 'get_logger') else unified_logging
        self.unified_logger = self.logger  # Alias for consistency
        
        # Chain configurations
        self.chains = {
            Chain.ETHEREUM: ChainInfo(
                chain=Chain.ETHEREUM,
                chain_id=1,
                rpc_url='https://eth.public-rpc.com',
                explorer_url='https://etherscan.io',
                native_token='ETH',
                bridge_addresses=[]
            ),
            Chain.BSC: ChainInfo(
                chain=Chain.BSC,
                chain_id=56,
                rpc_url='https://bsc-dataseed.binance.org',
                explorer_url='https://bscscan.com',
                native_token='BNB',
                bridge_addresses=[]
            ),
            Chain.POLYGON: ChainInfo(
                chain=Chain.POLYGON,
                chain_id=137,
                rpc_url='https://polygon-rpc.com',
                explorer_url='https://polygonscan.com',
                native_token='MATIC',
                bridge_addresses=[]
            ),
            Chain.ARBITRUM: ChainInfo(
                chain=Chain.ARBITRUM,
                chain_id=42161,
                rpc_url='https://arb1.arbitrum.io/rpc',
                explorer_url='https://arbiscan.io',
                native_token='ETH',
                bridge_addresses=[]
            ),
            Chain.OPTIMISM: ChainInfo(
                chain=Chain.OPTIMISM,
                chain_id=10,
                rpc_url='https://mainnet.optimism.io',
                explorer_url='https://optimistic.etherscan.io',
                native_token='ETH',
                bridge_addresses=[]
            ),
        }
        
        # Web3 connections
        self.w3_connections = {}
        self._initialize_connections()
        
        # Bridge configurations
        self.bridges = self._load_bridge_configs()
        
        # Token mappings across chains
        self.token_mappings = self._load_token_mappings()
        
        self.logger.info("✅ Cross-Chain Analyzer initialized - God Mode 10000")
    
    def _initialize_connections(self):
        """Initialize Web3 connections to all chains"""
        try:
            if not Web3:
                self.logger.warning("Web3 not available")
                return
            
            for chain, info in self.chains.items():
                try:
                    w3 = Web3(Web3.HTTPProvider(info.rpc_url))
                    if w3.is_connected():
                        self.w3_connections[chain] = w3
                        self.logger.info(f"✅ Connected to {chain.value}")
                except Exception as e:
                    self.logger.warning(f"Failed to connect to {chain.value}: {e}")
        
        except Exception as e:
            self.logger.error(f"Connection initialization failed: {e}")
    
    def _load_bridge_configs(self) -> List[BridgeInfo]:
        """Load bridge configurations"""
        return [
            BridgeInfo(
                name="Polygon Bridge",
                from_chain=Chain.ETHEREUM,
                to_chain=Chain.POLYGON,
                fee_pct=0.001,
                fixed_fee_usd=5.0,
                avg_time_minutes=15,
                max_amount=1000000
            ),
            BridgeInfo(
                name="Arbitrum Bridge",
                from_chain=Chain.ETHEREUM,
                to_chain=Chain.ARBITRUM,
                fee_pct=0.0005,
                fixed_fee_usd=3.0,
                avg_time_minutes=10,
                max_amount=5000000
            ),
            BridgeInfo(
                name="Optimism Bridge",
                from_chain=Chain.ETHEREUM,
                to_chain=Chain.OPTIMISM,
                fee_pct=0.0005,
                fixed_fee_usd=3.0,
                avg_time_minutes=10,
                max_amount=5000000
            ),
            BridgeInfo(
                name="BSC Bridge",
                from_chain=Chain.ETHEREUM,
                to_chain=Chain.BSC,
                fee_pct=0.002,
                fixed_fee_usd=10.0,
                avg_time_minutes=5,
                max_amount=2000000
            ),
        ]
    
    def _load_token_mappings(self) -> Dict[str, Dict[Chain, str]]:
        """Load token address mappings across chains"""
        return {
            'USDC': {
                Chain.ETHEREUM: '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
                Chain.POLYGON: '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174',
                Chain.ARBITRUM: '0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8',
                Chain.OPTIMISM: '0x7F5c764cBc14f9669B88837ca1490cCa17c31607',
                Chain.BSC: '0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d',
            },
            'USDT': {
                Chain.ETHEREUM: '0xdAC17F958D2ee523a2206206994597C13D831ec7',
                Chain.POLYGON: '0xc2132D05D31c914a87C6611C10748AEb04B58e8F',
                Chain.BSC: '0x55d398326f99059fF775485246999027B3197955',
            },
            'WETH': {
                Chain.ETHEREUM: '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
                Chain.POLYGON: '0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619',
                Chain.ARBITRUM: '0x82aF49447D8a07e3bd95BD0d56f35241523fBab1',
                Chain.OPTIMISM: '0x4200000000000000000000000000000000000006',
            },
            'WBTC': {
                Chain.ETHEREUM: '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599',
                Chain.POLYGON: '0x1BFD67037B42Cf73acF2047067bd4F2C47D9BfD6',
                Chain.ARBITRUM: '0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f',
                Chain.OPTIMISM: '0x68f180fcCe6836688e9084f035309E29Bf0A2095',
            },
        }
    
    def _extract_base_token(self, symbol: str) -> str:
        """Extract base token from trading pair (e.g., BTC/USDT -> BTC)"""
        if '/' in symbol:
            base = symbol.split('/')[0]
            # Map common crypto symbols to their wrapped equivalents
            token_map = {
                'BTC': 'WBTC',
                'ETH': 'WETH'
            }
            return token_map.get(base, base)
        return symbol
    
    async def get_cross_chain_prices(self, token_symbol: str) -> CrossChainPrice:
        """Get prices for token across all chains"""
        try:
            # Extract base token if trading pair provided
            base_token = self._extract_base_token(token_symbol)
            
            if base_token not in self.token_mappings:
                self.logger.debug(f"Token {base_token} (from {token_symbol}) not in mappings, using fallback")
                # Return None to gracefully skip cross-chain analysis for unsupported tokens
                return None
            
            token_addresses = self.token_mappings[base_token]
            prices = {}
            volumes = {}
            liquidity = {}
            
            # Fetch prices from each chain in parallel
            tasks = []
            for chain in token_addresses.keys():
                if chain in self.w3_connections:
                    task = self._get_token_price(chain, token_addresses[chain])
                    tasks.append((chain, task))
            
            # Gather results
            for chain, task in tasks:
                try:
                    price_data = await task
                    prices[chain] = price_data['price']
                    volumes[chain] = price_data.get('volume_24h', 0)
                    liquidity[chain] = price_data.get('liquidity', 0)
                except Exception as e:
                    self.logger.debug(f"Failed to get price on {chain.value}: {e}")
            
            return CrossChainPrice(
                token_symbol=token_symbol,
                token_address_by_chain=token_addresses,
                prices_by_chain=prices,
                volumes_by_chain=volumes,
                liquidity_by_chain=liquidity
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get cross-chain prices: {e}")
            raise
    
    async def _get_token_price(self, chain: Chain, token_address: str) -> Dict:
        """Get token price on specific chain"""
        try:
            # Simulated price fetching (would use real DEX APIs)
            await asyncio.sleep(0.1)
            
            # Base price with small variation per chain
            base_price = 1.00
            variation = hash(chain.value) % 100 / 10000  # 0-1% variation
            
            return {
                'price': base_price + variation,
                'volume_24h': 1000000 + hash(chain.value) % 1000000,
                'liquidity': 5000000 + hash(chain.value) % 5000000,
            }
            
        except Exception as e:
            self.logger.error(f"Price fetch failed on {chain.value}: {e}")
            return {'price': 0, 'volume_24h': 0, 'liquidity': 0}
    
    def find_arbitrage_opportunities(self, token_symbol: str, 
                                    min_profit_pct: float = 0.5) -> List[CrossChainArbitrage]:
        """Find cross-chain arbitrage opportunities"""
        try:
            # Get prices across chains
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            price_data = loop.run_until_complete(self.get_cross_chain_prices(token_symbol))
            loop.close()
            
            opportunities = []
            chains_list = list(price_data.prices_by_chain.keys())
            
            # Compare all chain pairs
            for i, chain1 in enumerate(chains_list):
                for chain2 in chains_list[i+1:]:
                    price1 = price_data.prices_by_chain[chain1]
                    price2 = price_data.prices_by_chain[chain2]
                    
                    # Check both directions
                    if price1 < price2:
                        buy_chain, sell_chain = chain1, chain2
                        buy_price, sell_price = price1, price2
                    else:
                        buy_chain, sell_chain = chain2, chain1
                        buy_price, sell_price = price2, price1
                    
                    price_diff_pct = ((sell_price - buy_price) / buy_price) * 100
                    
                    # Get bridge fee
                    bridge = self._find_bridge(buy_chain, sell_chain)
                    if not bridge:
                        continue
                    
                    # Calculate net profit
                    bridge_cost_pct = bridge.fee_pct * 100
                    net_profit_pct = price_diff_pct - bridge_cost_pct
                    
                    if net_profit_pct >= min_profit_pct:
                        # Calculate minimum amount for profitability
                        min_amount = bridge.fixed_fee_usd / (net_profit_pct / 100)
                        
                        opportunity = CrossChainArbitrage(
                            token_symbol=token_symbol,
                            buy_chain=buy_chain,
                            sell_chain=sell_chain,
                            buy_price=buy_price,
                            sell_price=sell_price,
                            price_diff_pct=price_diff_pct,
                            bridge_fee=bridge.fee_pct * 100,
                            bridge_time_minutes=bridge.avg_time_minutes,
                            net_profit_pct=net_profit_pct,
                            min_amount_usd=min_amount,
                            confidence=0.8
                        )
                        
                        opportunities.append(opportunity)
                        
                        self.logger.info(
                            f"🎯 Cross-chain arbitrage: {token_symbol} "
                            f"{buy_chain.value} -> {sell_chain.value}: "
                            f"{net_profit_pct:.2f}% profit"
                        )
            
            # Sort by net profit
            opportunities.sort(key=lambda x: x.net_profit_pct, reverse=True)
            
            return opportunities
            
        except Exception as e:
            self.logger.error(f"Arbitrage search failed: {e}")
            return []
    
    def _find_bridge(self, from_chain: Chain, to_chain: Chain) -> Optional[BridgeInfo]:
        """Find bridge between two chains"""
        for bridge in self.bridges:
            if bridge.from_chain == from_chain and bridge.to_chain == to_chain:
                return bridge
            if bridge.to_chain == from_chain and bridge.from_chain == to_chain:
                # Reverse direction
                return BridgeInfo(
                    name=bridge.name,
                    from_chain=to_chain,
                    to_chain=from_chain,
                    fee_pct=bridge.fee_pct,
                    fixed_fee_usd=bridge.fixed_fee_usd,
                    avg_time_minutes=bridge.avg_time_minutes,
                    max_amount=bridge.max_amount
                )
        return None
    
    def get_chain_statistics(self) -> Dict:
        """Get statistics for all monitored chains"""
        try:
            stats = {}
            
            for chain, w3 in self.w3_connections.items():
                try:
                    stats[chain.value] = {
                        'connected': w3.is_connected(),
                        'latest_block': w3.eth.block_number,
                        'gas_price_gwei': w3.from_wei(w3.eth.gas_price, 'gwei'),
                        'chain_id': self.chains[chain].chain_id,
                    }
                except Exception as e:
                    stats[chain.value] = {'connected': False, 'error': str(e)}
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Statistics failed: {e}")
            return {}
    
    def get_supported_tokens(self) -> List[str]:
        """Get list of supported tokens"""
        return list(self.token_mappings.keys())
    
    def get_supported_chains(self) -> List[str]:
        """Get list of supported chains"""
        return [chain.value for chain in self.chains.keys()]
    
    def _run_async_cross_chain(self, symbol: str):
        """Helper to run async cross-chain in new event loop"""
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.get_cross_chain_prices(symbol))
        finally:
            loop.close()
    
    def analyze_cross_chain_flows_sync(self, symbol: str) -> Dict[str, Any]:
        """Synchronous cross-chain flow analysis for integration"""
        try:
            # Get cross-chain prices
            import asyncio
            
            # Handle both running and non-running event loop scenarios
            try:
                loop = asyncio.get_running_loop()
                # Event loop is running, use thread executor
                self.unified_logger.debug("Event loop already running, using async wrapper")
                
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(self._run_async_cross_chain, symbol)
                    cross_chain_price = future.result(timeout=10)
            except RuntimeError:
                # No event loop running, safe to create one
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                cross_chain_price = loop.run_until_complete(self.get_cross_chain_prices(symbol))
                loop.close()
            
            # Return early if token not supported (None returned from get_cross_chain_prices)
            if cross_chain_price is None:
                return {
                    'cross_chain_flow': 'neutral',
                    'confidence': 0.5,
                    'net_flow': 0,
                    'arbitrage_opportunities': []
                }
            
            if cross_chain_price:
                # Calculate net flow based on price differences
                prices = cross_chain_price.prices_by_chain
                if prices:
                    avg_price = sum(prices.values()) / len(prices)
                    price_variance = sum((p - avg_price) ** 2 for p in prices.values()) / len(prices)
                    
                    # Estimate flow based on price variance
                    net_flow = price_variance * 1000  # Scale for meaningful values
                    flow_velocity = abs(net_flow) / avg_price if avg_price > 0 else 0
                    
                    return {
                        'net_flow': net_flow,
                        'flow_velocity': flow_velocity,
                        'bridge_activity': len(prices) * 0.1,  # Estimate based on active chains
                        'cross_chain_volume': avg_price * 1000000,  # Estimate volume
                        'confidence': min(0.9, len(prices) / 5.0)  # Confidence based on data availability
                    }
            
            # Default return if no data
            return {
                'net_flow': 0,
                'flow_velocity': 0,
                'bridge_activity': 0,
                'cross_chain_volume': 0,
                'confidence': 0.5
            }
            
        except Exception as e:
            self.unified_logger.error(f"Error in synchronous cross-chain analysis: {e}")
            return {
                'net_flow': 0,
                'flow_velocity': 0,
                'bridge_activity': 0,
                'cross_chain_volume': 0,
                'confidence': 0.5
            }


# Global instance
cross_chain_analyzer = CrossChainAnalyzer()

