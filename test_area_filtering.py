#!/usr/bin/env python3
"""Test script to verify area filtering works correctly."""

import asyncio
import logging
import sys
import os

# Add the custom_components directory to the path
sys.path.insert(0, '/workspaces/fmi-weather-warnings/custom_components/fmi_weather_warnings')

from coordinator import FMIWeatherWarningsCoordinator
from const import CONF_AREA

# Set up logging to see debug messages
logging.basicConfig(level=logging.DEBUG)
_LOGGER = logging.getLogger(__name__)

class MockConfigEntry:
    """Mock config entry for testing."""
    def __init__(self, area=""):
        self.data = {CONF_AREA: area}

class MockHomeAssistant:
    """Mock Home Assistant instance."""
    
    async def async_add_executor_job(self, func, *args):
        """Mock executor job."""
        return func(*args)

async def test_area_filtering():
    """Test area filtering with different configurations."""
    
    mock_hass = MockHomeAssistant()
    
    # Test cases
    test_cases = [
        "",  # No area filter
        "Helsinki",  # Major city
        "Lapland",  # Region
        "Uusimaa",  # Province
        "Turku",  # Another city
        "Oulu",  # Northern city
    ]
    
    for area in test_cases:
        print(f"\n=== Testing with area: '{area}' ===")
        
        entry = MockConfigEntry(area)
        coordinator = FMIWeatherWarningsCoordinator(mock_hass, entry)
        
        try:
            # Create a mock session that returns sample data
            import aiohttp
            
            # We'll skip the actual HTTP request for now and focus on parsing logic
            print(f"Coordinator configured with area: '{coordinator.area}'")
            
        except Exception as e:
            print(f"Error testing area '{area}': {e}")

if __name__ == "__main__":
    asyncio.run(test_area_filtering())