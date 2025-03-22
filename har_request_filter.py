import json
import os
from openai import OpenAI
import sys

client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)

import openai

openai.api_key = "your_openai_api_key"  # Replace with your actual OpenAI API key


def is_relevant_api_request(cleaned_entry, webpage):
    """
    Determine whether a given cleaned_entry represents a valid API request
    using OpenAI's API for intelligent classification.
    """
    request_data = cleaned_entry.get("request", {})
    response_data = cleaned_entry.get("response", {})

    # Prepare the input for OpenAI API
    system_prompt = ("You are an AI assistant specializes in reverse engineering you are best at classifying API requests and responses."
                     "You are given a request and response and you need to determine if it is a valid API request for the given webpage. "
                     "You don't want to miss anything important it's better to have extras if you have to. "
                     "Consider frameworks that are used in web development to access apis like graphql and rest.")
    prompt = f"""
Given the following details:

**Request Details**
Method: {request_data.get('method')}
URL: {request_data.get('url')}
Headers: {request_data.get('headers')}
Body: {request_data.get('postData', {}).get('text', 'N/A')}

**Response Details**
Status Code: {response_data.get('status', 'N/A')}
Headers: {response_data.get('headers')}
Body: {response_data.get('content', {}).get('text', 'N/A')}

Question:
Does this represent a valid API request and response for {webpage}?   Answer with only 'yes' or 'no' don't put anything else.
    """

    try:
        # Make a call to OpenAI API
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"system", "content": system_prompt},{"role": "user", "content": prompt}]
        )

        decision = completion.choices[0].message.content


        return decision.lower() == "yes"

    except Exception as e:
        print(f"Error classifying request using OpenAI API: {e}")
        return False, str(e)


def extract_har_data(har_file_path, webpage):
    try:
        # Load the HAR file
        with open(har_file_path, 'r', encoding='utf-8') as file:
            har_data = json.load(file)

        # Extract relevant entries
        entries = har_data.get('log', {}).get('entries', [])

        main_endpoints = select_main_api_endpoint(entries)

        print(main_endpoints)

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

            if is_relevant_api_endpoint(url, method, content_type, resource_type, response_body, main_endpoints):
                cleaned_entry = {
                    "request": request,
                    "response": response,
                }

                if (is_relevant_api_request(cleaned_entry, webpage)):
                    print(f"Relevant API request found: {cleaned_entry}")
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

def select_main_api_endpoint(entries):
    entries_deconstructed = [deconstruct_entry(x) for x in entries]


    prompt = f"""
    Given these urls and methods select relevantr urls for acessing API data on webpage {webpage} focus on back end resources.
    Answer should be list of urls represented as host with out path. Try to filter out analytics and urls that don't belong to the website but are known 3rd party tools.
    {[(x[0],x[1],x[2]) for x in entries_deconstructed] }
    """
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        decision = completion.choices[0].message.content
        return decision
    except Exception as e:
        return 'no main url selected.'

def deconstruct_entry(entry):
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

    return url, method, content_type, resource_type, response_body, webpage


def is_relevant_api_endpoint(url, method, content_type, resource_type, response_body, selected_backend_urls):
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
    {selected_backend_urls}
     Focus on back end resources. Answer with only 'yes' or 'no' don't put anything else. 
    """
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        decision = completion.choices[0].message.content

        return decision.lower() == 'yes'
    except Exception as e:
        print(f"Error querying OpenAI API: {e}")
        return False



# Example usage
webpage = sys.argv[1]
har_file = sys.argv[2]

data = extract_har_data(har_file, webpage)

output_har_file =  f"filtered_{har_file}" # Specify the output HAR file path
save_as_har(data, output_har_file)