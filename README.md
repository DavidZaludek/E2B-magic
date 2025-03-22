# E2B-magic
Sometimes a dream is all you need, sometimes it's just magic.


# Goal
Automate web information retrieval using human interaction as starting point. This project focuses on MVP :
Scrape potatoe prices from online retailers.
User uses webbrowser to navigate to potatoe prices. Everything is logged to HAR. LLM uses this to build scraper. Output is python script to get potatoe prices.

1. User starts a fresh (incognito) web session in browser and starts recording netork communication.
2. user navigates to potatoe pricing page in as little steps as possible.
3. As soon as potato pricing is dosplayed, HAR recording stops
4. Python script trimHAR.py starts -> removes fonts, images, js and everything not needed for scraping
5. OpenAI loop starts : it has trimmed har in context. New messages will have previous messages including requests and responses. The bot will try to create python scraper in loop. The python scraper runs in e2b :
```
 if parsed["code"]:
        print("🚀 Running code in sandbox...")
        exec_result = sbx.run_code(parsed["code"])
        logs = exec_result.logs
        print("📄 Logs from sandbox:\n", logs)
```
The bot response must always be in JSON format: { "response": "What you're doing", action:"code/done/kill" "code": "Python code or null" } .
Action is always code or stop. If it will be code, code will be executed in sbx. If it is kill or done, the loop stops, kill/done shows success/fail with the whole task.
6. User gets the final python code if action was done and executes it, this will print potato prices in python table

# Usage

pip install -r requirements.txt
python har_request_filter.py tesco.com .\www.tesco.com.har
python scraperGenerator.py .\filtered_www.tesco.com.har
