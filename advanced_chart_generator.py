"""
GOD MODE 1000 - ADVANCED CHART GENERATOR
Real-time professional trading charts with technical indicators
"""

# Fix Python 3.13 compatibility first
import python313_compatibility

# Import real libraries - NO BYPASS/FALLBACK
import pandas as pd
import numpy as np

import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import warnings
warnings.filterwarnings('ignore')

# pandas and numpy already imported at top with python313_compatibility fix

try:
    from unified_logging_manager import unified_logging
except ImportError:
    import logging
    unified_logging = logging.getLogger(__name__)

try:
    from real_market_data_fetcher import real_market_data_fetcher
except ImportError:
    real_market_data_fetcher = None

class AdvancedChartGenerator:
    """Professional trading charts with real-time data"""
    
    def __init__(self):
        """Initialize chart generator"""
        try:
            self.unified_logger = unified_logging.get_logger("chart_generator")
            self.chart_theme = self._get_professional_theme()
            self.unified_logger.info("Advanced Chart Generator initialized")
        except Exception as e:
            self.unified_logger.error(f"Failed to initialize chart generator: {e}")
            raise
    
    def _get_professional_theme(self) -> Dict[str, Any]:
        """Professional dark theme for charts"""
        return {
            'plot_bgcolor': '#0a0e27',
            'paper_bgcolor': '#0a0e27',
            'font': {'color': '#ffffff', 'family': 'Inter, sans-serif'},
            'xaxis': {'gridcolor': '#1e2139', 'linecolor': '#1e2139'},
            'yaxis': {'gridcolor': '#1e2139', 'linecolor': '#1e2139'},
            'colorway': ['#00ff94', '#00d4ff', '#a855f7', '#ff0066', '#ffea00']
        }
    
    def generate_candlestick_chart(self, symbol: str, timeframe: str = '1h', limit: int = 100) -> go.Figure:
        """Generate professional candlestick chart with volume"""
        try:
            # Get historical data
            if real_market_data_fetcher:
                data = real_market_data_fetcher.get_historical_data(symbol, timeframe, limit)
            else:
                return self._create_empty_chart("Market data unavailable")
            
            if not data or len(data) < 10:
                return self._create_empty_chart("Insufficient data")
            
            # Create DataFrame
            df = pd.DataFrame(data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Create subplots
            fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.03,
                row_heights=[0.7, 0.3],
                subplot_titles=(f'{symbol} Price', 'Volume')
            )
            
            # Candlestick
            fig.add_trace(
                go.Candlestick(
                    x=df['timestamp'],
                    open=df['open'],
                    high=df['high'],
                    low=df['low'],
                    close=df['close'],
                    name='Price',
                    increasing_line_color='#00ff94',
                    decreasing_line_color='#ff0066'
                ),
                row=1, col=1
            )
            
            # Volume bars
            colors = ['#00ff94' if df['close'].iloc[i] >= df['open'].iloc[i] else '#ff0066' 
                     for i in range(len(df))]
            
            fig.add_trace(
                go.Bar(
                    x=df['timestamp'],
                    y=df['volume'],
                    name='Volume',
                    marker_color=colors,
                    opacity=0.5
                ),
                row=2, col=1
            )
            
            # Apply theme
            fig.update_layout(
                **self.chart_theme,
                height=600,
                showlegend=True,
                xaxis_rangeslider_visible=False,
                hovermode='x unified'
            )
            
            return fig
            
        except Exception as e:
            self.unified_logger.error(f"Failed to generate candlestick chart: {e}")
            return self._create_empty_chart("Chart generation error")
    
    def generate_indicator_chart(self, symbol: str, indicators: List[str], 
                                timeframe: str = '1h', limit: int = 100) -> go.Figure:
        """Generate chart with technical indicators"""
        try:
            # Get historical data
            if real_market_data_fetcher:
                data = real_market_data_fetcher.get_historical_data(symbol, timeframe, limit)
            else:
                return self._create_empty_chart("Market data unavailable")
            
            if not data or len(data) < 20:
                return self._create_empty_chart("Insufficient data")
            
            df = pd.DataFrame(data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Calculate indicators
            if 'SMA' in indicators:
                df['SMA_20'] = df['close'].rolling(window=20).mean()
                df['SMA_50'] = df['close'].rolling(window=50).mean()
            
            if 'EMA' in indicators:
                df['EMA_12'] = df['close'].ewm(span=12, adjust=False).mean()
                df['EMA_26'] = df['close'].ewm(span=26, adjust=False).mean()
            
            if 'BB' in indicators:
                sma = df['close'].rolling(window=20).mean()
                std = df['close'].rolling(window=20).std()
                df['BB_upper'] = sma + (std * 2)
                df['BB_lower'] = sma - (std * 2)
            
            # Create figure
            fig = go.Figure()
            
            # Price line
            fig.add_trace(go.Scatter(
                x=df['timestamp'],
                y=df['close'],
                name='Price',
                line=dict(color='#00d4ff', width=2)
            ))
            
            # Add indicators
            if 'SMA' in indicators:
                fig.add_trace(go.Scatter(
                    x=df['timestamp'], y=df['SMA_20'],
                    name='SMA 20', line=dict(color='#00ff94', width=1)
                ))
                fig.add_trace(go.Scatter(
                    x=df['timestamp'], y=df['SMA_50'],
                    name='SMA 50', line=dict(color='#a855f7', width=1)
                ))
            
            if 'BB' in indicators:
                fig.add_trace(go.Scatter(
                    x=df['timestamp'], y=df['BB_upper'],
                    name='BB Upper', line=dict(color='#ffea00', width=1, dash='dash')
                ))
                fig.add_trace(go.Scatter(
                    x=df['timestamp'], y=df['BB_lower'],
                    name='BB Lower', line=dict(color='#ffea00', width=1, dash='dash'),
                    fill='tonexty', fillcolor='rgba(255,234,0,0.1)'
                ))
            
            fig.update_layout(
                **self.chart_theme,
                height=500,
                title=f'{symbol} with Technical Indicators',
                xaxis_title='Time',
                yaxis_title='Price',
                hovermode='x unified'
            )
            
            return fig
            
        except Exception as e:
            self.unified_logger.error(f"Failed to generate indicator chart: {e}")
            return self._create_empty_chart("Chart generation error")
    
    def generate_prediction_chart(self, symbol: str, prediction: Any) -> go.Figure:
        """Generate chart with prediction overlay"""
        try:
            # Get recent data
            if real_market_data_fetcher:
                data = real_market_data_fetcher.get_historical_data(symbol, '1h', 50)
            else:
                return self._create_empty_chart("Market data unavailable")
            
            if not data:
                return self._create_empty_chart("No data available")
            
            df = pd.DataFrame(data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            fig = go.Figure()
            
            # Price line
            fig.add_trace(go.Scatter(
                x=df['timestamp'],
                y=df['close'],
                name='Price',
                line=dict(color='#00d4ff', width=2)
            ))
            
            # Prediction levels
            current_price = df['close'].iloc[-1]
            current_time = df['timestamp'].iloc[-1]
            
            # Entry level
            fig.add_hline(
                y=prediction.entry_price,
                line_dash="solid",
                line_color="#00ff94",
                annotation_text=f"Entry: ${prediction.entry_price:,.2f}",
                annotation_position="right"
            )
            
            # Stop Loss
            fig.add_hline(
                y=prediction.stop_loss,
                line_dash="dash",
                line_color="#ff0066",
                annotation_text=f"SL: ${prediction.stop_loss:,.2f}",
                annotation_position="right"
            )
            
            # Take Profit
            fig.add_hline(
                y=prediction.take_profit,
                line_dash="dash",
                line_color="#00ff94",
                annotation_text=f"TP: ${prediction.take_profit:,.2f}",
                annotation_position="right"
            )
            
            # Signal annotation
            signal_color = "#00ff94" if "BUY" in prediction.final_signal.value else "#ff0066"
            fig.add_annotation(
                x=current_time,
                y=current_price,
                text=f"{prediction.final_signal.value}<br>{prediction.confidence_score:.0%}",
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor=signal_color,
                bgcolor=signal_color,
                font=dict(color='#000', size=12, family='Inter'),
                borderpad=4
            )
            
            fig.update_layout(
                **self.chart_theme,
                height=500,
                title=f'{symbol} - Enhanced Prediction Analysis',
                xaxis_title='Time',
                yaxis_title='Price',
                hovermode='x unified'
            )
            
            return fig
            
        except Exception as e:
            self.unified_logger.error(f"Failed to generate prediction chart: {e}")
            return self._create_empty_chart("Chart generation error")
    
    def _create_empty_chart(self, message: str) -> go.Figure:
        """Create empty chart with message"""
        fig = go.Figure()
        fig.add_annotation(
            text=message,
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=20, color='#cbd5e1')
        )
        fig.update_layout(
            **self.chart_theme,
            height=400
        )
        return fig

# Global instance
advanced_chart_generator = AdvancedChartGenerator()

