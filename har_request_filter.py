import json
import os
from openai import OpenAI


client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)

def extract_har_data(har_file_path, webpage):
    try:
        # Load the HAR file
        with open(har_file_path, 'r', encoding='utf-8') as file:
            har_data = json.load(file)

        # Extract relevant entries
        entries = har_data.get('log', {}).get('entries', [])

        # Collect required information and remove _initiator key
        results = []
        for entry in entries:
            request = entry.get('request', {})
            response = entry.get('response', {})

            url = request.get('url', 'N/A')
            method = request.get('method', 'N/A')

            # Get headers and find Content-Type
            headers = response.get('headers', [])

            content_type = (h.get('value') for h in headers if h.get('name').lower() == 'content-type')
            content_type = next(content_type, '')

            # Extract the _resourceType field if present
            resource_type = entry.get('_resourceType', 'N/A')

            response_content = response.get('content', {})
            response_body = response_content.get('text', '')


            if is_relevant_api_endpoint(url, method, content_type, resource_type, response_body, webpage):
                print(f"Relevant API endpoint found: {url}")

                cleaned_entry = {
                    "request": request,
                    "response": response,
                }

                results.append(cleaned_entry)

        return results
    except Exception as e:
        print(f"Error reading HAR file: {e}")
        return []


def save_as_har(data, output_file_path):
    """
    Save the filtered HAR data to a new HAR file.
    
    Args:
        data: The filtered entries to be saved.
        output_file_path: The output HAR file to be created.
    """
    try:
        with open(output_file_path, 'w', encoding='utf-8') as file:
            json.dump({"log": {"entries": data}}, file, indent=4)
        print(f"Filtered HAR data saved to {output_file_path}")
    except Exception as e:
        print(f"Error saving HAR file: {e}")


def is_relevant_api_endpoint(url, method, content_type, resource_type, response_body, webpage):
    """
    Use OpenAI to determine if the given URL, method, and content type is a relevant API endpoint.
    Exclude `.js` and image files based on URL or Content-Type.
    """
    # Exclude .js, picture files, and font files from relevancy
    excluded_extensions = ['.js', '.css', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.woff', '.woff2', '.ttf', '.ico']
    if any(url.endswith(ext) for ext in excluded_extensions):
        return False

    # Exclude irrelevant content types
    excluded_content_types = [
        'application/javascript',
        'font/woff',
        'font/woff2',
        'application/x-font-ttf',
        'image/',
        'text/css'
    ]
    if any(content_type.startswith(excluded) for excluded in excluded_content_types):
        return False

    # Exclude entries with empty or missing response bodies
    if not response_body or response_body.strip() == '':
        return False

    print(f"Checking URL: {url} with Content-Type: {content_type} with resource type: {resource_type}")

    prompt = f"""
    Given the following information:
    - URL: {url}
    - HTTP Method: {method}
    - Content Type: {content_type}
    Decide if this is a relevant API endpoint for webpage {webpage}.
     Focus on back end resources. Answer with only 'yes' or 'no' don't put anything else. 
    """
    try:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        
        decision = completion.choices[0].message.content

        return decision.lower() == 'yes'
    except Exception as e:
        print(f"Error querying OpenAI API: {e}")
        return False


# Example usage
webpage = "www.rohlik.cz"
har_file = "rohlik.har"  # Replace with your HAR file path

data = extract_har_data(har_file, webpage)



output_har_file = "filtered_rohlik.har"  # Specify the output HAR file path
save_as_har(data, output_har_file)