import json
import os

# Input HAR file
input_filename = 'www.kosik.cz.har'

# Load HAR file
with open(input_filename, 'r', encoding='utf-8') as f:
    har_data = json.load(f)

# Access entries
entries = har_data.get('log', {}).get('entries', [])

# Filter and clean entries
filtered_entries = []
for entry in entries:
    url = entry.get('request', {}).get('url', '')
    if url.startswith('https://www.kosik.cz/api/front/page/products/flexible'):
        # Remove _initiator if present
        entry.pop('_initiator', None)
        filtered_entries.append(entry)

# Create filtered HAR structure
filtered_har = {
    "log": {
        **har_data.get('log', {}),
        "entries": filtered_entries
    }
}

# Output filename
base, ext = os.path.splitext(input_filename)
output_filename = f"{base}_filtered{ext}"

# Write to filtered HAR file
with open(output_filename, 'w', encoding='utf-8') as f:
    json.dump(filtered_har, f, ensure_ascii=False, indent=2)

print(f"Filtered HAR saved to: {output_filename}")
