# FMI Weather Warnings Integration

## Overview

This integration provides real-time weather warnings from the Finnish Meteorological Institute (Ilmatieteen laitos) for Home Assistant users.

## Installation Methods

### Via HACS (Home Assistant Community Store)

1. Ensure HACS is installed in your Home Assistant instance
2. Add this repository as a custom repository in HACS
3. Search for "FMI Weather Warnings" and install
4. Restart Home Assistant
5. Add the integration via the Home Assistant UI

### Manual Installation

1. Download or clone this repository
2. Copy the `custom_components/fmi_weather_warnings` folder to your Home Assistant's `custom_components` directory
3. Restart Home Assistant
4. Add the integration via the Home Assistant UI (Settings → Devices & Services → Add Integration)

## Features

- **Real-time Updates**: Automatically fetches weather warnings every 5 minutes
- **Location Filtering**: Optional filtering by geographical area (e.g., "Helsinki", "Lapland")
- **Detailed Information**: Access to severity, urgency, certainty, effective time, expiration, and instructions
- **CAP Compliant**: Parses Common Alerting Protocol (CAP) format data
- **Home Assistant Native**: Uses config flow for easy setup and configuration

## Data Source

The integration uses the official FMI CAP RSS feed:
- URL: https://alerts.fmi.fi/cap/feed/rss_en-GB.rss
- Format: RSS with CAP (Common Alerting Protocol) extensions
- Language: English (en-GB)
- Update Frequency: Every 5 minutes

## Sensor Entity

The integration creates one sensor entity per configuration:

**Entity ID**: `sensor.fmi_weather_warnings_active_warnings`

**State**: Number of active weather warnings (integer)

**Attributes**:
- `warnings`: List of all active warnings with detailed information

## Warning Attributes

Each warning in the `warnings` attribute contains:

- **title**: Warning title/summary
- **headline**: CAP headline
- **description**: Detailed warning description
- **severity**: Warning severity level
  - Minor
  - Moderate
  - Severe
  - Extreme
- **urgency**: Time frame for response
  - Immediate
  - Expected
  - Future
  - Past
- **certainty**: Likelihood of the event
  - Observed
  - Likely
  - Possible
  - Unlikely
- **event**: Type of weather event (e.g., "Wind", "Heavy Rain", "Snow")
- **area**: Affected geographical area
- **effective**: Warning start time (ISO 8601 format)
- **expires**: Warning end time (ISO 8601 format)
- **instruction**: Safety instructions and recommendations
- **sender**: Warning issuer (FMI)
- **link**: URL to detailed warning information

## Example Use Cases

### Automation: Mobile Notification

Get notified when severe weather warnings are issued:

```yaml
automation:
  - alias: "Severe Weather Alert"
    trigger:
      - platform: state
        entity_id: sensor.fmi_weather_warnings_active_warnings
    condition:
      - condition: template
        value_template: >
          {% set warnings = state_attr('sensor.fmi_weather_warnings_active_warnings', 'warnings') %}
          {{ warnings | selectattr('severity', 'in', ['Severe', 'Extreme']) | list | count > 0 }}
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "⚠️ Severe Weather Warning"
          message: >
            {% set warnings = state_attr('sensor.fmi_weather_warnings_active_warnings', 'warnings') %}
            {% set severe = warnings | selectattr('severity', 'in', ['Severe', 'Extreme']) | first %}
            {{ severe.headline }}
```

### Dashboard Card: Warning Display

Show active warnings on your dashboard:

```yaml
type: markdown
content: >
  {% set count = states('sensor.fmi_weather_warnings_active_warnings') | int %}
  {% set warnings = state_attr('sensor.fmi_weather_warnings_active_warnings', 'warnings') %}
  
  {% if count > 0 %}
    ## ⚠️ Weather Warnings ({{ count }})
    
    {% for warning in warnings %}
      ### {{ warning.headline | default(warning.title) }}
      
      **Severity**: {{ warning.severity | default('Unknown') }}  
      **Area**: {{ warning.area | default('Not specified') }}  
      **Valid**: {{ warning.effective | default('N/A') }} to {{ warning.expires | default('N/A') }}
      
      {{ warning.description | default(warning.summary) }}
      
      {% if warning.instruction %}
      **⚠️ Instructions**: {{ warning.instruction }}
      {% endif %}
      
      ---
    {% endfor %}
  {% else %}
    ✅ **No Active Weather Warnings**
    
    All clear! No weather warnings are currently in effect.
  {% endif %}
```

### Conditional Card: Show Only When Active

Display a card only when warnings are active:

```yaml
type: conditional
conditions:
  - entity: sensor.fmi_weather_warnings_active_warnings
    state_not: "0"
card:
  type: entities
  title: ⚠️ Active Weather Warnings
  entities:
    - entity: sensor.fmi_weather_warnings_active_warnings
      name: Number of Warnings
```

## Troubleshooting

### No Warnings Showing

1. Check that the FMI RSS feed is accessible
2. Verify your Home Assistant can reach external URLs
3. Check the Home Assistant logs for errors related to `fmi_weather_warnings`
4. If using location filtering, ensure the location name matches the area names in FMI warnings

### Integration Not Loading

1. Verify the `custom_components/fmi_weather_warnings` directory exists
2. Check that all required files are present
3. Restart Home Assistant completely
4. Check the Home Assistant logs for startup errors

### Updates Not Appearing

1. The integration updates every 5 minutes by default
2. Check your internet connection
3. Verify the FMI service is operational
4. Check logs for update errors

## Technical Details

### Dependencies

- `feedparser==6.0.11`: For parsing RSS feeds with CAP extensions

### Update Interval

- Default: 300 seconds (5 minutes)
- Configurable through coordinator initialization

### API Endpoint

- Primary: https://alerts.fmi.fi/cap/feed/rss_en-GB.rss
- Protocol: HTTPS
- Format: RSS 2.0 with CAP 1.2 extensions

## Support

- **Issues**: [GitHub Issues](https://github.com/Aasikki/fmi-weather-warnings/issues)
- **Documentation**: [README.md](README.md)

## License

MIT License - See [LICENSE](LICENSE) file for details

## Credits

- Weather data: Finnish Meteorological Institute (Ilmatieteen laitos)
- Integration: Community contribution
