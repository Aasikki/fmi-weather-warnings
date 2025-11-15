#!/usr/bin/env python3
"""Debug script to examine FMI RSS feed structure and test area filtering."""

import urllib.request
import xml.etree.ElementTree as ET
import re

def test_area_matching(area_config, warning_text):
    """Test area matching logic similar to the coordinator."""
    area_config = area_config.lower()
    warning_text = warning_text.lower()
    
    # Direct match
    if area_config in warning_text:
        return True, "direct_match"
    
    # Try more flexible matching for Finnish place names
    area_variants = [area_config]
    
    # Add variant without common Finnish suffixes
    for suffix in ['n', 'ssa', 'ssä', 'sta', 'stä', 'an', 'än', 'la', 'lä']:
        if area_config.endswith(suffix) and len(area_config) > len(suffix) + 2:
            area_variants.append(area_config[:-len(suffix)])
    
    # Check if any variant matches
    for variant in area_variants:
        if variant in warning_text:
            return True, f"variant_match: {variant}"
    
    return False, "no_match"

def fetch_and_parse_rss():
    """Fetch and parse the FMI RSS feed."""
    
    url = "https://alerts.fmi.fi/cap/feed/rss_en-GB.rss"
    
    print(f"Fetching: {url}")
    try:
        with urllib.request.urlopen(url) as response:
            content = response.read()
            
        print(f"Response length: {len(content)} bytes")
        
        # Parse as XML to examine structure
        root = ET.fromstring(content)
        
        # Find all entries/items
        entries = root.findall('.//item') or root.findall('.//entry')
        print(f"Found {len(entries)} entries/items")
        
        if len(entries) == 0:
            print("No warnings found in feed")
            return False
        
        # Test areas to check
        test_areas = ["Helsinki", "Lapland", "Uusimaa", "Turku", "Oulu", "Tampere"]
        
        print(f"\n=== Testing area matching with {len(test_areas)} test areas ===")
        
        # Examine each entry
        for i, entry in enumerate(entries[:5]):  # Look at first 5 entries
            print(f"\n--- Warning {i+1} ---")
            
            title = ""
            description = ""
            area_desc = ""
            
            # Extract key information
            for child in entry:
                tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                
                if tag == 'title':
                    title = child.text or ""
                    print(f"  Title: {title}")
                elif tag == 'description':
                    description = child.text or ""
                    print(f"  Description: {(description[:100] + '...') if len(description) > 100 else description}")
                elif 'area' in tag.lower():
                    area_desc = child.text or ""
                    print(f"  Area ({tag}): {area_desc}")
            
            # Combine all text for area matching
            combined_text = f"{title} {description} {area_desc}"
            
            print(f"  Combined text length: {len(combined_text)} chars")
            
            # Test each area
            for area in test_areas:
                matches, reason = test_area_matching(area, combined_text)
                status = "✓" if matches else "✗"
                print(f"    {status} {area}: {reason}")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    fetch_and_parse_rss()