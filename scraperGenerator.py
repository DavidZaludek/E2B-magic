import os
import sys
import json
import tiktoken
import time
import re
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Literal, Optional
from e2b_code_interpreter import Sandbox

# Toggle between OpenAI and Gemini
useGemini = True

# Load environment variables
load_dotenv()

class BotReply(BaseModel):
    response: str
    action: Literal["code", "done", "kill"]
    code: Optional[str]

# Initialize the appropriate client based on useGemini flag
if useGemini:
    from google import genai
    gemini_client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
else:
    from openai import OpenAI
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Load HAR file
har_path = sys.argv[1]
shopName = sys.argv[2]
print("Scraping ", shopName)
with open(har_path, "r") as f:
    trimmed_har = f.read()

print("Initing Sandbox...")
sbx = Sandbox(timeout=600)
print("Sandbox ready.")

system_prompt = (
    "You are an autonomous agent tasked with building a Python scraper based on a trimmed HAR file. "
    "This HAR data is provided only as a reference to understand how the website loads potato pricing data -- "
    "including useful endpoints, headers, query parameters, and request/response structure.\n\n"
    "The HAR data contains the actual potato prices, its a good idea to first find the potato prices from the HAR data. That should be your starting point.\n\n"
    
    "Your scraper must NOT extract data from the HAR file itself. Instead, it must fetch live data directly from the actual website "
    "using the same URLs, headers, or request structure found in the HAR.\n\n"
    
    "You operate in a loop. Each of your responses will be parsed as JSON and your code will be executed in a real Python sandbox. "
    "Execution logs will be shown to you after each iteration to guide your improvements.\n\n"

    "🎯 Goal:\n"
    "- Build a working Python script that fetches potato prices from the live website.\n"
    "- Use HAR only to reverse-engineer how the data is retrieved (e.g., look at request URLs, headers, parameters).\n"
    "- When the script is working and printing the potato prices correctly, respond with `action: done`.\n\n"

    "🛑 Rules:\n"
    "- Always respond in valid JSON format.\n"
    "- Required keys: `response` (summary), `action` (code/done/kill), and `code` (Python or null).\n"
    "- Use `action: code` while iterating and testing improvements.\n"
    "- Use `action: kill` if the HAR is unusable or scraping is impossible.\n"
    "- Use `action: done` only when you're confident the scraper works and extracts live potato prices.\n"
    "- Never use print(), always use printTrunc instead : "
    "def printTrunc(*args, sep=' ', end='\\n', file=None, flush=False):"
    "    output = sep.join(str(arg) for arg in args) + end"
    "    lines = output.splitlines()"
    "    quoted_lines = [f'\"{line}\"' for line in lines]"
    "    final_output = '\\n'.join(quoted_lines)"
    ""
    "    if len(final_output) > 5000:"
    "        final_output = final_output[:5000] + '... [truncated]'"
    ""
    "    print(final_output, end='', file=file, flush=flush)"
    "\n\n"
    "- Use pandas for nice final output. \n"

    "✅ Format example:\n"
    '{ \"response\": \"What you are doing\", \"action\": \"code/done/kill\", \"code\": \"...Python code...\" }'
)

history = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": f"Here's the HAR data:\n{trimmed_har}"}
]

lastCode = ""

def printTrunc(*args, sep=' ', end='\n', file=None, flush=False):
    maxtruncate = 600
    output = sep.join(str(arg) for arg in args) + end
    if len(output) > maxtruncate:
        output = output[:maxtruncate] + '... [truncated]'
    print(output, end='', file=file, flush=flush)

MAX_INPUT_TOKENS = 300_000  # safe buffer under 128k

def count_tokens(messages, model="gpt-3.5-turbo"):
    if useGemini:
        # Approximate token count for Gemini - chars/4 is a rough approximation
        total_tokens = 0
        for msg in messages:
            for _, value in msg.items():
                total_tokens += len(value) // 4
        return total_tokens
    else:
        # Use tiktoken for OpenAI models
        enc = tiktoken.encoding_for_model(model)
        total_tokens = 0
        for msg in messages:
            total_tokens += 4  # every message has a role + structure
            for key, value in msg.items():
                total_tokens += len(enc.encode(value))
        total_tokens += 2  # for priming/assistant start
        return total_tokens

def get_llm_response_structured(conversation, max_retries=3, wait_time=15):
    print("Counting token...")
    input_tokens = count_tokens(conversation, "gpt-4o" if not useGemini else None)

    print(f"🤖 : Sending LLM query with {input_tokens} tokens ... ")
    if input_tokens > MAX_INPUT_TOKENS:
        raise ValueError(f"❌ Input exceeds token limit ({input_tokens} > {MAX_INPUT_TOKENS})")

    if useGemini:
        all_messages = []
        for msg in conversation:
            if msg["role"] == "system":
                all_messages.append(msg["content"])
            elif msg["role"] == "user":
                all_messages.append(f"User: {msg['content']}")
            elif msg["role"] == "assistant":
                all_messages.append(f"Assistant: {msg['content']}")

        prompt = "\n\n".join(all_messages)
        prompt += "\n\nRespond only with valid JSON in this format: {\"response\": \"explanation\", \"action\": \"code/done/kill\", \"code\": \"Python code or null\"}"

        for attempt in range(max_retries):
            try:
                response = gemini_client.models.generate_content(
                    model='gemini-2.0-flash',
                    contents=prompt,
                )
                response_text = response.text
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    response_json = json.loads(json_match.group(0))
                    return BotReply(**response_json)
                else:
                    print("⚠️ No valid JSON found in response.")
                    return None
            except Exception as e:
                if "RESOURCE_EXHAUSTED" in str(e):
                    print(f"⚠️ Gemini quota exhausted. Waiting {wait_time}s and retrying... ({attempt+1}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    print(f"❌ Gemini error: {e} Waiting {wait_time}s and retrying... ({attempt+1}/{max_retries})")
                    time.sleep(wait_time)

        print("❌ Max retries reached. Gemini still exhausted.")
        return None

    else:
        completion = client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=conversation,
            response_format=BotReply
        )
        return completion.choices[0].message.parsed

# Main loop
while True:
    
    parsed = get_llm_response_structured(history)
    if not parsed:
            print("❌ Failed to get a valid response.")
            break
    
    print(f"🤖 LLM Response:\n{parsed.action}")
    print(parsed.response)
    printTrunc(parsed.code)

    if parsed.code:
        lastCode = parsed.code

    if parsed.action == "code":
        if parsed.code:
            print("🚀 Running code in sandbox...")
            try:
                exec_result = sbx.run_code(parsed.code)
                logs = exec_result.logs

                printTrunc("Exec result:\n", exec_result)
                printTrunc("📄 Logs from sandbox:\n", logs)
                print("❌ Errors:", exec_result.error)

                # Append to conversation for next round
                response_content = parsed.model_dump_json() if not useGemini else json.dumps({
                    "response": parsed.response,
                    "action": parsed.action,
                    "code": parsed.code
                })
                
                history.append({
                    "role": "assistant" if not useGemini else "model",
                    "content": response_content
                })
                history.append({
                    "role": "user",
                    "content": f"Logs from code:\n{logs}  Errors: {exec_result.error}"
                })
            except Exception as e:
                print(f"❌ Error running code: {e}")
                break
        else:
            print("⚠️ Code action selected but no code provided.")
            break
    elif parsed.action in ("done", "kill"):
        if(parsed.action == "done"):
            print("✅✅✅✅ DONE ✅✅✅✅")
        if parsed.response:
            print("🥔 Scraped potato prices:")
            print(parsed.response)

        scraperPath = f"scraper_{shopName}.py"
        with open(scraperPath, "w") as f:
            f.write(lastCode)
            print(f"✅ Final scraper written to {scraperPath}")
        break
    else:
        print(f"❓ Unknown action: {parsed.action}")
        break