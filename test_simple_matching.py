#!/usr/bin/env python3
"""Simple test to demonstrate the area filtering issue and solution."""

import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_area_matching():
    """Test the area matching logic with sample data."""
    
    # Sample warnings with different area formats (simulated from RSS feed)
    sample_warnings = [
        {
            "title": "Weather warning for Uusimaa",
            "area": "Uusimaa",
            "summary": "Strong winds expected in the region"
        },
        {
            "title": "Snow warning",
            "area": "Southern Finland",
            "summary": "Heavy snowfall expected in Helsinki, Espoo, and surrounding areas"
        },
        {
            "title": "Ice warning",
            "area": "",  # No area field
            "summary": "Slippery conditions in Turku and nearby municipalities"
        },
        {
            "title": "Wind warning",
            "area": "Lappi",
            "summary": "Strong winds in northern Finland"
        },
        {
            "title": "Temperature warning",
            "area": "Helsingin seutu",
            "summary": "Very cold weather expected"
        }
    ]
    
    # Test different area configurations
    test_areas = ["Helsinki", "Uusimaa", "Turku", "Lapland", "Lappi"]
    
    for area_config in test_areas:
        print(f"\n=== Testing area config: '{area_config}' ===")
        area_lower = area_config.lower()
        matched_warnings = []
        
        for warning in sample_warnings:
            area_desc = warning.get("area", "").lower()
            title_lower = warning.get("title", "").lower()
            summary_lower = warning.get("summary", "").lower()
            
            logger.debug(f"Checking warning: {warning['title']}")
            logger.debug(f"  Area: '{area_desc}'")
            logger.debug(f"  Title: '{title_lower}'")
            logger.debug(f"  Summary: '{summary_lower[:50]}...'")
            
            # Current logic: check if area is in any text
            search_text = f"{area_desc} {title_lower} {summary_lower}"
            
            area_found = False
            
            if area_lower in search_text:
                area_found = True
                logger.debug(f"  ✓ Direct match found")
            else:
                # Try variant matching
                area_variants = [area_lower]
                
                # Add variants without Finnish suffixes
                for suffix in ['n', 'ssa', 'ssä', 'sta', 'stä', 'an', 'än', 'la', 'lä', 'lla', 'llä']:
                    if area_lower.endswith(suffix) and len(area_lower) > len(suffix) + 2:
                        variant = area_lower[:-len(suffix)]
                        if variant not in area_variants:
                            area_variants.append(variant)
                
                # Add variants with Finnish suffixes  
                for suffix in ['ssa', 'ssä', 'sta', 'stä', 'an', 'än', 'la', 'lä']:
                    variant = area_lower + suffix
                    if variant not in area_variants:
                        area_variants.append(variant)
                
                logger.debug(f"  Trying variants: {area_variants}")
                
                for variant in area_variants:
                    if variant in search_text:
                        area_found = True
                        logger.debug(f"  ✓ Variant match found: '{variant}'")
                        break
            
            if area_found:
                matched_warnings.append(warning)
                print(f"  ✓ MATCH: {warning['title']}")
            else:
                logger.debug(f"  ✗ No match")
        
        print(f"  Total matches: {len(matched_warnings)}/{len(sample_warnings)}")

if __name__ == "__main__":
    test_area_matching()