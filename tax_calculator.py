"""
GOD MODE 1000 - TAX CALCULATOR MODULE
=====================================
Tax calculation, reporting, and compliance for crypto trading
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum

try:
    from .unified_logging_manager import unified_logging
except ImportError:
    import logging
    unified_logging = logging

# Use centralized pandas/numpy bypass
# Fix Python 3.13 compatibility first
from . import python313_compatibility

# Import real libraries - NO BYPASS/FALLBACK
import pandas as pd
import numpy as np



class TaxMethod(Enum):
    """Tax calculation methods"""
    FIFO = "fifo"  # First In First Out
    LIFO = "lifo"  # Last In First Out
    HIFO = "hifo"  # Highest In First Out
    SPEC_ID = "spec_id"  # Specific Identification


class TransactionType(Enum):
    """Transaction types"""
    BUY = "buy"
    SELL = "sell"
    TRANSFER_IN = "transfer_in"
    TRANSFER_OUT = "transfer_out"
    MINING = "mining"
    STAKING = "staking"
    AIRDROP = "airdrop"


@dataclass
class Transaction:
    """Transaction record"""
    date: datetime
    type: TransactionType
    symbol: str
    amount: float
    price: float
    fee: float
    total_cost: float


@dataclass
class TaxReport:
    """Tax report summary"""
    total_capital_gains: float
    short_term_gains: float
    long_term_gains: float
    total_income: float
    total_fees: float
    net_profit_loss: float
    tax_liability: float
    transactions_count: int


class TaxCalculator:
    """Tax Calculator - God Mode 1000"""
    
    def __init__(self, country: str = "US"):
        """Initialize Tax Calculator"""
        self.unified_logger = unified_logging.get_logger("tax_calculator")
        self.country = country
        
        # Tax rates (US default)
        self.short_term_rate = 0.37  # 37% for short-term (< 1 year)
        self.long_term_rate = 0.20   # 20% for long-term (>= 1 year)
        self.income_tax_rate = 0.37  # For mining, staking, airdrops
        
        # Holding period for long-term (days)
        self.long_term_days = 365
        
        self.transactions: List[Transaction] = []
        self.inventory: Dict[str, List[Dict]] = {}  # Symbol -> List of purchases
        
        self.unified_logger.info(f"✅ Tax Calculator initialized - {country}")
    
    def add_transaction(self, date: datetime, tx_type: str, symbol: str,
                       amount: float, price: float, fee: float = 0.0):
        """Add a transaction"""
        try:
            tx_type_enum = TransactionType(tx_type.lower())
            total_cost = amount * price + fee
            
            transaction = Transaction(
                date=date,
                type=tx_type_enum,
                symbol=symbol,
                amount=amount,
                price=price,
                fee=fee,
                total_cost=total_cost
            )
            
            self.transactions.append(transaction)
            
            # Update inventory
            if tx_type_enum == TransactionType.BUY:
                self._add_to_inventory(symbol, amount, price, date, fee)
            elif tx_type_enum == TransactionType.SELL:
                self._remove_from_inventory(symbol, amount, price, date, fee)
        
        except Exception as e:
            self.unified_logger.error(f"Add transaction error: {e}")
    
    def _add_to_inventory(self, symbol: str, amount: float, price: float, date: datetime, fee: float):
        """Add purchase to inventory"""
        if symbol not in self.inventory:
            self.inventory[symbol] = []
        
        self.inventory[symbol].append({
            'date': date,
            'amount': amount,
            'price': price,
            'cost_basis': price * amount + fee / amount if amount > 0 else price
        })
    
    def _remove_from_inventory(self, symbol: str, amount: float, sale_price: float,
                               sale_date: datetime, fee: float,
                               method: TaxMethod = TaxMethod.FIFO) -> Tuple[float, float]:
        """Remove from inventory and calculate gains"""
        if symbol not in self.inventory or not self.inventory[symbol]:
            return 0.0, 0.0
        
        remaining_amount = amount
        total_cost_basis = 0.0
        total_short_term = 0.0
        total_long_term = 0.0
        
        # Sort inventory based on method
        if method == TaxMethod.FIFO:
            inventory = sorted(self.inventory[symbol], key=lambda x: x['date'])
        elif method == TaxMethod.LIFO:
            inventory = sorted(self.inventory[symbol], key=lambda x: x['date'], reverse=True)
        elif method == TaxMethod.HIFO:
            inventory = sorted(self.inventory[symbol], key=lambda x: x['cost_basis'], reverse=True)
        else:
            inventory = self.inventory[symbol]
        
        i = 0
        while remaining_amount > 0 and i < len(inventory):
            lot = inventory[i]
            
            # Amount to sell from this lot
            sell_from_lot = min(remaining_amount, lot['amount'])
            
            # Cost basis
            cost_basis = sell_from_lot * lot['cost_basis']
            total_cost_basis += cost_basis
            
            # Proceeds
            proceeds = sell_from_lot * sale_price - (fee * sell_from_lot / amount)
            
            # Gain/Loss
            gain_loss = proceeds - cost_basis
            
            # Holding period
            holding_days = (sale_date - lot['date']).days
            
            if holding_days >= self.long_term_days:
                total_long_term += gain_loss
            else:
                total_short_term += gain_loss
            
            # Update lot
            lot['amount'] -= sell_from_lot
            if lot['amount'] <= 0:
                inventory.pop(i)
            else:
                i += 1
            
            remaining_amount -= sell_from_lot
        
        self.inventory[symbol] = inventory
        
        return total_short_term, total_long_term
    
    def generate_tax_report(self, year: int) -> TaxReport:
        """Generate tax report for a specific year"""
        try:
            total_short_term = 0.0
            total_long_term = 0.0
            total_income = 0.0
            total_fees = 0.0
            transactions_count = 0
            
            for tx in self.transactions:
                if tx.date.year != year:
                    continue
                
                transactions_count += 1
                total_fees += tx.fee
                
                if tx.type == TransactionType.SELL:
                    short_term, long_term = self._remove_from_inventory(
                        tx.symbol, tx.amount, tx.price, tx.date, tx.fee
                    )
                    total_short_term += short_term
                    total_long_term += long_term
                
                elif tx.type in [TransactionType.MINING, TransactionType.STAKING, TransactionType.AIRDROP]:
                    # Taxed as income at fair market value
                    income = tx.amount * tx.price
                    total_income += income
            
            # Calculate tax liability
            total_capital_gains = total_short_term + total_long_term
            capital_gains_tax = (total_short_term * self.short_term_rate +
                                total_long_term * self.long_term_rate)
            income_tax = total_income * self.income_tax_rate
            total_tax = capital_gains_tax + income_tax
            
            net_profit_loss = total_capital_gains + total_income - total_fees
            
            return TaxReport(
                total_capital_gains=total_capital_gains,
                short_term_gains=total_short_term,
                long_term_gains=total_long_term,
                total_income=total_income,
                total_fees=total_fees,
                net_profit_loss=net_profit_loss,
                tax_liability=total_tax,
                transactions_count=transactions_count
            )
        
        except Exception as e:
            self.unified_logger.error(f"Tax report generation error: {e}")
            return TaxReport(
                total_capital_gains=0.0,
                short_term_gains=0.0,
                long_term_gains=0.0,
                total_income=0.0,
                total_fees=0.0,
                net_profit_loss=0.0,
                tax_liability=0.0,
                transactions_count=0
            )
    
    def export_to_csv(self, filename: str, year: int):
        """Export transactions to CSV for tax filing"""
        try:
            year_txs = [tx for tx in self.transactions if tx.date.year == year]
            
            df = pd.DataFrame([{
                'Date': tx.date.strftime('%Y-%m-%d'),
                'Type': tx.type.value,
                'Symbol': tx.symbol,
                'Amount': tx.amount,
                'Price': tx.price,
                'Fee': tx.fee,
                'Total': tx.total_cost
            } for tx in year_txs])
            
            df.to_csv(filename, index=False)
            self.unified_logger.info(f"Tax report exported to {filename}")
            return True
        
        except Exception as e:
            self.unified_logger.error(f"CSV export error: {e}")
            return False
    
    def get_cost_basis(self, symbol: str) -> float:
        """Get current cost basis for a symbol"""
        try:
            if symbol not in self.inventory:
                return 0.0
            
            total_cost = sum(lot['amount'] * lot['cost_basis'] for lot in self.inventory[symbol])
            total_amount = sum(lot['amount'] for lot in self.inventory[symbol])
            
            return total_cost / total_amount if total_amount > 0 else 0.0
        
        except Exception as e:
            self.unified_logger.error(f"Cost basis calculation error: {e}")
            return 0.0


# Global instance
tax_calculator = TaxCalculator()

