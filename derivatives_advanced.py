"""
GOD MODE 10000 - ADVANCED DERIVATIVES & OPTIONS TRADING MODULE
=============================================================
Options Greeks calculation, volatility surface analysis, delta-neutral strategies,
and advanced derivatives trading for crypto markets.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta, timezone
from enum import Enum
import asyncio
import math

try:
    from unified_logging_manager import unified_logging
except ImportError:
    import logging
    unified_logging = logging.getLogger(__name__)

class OptionType(Enum):
    CALL = "Call"
    PUT = "Put"

class GreeksCalculator:
    """Calculate option Greeks using Black-Scholes model"""
    
    @staticmethod
    def _calculate_d1_d2(S: float, K: float, T: float, r: float, sigma: float) -> Tuple[float, float]:
        """Calculate d1 and d2 for Black-Scholes"""
        if T <= 0 or sigma <= 0:
            return 0, 0
        
        d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
        d2 = d1 - sigma * math.sqrt(T)
        return d1, d2
    
    @staticmethod
    def _norm_cdf(x: float) -> float:
        """Cumulative distribution function for standard normal distribution"""
        return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0
    
    @staticmethod
    def _norm_pdf(x: float) -> float:
        """Probability density function for standard normal distribution"""
        return math.exp(-0.5 * x ** 2) / math.sqrt(2 * math.pi)
    
    @staticmethod
    def calculate_greeks(
        S: float,  # Current price
        K: float,  # Strike price
        T: float,  # Time to expiration (years)
        r: float,  # Risk-free rate
        sigma: float,  # Volatility
        option_type: OptionType
    ) -> Dict[str, float]:
        """Calculate all Greeks for an option"""
        
        if T <= 0:
            return {
                'delta': 1.0 if S > K else 0.0,
                'gamma': 0.0,
                'theta': 0.0,
                'vega': 0.0,
                'rho': 0.0
            }
        
        d1, d2 = GreeksCalculator._calculate_d1_d2(S, K, T, r, sigma)
        
        # Delta
        if option_type == OptionType.CALL:
            delta = GreeksCalculator._norm_cdf(d1)
        else:
            delta = GreeksCalculator._norm_cdf(d1) - 1
        
        # Gamma (same for calls and puts)
        gamma = GreeksCalculator._norm_pdf(d1) / (S * sigma * math.sqrt(T))
        
        # Vega (same for calls and puts, divided by 100 for 1% move)
        vega = S * GreeksCalculator._norm_pdf(d1) * math.sqrt(T) / 100
        
        # Theta
        term1 = -(S * GreeksCalculator._norm_pdf(d1) * sigma) / (2 * math.sqrt(T))
        if option_type == OptionType.CALL:
            term2 = -r * K * math.exp(-r * T) * GreeksCalculator._norm_cdf(d2)
            theta = (term1 + term2) / 365  # Per day
        else:
            term2 = r * K * math.exp(-r * T) * GreeksCalculator._norm_cdf(-d2)
            theta = (term1 + term2) / 365  # Per day
        
        # Rho (divided by 100 for 1% move)
        if option_type == OptionType.CALL:
            rho = K * T * math.exp(-r * T) * GreeksCalculator._norm_cdf(d2) / 100
        else:
            rho = -K * T * math.exp(-r * T) * GreeksCalculator._norm_cdf(-d2) / 100
        
        return {
            'delta': delta,
            'gamma': gamma,
            'theta': theta,
            'vega': vega,
            'rho': rho
        }

@dataclass
class OptionContract:
    """Represents an options contract"""
    symbol: str
    strike: float
    expiration: datetime
    option_type: OptionType
    current_price: float
    underlying_price: float
    implied_volatility: float
    greeks: Dict[str, float] = field(default_factory=dict)
    premium: float = 0.0
    volume: float = 0.0
    open_interest: float = 0.0

@dataclass
class VolatilitySurface:
    """Represents implied volatility surface"""
    symbol: str
    timestamp: datetime
    strikes: List[float]
    expirations: List[datetime]
    iv_matrix: List[List[float]]  # 2D array [expiration][strike]
    atm_iv: float
    skew: float  # Put-Call skew

class DerivativesAdvanced:
    """
    Advanced Derivatives Trading - God Mode 10000
    Professional options trading with Greeks, volatility surface, and delta-neutral strategies.
    """
    
    def __init__(self):
        self.logger = unified_logging.get_logger("derivatives_advanced")
        self.greeks_calculator = GreeksCalculator()
        self.risk_free_rate = 0.05  # 5% default
        self.logger.info("✅ Advanced Derivatives module initialized - God Mode 10000")
    
    async def get_option_chain(self, symbol: str, expiration: datetime) -> List[OptionContract]:
        """Fetch or simulate option chain for a symbol"""
        self.logger.info(f"Fetching option chain for {symbol}")
        
        try:
            # Simulate fetching current price
            await asyncio.sleep(0.1)
            current_price = 50000.0 if 'BTC' in symbol else 3000.0  # Dummy prices
            
            # Generate strikes around current price
            strikes = []
            for i in range(-5, 6):  # 11 strikes
                strike = current_price * (1 + i * 0.05)  # 5% intervals
                strikes.append(strike)
            
            # Calculate time to expiration
            T = (expiration - datetime.now(timezone.utc)).total_seconds() / (365.25 * 24 * 3600)
            
            # Simulate implied volatility
            base_iv = 0.80  # 80% IV for crypto
            
            options = []
            for strike in strikes:
                # Simulate different IVs (skew)
                moneyness = strike / current_price
                iv_adjustment = 0.1 * abs(1 - moneyness)  # Higher IV for OTM
                iv = base_iv + iv_adjustment
                
                for opt_type in [OptionType.CALL, OptionType.PUT]:
                    greeks = self.greeks_calculator.calculate_greeks(
                        S=current_price,
                        K=strike,
                        T=T,
                        r=self.risk_free_rate,
                        sigma=iv,
                        option_type=opt_type
                    )
                    
                    # Simulate premium calculation
                    premium = self._calculate_option_premium(
                        current_price, strike, T, self.risk_free_rate, iv, opt_type
                    )
                    
                    option = OptionContract(
                        symbol=symbol,
                        strike=strike,
                        expiration=expiration,
                        option_type=opt_type,
                        current_price=premium,
                        underlying_price=current_price,
                        implied_volatility=iv,
                        greeks=greeks,
                        premium=premium,
                        volume=abs(hash(f"{symbol}{strike}{opt_type}") % 1000),
                        open_interest=abs(hash(f"{symbol}{strike}{opt_type}oi") % 5000)
                    )
                    options.append(option)
            
            self.logger.info(f"✅ Generated {len(options)} option contracts")
            return options
            
        except Exception as e:
            self.logger.error(f"Error fetching option chain: {e}")
            return []
    
    def _calculate_option_premium(
        self, S: float, K: float, T: float, r: float, sigma: float, option_type: OptionType
    ) -> float:
        """Calculate option premium using Black-Scholes"""
        if T <= 0:
            return max(0, S - K) if option_type == OptionType.CALL else max(0, K - S)
        
        d1, d2 = self.greeks_calculator._calculate_d1_d2(S, K, T, r, sigma)
        
        if option_type == OptionType.CALL:
            premium = S * self.greeks_calculator._norm_cdf(d1) - K * math.exp(-r * T) * self.greeks_calculator._norm_cdf(d2)
        else:
            premium = K * math.exp(-r * T) * self.greeks_calculator._norm_cdf(-d2) - S * self.greeks_calculator._norm_cdf(-d1)
        
        return premium
    
    async def construct_volatility_surface(self, symbol: str) -> Optional[VolatilitySurface]:
        """Construct implied volatility surface for a symbol"""
        self.logger.info(f"Constructing volatility surface for {symbol}")
        
        try:
            # Generate expirations (7 days, 14 days, 30 days, 60 days, 90 days)
            expirations = [
                datetime.now(timezone.utc) + timedelta(days=d)
                for d in [7, 14, 30, 60, 90]
            ]
            
            # Get current price
            current_price = 50000.0 if 'BTC' in symbol else 3000.0
            
            # Generate strikes
            strikes = [current_price * (1 + i * 0.1) for i in range(-3, 4)]  # 7 strikes
            
            # Generate IV matrix
            iv_matrix = []
            atm_ivs = []
            
            for exp_idx, expiration in enumerate(expirations):
                T = (expiration - datetime.now(timezone.utc)).total_seconds() / (365.25 * 24 * 3600)
                iv_row = []
                
                for strike in strikes:
                    moneyness = strike / current_price
                    
                    # Base IV increases with time
                    base_iv = 0.70 + (exp_idx * 0.02)
                    
                    # Volatility smile/skew
                    if moneyness < 0.9:  # Deep OTM puts
                        iv = base_iv + 0.15
                    elif moneyness < 0.95:  # OTM puts
                        iv = base_iv + 0.08
                    elif moneyness > 1.1:  # OTM calls
                        iv = base_iv + 0.05
                    else:  # ATM
                        iv = base_iv
                    
                    iv_row.append(iv)
                    
                    # Track ATM IV
                    if abs(moneyness - 1.0) < 0.05:
                        atm_ivs.append(iv)
                
                iv_matrix.append(iv_row)
            
            atm_iv = sum(atm_ivs) / len(atm_ivs) if atm_ivs else 0.75
            
            # Calculate put-call skew
            otm_put_iv = iv_matrix[0][0]  # Lowest strike, shortest expiration
            otm_call_iv = iv_matrix[0][-1]  # Highest strike, shortest expiration
            skew = otm_put_iv - otm_call_iv
            
            surface = VolatilitySurface(
                symbol=symbol,
                timestamp=datetime.now(timezone.utc),
                strikes=strikes,
                expirations=expirations,
                iv_matrix=iv_matrix,
                atm_iv=atm_iv,
                skew=skew
            )
            
            self.logger.info(f"✅ Volatility surface constructed: ATM IV={atm_iv:.2%}, Skew={skew:.2%}")
            return surface
            
        except Exception as e:
            self.logger.error(f"Error constructing volatility surface: {e}")
            return None
    
    async def create_delta_neutral_strategy(
        self, symbol: str, capital: float
    ) -> Dict[str, Any]:
        """
        Create a delta-neutral options strategy (e.g., straddle, strangle)
        """
        self.logger.info(f"Creating delta-neutral strategy for {symbol}")
        
        try:
            # Get ATM options
            expiration = datetime.now(timezone.utc) + timedelta(days=30)
            options = await self.get_option_chain(symbol, expiration)
            
            if not options:
                return {'error': 'No options available'}
            
            # Find ATM options
            underlying_price = options[0].underlying_price
            atm_options = [opt for opt in options if abs(opt.strike - underlying_price) / underlying_price < 0.02]
            
            if not atm_options:
                return {'error': 'No ATM options found'}
            
            # Get ATM call and put
            atm_call = next((opt for opt in atm_options if opt.option_type == OptionType.CALL), None)
            atm_put = next((opt for opt in atm_options if opt.option_type == OptionType.PUT), None)
            
            if not atm_call or not atm_put:
                return {'error': 'Missing ATM options'}
            
            # Calculate straddle cost
            straddle_cost = atm_call.premium + atm_put.premium
            num_contracts = int(capital / straddle_cost) if straddle_cost > 0 else 0
            
            # Calculate combined Greeks
            combined_delta = (atm_call.greeks['delta'] + atm_put.greeks['delta']) * num_contracts
            combined_gamma = (atm_call.greeks['gamma'] + atm_put.greeks['gamma']) * num_contracts
            combined_vega = (atm_call.greeks['vega'] + atm_put.greeks['vega']) * num_contracts
            combined_theta = (atm_call.greeks['theta'] + atm_put.greeks['theta']) * num_contracts
            
            return {
                'strategy': 'ATM Straddle (Delta Neutral)',
                'symbol': symbol,
                'underlying_price': underlying_price,
                'strike': atm_call.strike,
                'expiration': expiration,
                'num_contracts': num_contracts,
                'total_cost': straddle_cost * num_contracts,
                'call_premium': atm_call.premium,
                'put_premium': atm_put.premium,
                'greeks': {
                    'delta': combined_delta,
                    'gamma': combined_gamma,
                    'vega': combined_vega,
                    'theta': combined_theta
                },
                'breakeven_upper': atm_call.strike + straddle_cost,
                'breakeven_lower': atm_call.strike - straddle_cost,
                'max_profit': 'Unlimited',
                'max_loss': straddle_cost * num_contracts,
                'recommendation': 'Use when expecting high volatility'
            }
            
        except Exception as e:
            self.logger.error(f"Error creating delta-neutral strategy: {e}")
            return {'error': str(e)}

derivatives_advanced = DerivativesAdvanced()

