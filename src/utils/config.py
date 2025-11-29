"""
Configuration and Logging Setup for Algorithmic Trading System

This module handles configuration management and logging setup for the trading system.
"""

import os
import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    DEFAULT_CONFIG = {
        "trading": {
            "initial_capital": 100000,
            "commission": 0.001,
            "slippage": 0.0005,
            "max_position_size": 0.1,
            "risk_free_rate": 0.02,
        },
        "data": {
            "default_source": "yahoo",
            "cache_enabled": True,
            "cache_duration_hours": 24,
        },
        "backtesting": {
            "benchmark": "SPY",
            "start_date": "2020-01-01",
            "end_date": None,
            "plot_results": True,
            "save_results": True,
        },
        "logging": {
            "level": "INFO",
            "log_to_file": True,
            "log_format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    }

    def __init__(self, config_file: Optional[str] = None):
        self.config = self.DEFAULT_CONFIG.copy()
        self.config_file = config_file

        if config_file and os.path.exists(config_file):
            self.load_config(config_file)

        self._load_env_variables()

    def load_config(self, config_file: str):
        try:
            with open(config_file, "r") as f:
                custom_config = json.load(f)
            self._deep_merge(self.config, custom_config)
        except Exception as e:
            logging.warning(f"Could not load config file {config_file}: {e}")

    def _deep_merge(self, default_dict: Dict, custom_dict: Dict):
        for key, value in custom_dict.items():
            if (
                isinstance(value, dict)
                and key in default_dict
                and isinstance(default_dict[key], dict)
            ):
                self._deep_merge(default_dict[key], value)
            else:
                default_dict[key] = value

    def _load_env_variables(self):
        initial_capital = os.getenv("INITIAL_CAPITAL")
        if initial_capital:
            self.config["trading"]["initial_capital"] = float(initial_capital)

        commission_rate = os.getenv("COMMISSION_RATE")
        if commission_rate:
            self.config["trading"]["commission"] = float(commission_rate)

        if os.getenv("DEFAULT_DATA_SOURCE"):
            self.config["data"]["default_source"] = os.getenv("DEFAULT_DATA_SOURCE")

        if os.getenv("LOG_LEVEL"):
            self.config["logging"]["level"] = os.getenv("LOG_LEVEL")

    def get(self, key_path: str, default: Any = None) -> Any:
        keys = key_path.split(".")
        current = self.config

        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default

        return current

    def set(self, key_path: str, value: Any):
        keys = key_path.split(".")
        current = self.config

        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        current[keys[-1]] = value

    def save_config(self, filepath: str):
        directory = os.path.dirname(filepath)
        if directory:
            os.makedirs(directory, exist_ok=True)

        with open(filepath, "w") as f:
            json.dump(self.config, f, indent=2, default=str)

    def get_trading_config(self) -> Dict:
        return self.config.get("trading", {})
    
    def get_data_config(self) -> Dict:
        return self.config.get("data", {})
    
    def get_backtesting_config(self) -> Dict:
        return self.config.get("backtesting", {})
    
    def get_api_keys(self) -> Dict:
        api_keys = {}
        alpha_vantage_key = os.getenv("ALPHA_VANTAGE_API_KEY")
        if alpha_vantage_key:
            api_keys["alpha_vantage"] = alpha_vantage_key
        alpaca_key = os.getenv("ALPACA_API_KEY")
        if alpaca_key:
            api_keys["alpaca_api"] = alpaca_key
        alpaca_secret = os.getenv("ALPACA_SECRET_KEY") 
        if alpaca_secret:
            api_keys["alpaca_secret"] = alpaca_secret
        return api_keys

    def update_config(self, section: str, values: Dict):
        if section not in self.config:
            self.config[section] = {}
        self.config[section].update(values)

    def validate_config(self) -> bool:
        try:
            trading = self.get_trading_config()
            if trading.get("initial_capital", 0) <= 0:
                return False
            if not (0 <= trading.get("commission", 0) < 1):
                return False
            if not (0 <= trading.get("max_position_size", 0) <= 1):
                return False
            data = self.get_data_config()
            valid_sources = ["yahoo", "alpha_vantage", "alpaca"]
            if data.get("default_source") not in valid_sources:
                return False
            return True
        except Exception:
            return False

    @property
    def trading(self) -> Dict:
        return self.get_trading_config()
    
    @property
    def data(self) -> Dict:
        return self.get_data_config()
        
    @property
    def backtesting(self) -> Dict:
        return self.get_backtesting_config()
        
    @property
    def logging(self) -> Dict:
        return self.config.get("logging", {})
    
    @trading.setter
    def trading(self, value: Dict):
        self.config["trading"] = value
    
    @data.setter  
    def data(self, value: Dict):
        self.config["data"] = value
        
    @backtesting.setter
    def backtesting(self, value: Dict):
        self.config["backtesting"] = value
        
    @logging.setter
    def logging(self, value: Dict):
        self.config["logging"] = value
    
    def to_dict(self) -> Dict:
        return self.config.copy()


def setup_logging(config: Config) -> logging.Logger:
    log_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs"
    )
    os.makedirs(log_dir, exist_ok=True)

    log_level = config.get("logging.level", "INFO")
    log_format = config.get("logging.log_format")
    log_to_file = config.get("logging.log_to_file", True)

    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))

    logger.handlers.clear()

    formatter = logging.Formatter(log_format)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if log_to_file:
        log_filename = f"trading_system_{datetime.now().strftime('%Y%m%d')}.log"
        log_filepath = os.path.join(log_dir, log_filename)

        file_handler = logging.FileHandler(log_filepath)
        file_handler.setLevel(getattr(logging, log_level.upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    app_logger = logging.getLogger("algo_trading")
    app_logger.setLevel(getattr(logging, log_level.upper()))
    app_logger.info("Logging system initialized")

    return app_logger


_config_instance = None


def get_config(config_file: Optional[str] = None) -> Config:
    global _config_instance

    if _config_instance is None:
        _config_instance = Config(config_file)

    return _config_instance

if __name__ == "__main__":
    create_default = False
    # This module is typically imported rather than executed directly
