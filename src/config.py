import configparser
import os
from typing import Dict, Any, List

class Config:
    """Configuration manager for the backtesting framework"""
    
    def __init__(self, config_file: str = "config.ini"):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.load_config()
    
    def load_config(self):
        """Load configuration from file"""
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)
        else:
            # Create default config if file doesn't exist
            self.create_default_config()
    
    def create_default_config(self):
        """Create default configuration"""
        self.config['general'] = {
            'initial_capital': '100000',
            'data_source': 'yfinance',
            'default_period': '1y',
            'default_interval': '1d',
            'data_dir': 'data',
            'plots_dir': 'plots'
        }
        
        self.config['sma_crossover'] = {
            'short_period': '20',
            'long_period': '50'
        }
        
        self.config['risk_management'] = {
            'max_position_size': '0.95',
            'stop_loss_percent': '0.05',
            'take_profit_percent': '0.15'
        }
        
        self.config['performance'] = {
            'risk_free_rate': '0.02',
            'trading_days_per_year': '252'
        }
        
        self.config['plotting'] = {
            'figure_size_width': '15',
            'figure_size_height': '10',
            'dpi': '300',
            'save_format': 'png'
        }
        
        self.config['symbols'] = {
            'tech_stocks': 'AAPL,MSFT,GOOGL,AMZN,TSLA,NVDA',
            'market_indices': 'SPY,QQQ,IWM,VTI,EFA,EEM',
            'crypto': 'BTC-USD,ETH-USD,ADA-USD',
            'commodities': 'GLD,SLV,USO,DBA'
        }
        
        # Save default config
        with open(self.config_file, 'w') as f:
            self.config.write(f)
    
    def get(self, section: str, key: str, fallback=None) -> Any:
        """Get configuration value"""
        try:
            value = self.config.get(section, key)
            # Try to convert to appropriate type
            if value.replace('.', '').isdigit():
                return float(value) if '.' in value else int(value)
            elif value.lower() in ['true', 'false']:
                return value.lower() == 'true'
            return value
        except (configparser.NoSectionError, configparser.NoOptionError):
            return fallback
    
    def get_symbol_list(self, group: str) -> List[str]:
        """Get list of symbols from configuration"""
        symbols_str = self.get('symbols', group, '')
        return [s.strip() for s in symbols_str.split(',') if s.strip()]
    
    def get_sma_params(self) -> Dict[str, int]:
        """Get SMA crossover strategy parameters"""
        return {
            'short_period': self.get('sma_crossover', 'short_period', 20),
            'long_period': self.get('sma_crossover', 'long_period', 50)
        }
    
    def get_plotting_params(self) -> Dict[str, Any]:
        """Get plotting parameters"""
        return {
            'figsize': (
                self.get('plotting', 'figure_size_width', 15),
                self.get('plotting', 'figure_size_height', 10)
            ),
            'dpi': self.get('plotting', 'dpi', 300),
            'format': self.get('plotting', 'save_format', 'png')
        }
    
    def update(self, section: str, key: str, value: Any):
        """Update configuration value"""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = str(value)
    
    def save(self):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            self.config.write(f)

# Global config instance
config = Config()