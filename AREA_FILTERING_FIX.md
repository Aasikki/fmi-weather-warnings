# FMI Weather Warnings - Area Filtering Fix

## Problem
The integration works when no location is specified, but fails to find warnings when a specific location/area is configured, even for locations that have active warnings.

## Root Cause Analysis
The area filtering logic had several issues:

1. **Missing area information**: If the RSS feed entries don't have proper `cap_areadesc` fields, warnings were being filtered out incorrectly
2. **Strict matching**: The area matching was too strict and didn't handle Finnish place name variations
3. **No fallback logic**: Warnings without area information were being excluded even if they might be relevant
4. **Limited debugging**: It was hard to diagnose what was happening during filtering

## Changes Made

### 1. Enhanced Area Parsing (`coordinator.py`)
- Improved extraction of area information from multiple sources
- Added fallback to extract area info from title/summary if CAP fields are empty
- Added debugging to show what CAP attributes are available

### 2. Improved Area Matching Logic
- **Inclusive approach**: If a warning has no area information, include it rather than filter it out
- **Finnish language support**: Handle common Finnish suffixes/cases (ssa, ssä, sta, stä, la, lä, etc.)
- **Variant matching**: Try multiple variations of place names (e.g., "Helsinki" matches "Helsingissä")
- **Extended debugging**: Log search text and matching process for troubleshooting

### 3. Better User Experience
- Updated config flow description with better examples
- More detailed logging for debugging area filtering issues

## Testing the Fix

### 1. Enable Debug Logging
Add this to your Home Assistant `configuration.yaml`:

```yaml
logger:
  default: warning
  logs:
    custom_components.fmi_weather_warnings: debug
```

### 2. Test Different Area Configurations
Try configuring the integration with:
- `Helsinki` - Should match warnings for Helsinki area
- `Uusimaa` - Should match warnings for Uusimaa region  
- `Lapland` or `Lappi` - Should match northern Finland warnings
- `Turku` - Should match warnings for Turku area

### 3. Check the Logs
After configuring with a location, check the Home Assistant logs for debug messages like:
```
DEBUG: Checking area filter: configured='helsinki', warning_area='uusimaa', title='weather warning for uusimaa'
DEBUG: Search text (first 200 chars): 'uusimaa weather warning for uusimaa strong winds expected...'
DEBUG: Direct match found for 'helsinki'
DEBUG: Area match found, including: Weather warning for Uusimaa
```

## Expected Behavior After Fix

1. **With no area configured**: Shows all warnings for Finland (as before)
2. **With area configured**: Shows warnings that match the area in any text field
3. **Flexible matching**: Handles Finnish place name variations automatically
4. **Inclusive filtering**: Includes warnings without clear area info (better safe than sorry)
5. **Clear debugging**: Logs show exactly what's happening during filtering

## Files Modified

1. `custom_components/fmi_weather_warnings/coordinator.py` - Main filtering logic
2. `custom_components/fmi_weather_warnings/config_flow.py` - Improved user guidance
3. Added test files for debugging (not part of integration)

## How to Test

1. Restart Home Assistant after applying these changes
2. Enable debug logging (see above)
3. Configure the integration with a specific location
4. Check that warnings appear for that location
5. Check the logs to see the matching process in action

If you're still having issues, the debug logs will now show exactly what text is being searched and why matches are or aren't being found.