import pytest
import os
import tempfile
from src.config import Config

def test_config_creation_and_loading():
    """Test config creation and loading"""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_file = os.path.join(temp_dir, "test_config.ini")
        config = Config(config_file)
        
        # Test that config was created
        assert os.path.exists(config_file)
        
        # Test default values
        assert config.get('general', 'initial_capital') == 100000
        assert config.get('sma_crossover', 'short_period') == 20
        assert config.get('sma_crossover', 'long_period') == 50

def test_config_get_with_type_conversion():
    """Test config get method with automatic type conversion"""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_file = os.path.join(temp_dir, "test_config.ini")
        config = Config(config_file)
        
        # Test integer conversion
        assert isinstance(config.get('general', 'initial_capital'), int)
        
        # Test float conversion
        assert isinstance(config.get('risk_management', 'max_position_size'), float)
        
        # Test string values
        assert isinstance(config.get('general', 'data_source'), str)

def test_config_symbol_lists():
    """Test getting symbol lists from config"""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_file = os.path.join(temp_dir, "test_config.ini")
        config = Config(config_file)
        
        tech_stocks = config.get_symbol_list('tech_stocks')
        assert isinstance(tech_stocks, list)
        assert len(tech_stocks) > 0
        assert 'AAPL' in tech_stocks

def test_config_sma_params():
    """Test getting SMA parameters"""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_file = os.path.join(temp_dir, "test_config.ini")
        config = Config(config_file)
        
        sma_params = config.get_sma_params()
        assert isinstance(sma_params, dict)
        assert 'short_period' in sma_params
        assert 'long_period' in sma_params
        assert isinstance(sma_params['short_period'], int)
        assert isinstance(sma_params['long_period'], int)

def test_config_plotting_params():
    """Test getting plotting parameters"""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_file = os.path.join(temp_dir, "test_config.ini")
        config = Config(config_file)
        
        plot_params = config.get_plotting_params()
        assert isinstance(plot_params, dict)
        assert 'figsize' in plot_params
        assert 'dpi' in plot_params
        assert 'format' in plot_params
        assert isinstance(plot_params['figsize'], tuple)

def test_config_update_and_save():
    """Test updating and saving configuration"""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_file = os.path.join(temp_dir, "test_config.ini")
        config = Config(config_file)
        
        # Update a value
        config.update('general', 'initial_capital', 200000)
        config.save()
        
        # Create new config instance to test persistence
        config2 = Config(config_file)
        assert config2.get('general', 'initial_capital') == 200000

def test_config_fallback_values():
    """Test fallback values for missing keys"""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_file = os.path.join(temp_dir, "test_config.ini")
        config = Config(config_file)
        
        # Test fallback for non-existent key
        value = config.get('nonexistent_section', 'nonexistent_key', 'default_value')
        assert value == 'default_value'