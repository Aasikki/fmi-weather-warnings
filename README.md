# FMI Weather Warnings for Home Assistant

A Home Assistant custom integration that displays weather warning data from the Finnish Meteorological Institute (FMI) using their Common Alerting Protocol (CAP) RSS feed.

## Features

- 🌦️ Real-time weather warnings from FMI
- 📍 Optional location-based filtering
- 🔄 Automatic updates every 5 minutes
- 📊 Detailed warning information including severity, urgency, and instructions
- 🏠 Native Home Assistant integration with config flow

## Installation

### HACS (Recommended)

1. Open HACS in your Home Assistant instance
2. Click on "Integrations"
3. Click the three dots in the top right corner and select "Custom repositories"
4. Add this repository URL: `https://github.com/Aasikki/fmi-weather-warnings`
5. Select "Integration" as the category
6. Click "Add"
7. Find "FMI Weather Warnings" in HACS and click "Download"
8. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/fmi_weather_warnings` directory to your Home Assistant's `custom_components` directory
2. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for **FMI Weather Warnings**
4. (Optional) Enter a location name to filter warnings (e.g., "Helsinki", "Lapland", "Uusimaa")
   - Leave empty to receive all warnings for Finland
5. Click **Submit**

## Usage

After configuration, the integration creates a sensor entity:

- **sensor.fmi_weather_warnings_active_warnings** - Number of active warnings

The sensor provides the following information in its attributes:

- **warnings**: List of active warnings, each containing:
  - `title`: Warning title
  - `headline`: CAP headline
  - `description`: Detailed description
  - `severity`: Warning severity (Minor, Moderate, Severe, Extreme)
  - `urgency`: Warning urgency (Immediate, Expected, Future, Past)
  - `certainty`: Warning certainty (Observed, Likely, Possible, Unlikely)
  - `event`: Type of weather event
  - `area`: Affected geographical area
  - `effective`: Warning start time
  - `expires`: Warning expiration time
  - `instruction`: Safety instructions
  - `sender`: Warning issuer
  - `link`: Link to detailed information

### Example Automation

```yaml
automation:
  - alias: "Notify on Severe Weather Warning"
    trigger:
      - platform: numeric_state
        entity_id: sensor.fmi_weather_warnings_active_warnings
        above: 0
    condition:
      - condition: template
        value_template: >
          {% set warnings = state_attr('sensor.fmi_weather_warnings_active_warnings', 'warnings') %}
          {{ warnings | selectattr('severity', 'in', ['Severe', 'Extreme']) | list | count > 0 }}
    action:
      - service: notify.mobile_app
        data:
          title: "⚠️ Severe Weather Warning"
          message: >
            {% set warnings = state_attr('sensor.fmi_weather_warnings_active_warnings', 'warnings') %}
            {% set severe = warnings | selectattr('severity', 'in', ['Severe', 'Extreme']) | list %}
            {{ severe[0].headline }}
```

### Example Lovelace Card

```yaml
type: markdown
content: >
  {% set warnings = state_attr('sensor.fmi_weather_warnings_active_warnings', 'warnings') %}
  {% if warnings | length > 0 %}
    ## ⚠️ Active Weather Warnings ({{ warnings | length }})
    {% for warning in warnings %}
      ### {{ warning.headline if warning.headline else warning.title }}
      **Severity:** {{ warning.severity | default('Unknown') }}  
      **Area:** {{ warning.area | default('Not specified') }}  
      **Valid:** {{ warning.effective | default('') }} - {{ warning.expires | default('') }}
      
      {{ warning.description | default(warning.summary) }}
      
      {% if warning.instruction %}
      **Instructions:** {{ warning.instruction }}
      {% endif %}
      ---
    {% endfor %}
  {% else %}
    ✅ No active weather warnings
  {% endif %}
```

## Data Source

This integration uses the FMI CAP RSS feed:
- **URL**: https://alerts.fmi.fi/cap/feed/rss_en-GB.rss
- **Protocol**: Common Alerting Protocol (CAP)
- **Language**: English (en-GB)

## Support

For issues, feature requests, or questions:
- [GitHub Issues](https://github.com/Aasikki/fmi-weather-warnings/issues)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Credits

Weather warning data provided by the Finnish Meteorological Institute (Ilmatieteen laitos)
