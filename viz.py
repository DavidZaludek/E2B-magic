from dotenv import load_dotenv
from e2b_code_interpreter import Sandbox
import base64
import os
from openai import OpenAI
import base64
import sys



def gen_histplot_code(str_dump, commodity, client, plot_type):
  
  sys_prompt = """
    You are a code-writing assistant that returns data visualization charts.
    When you write Python code that produces a chart, convert the chart into a base64-encoded PNG and print it like this:

    "<base64-encoded image here>"

    Use matplotlib for plotting. Use io.BytesIO to capture the image.
  """


  prompt = f"""
      Given the following string of commodity prices:
      - STR: {str_dump}
      - COMMODITY: {commodity}
      - PLOT_TYPE: {plot_type}

      assume commodity in any language 
      generate PLOT_TYPE plot of values, code should be runnable with no additional comments

   """
  final_prompt = sys_prompt + prompt
  try:
      completion = client.chat.completions.create(
          model="gpt-4o",
          messages=[{"role": "user", "content": final_prompt}]
      )
      
      to_numpy_code = completion.choices[0].message.content

      return to_numpy_code

  except Exception as e:
      print(f"Error querying OpenAI API: {e}")



if __name__ == "__main__":
  if len(sys.argv) != 4:
    print("Usage: python viz.py scraper_rohlik.cz.py potato histogram")
    sys.exit(1)

  if not os.path.exists('viz'):
    os.makedirs('viz')

  filepath = sys.argv[1]
  commodity = sys.argv[2]
  plot_type = sys.argv[3]

  load_dotenv(dotenv_path='.env', override=True)

  E2B_API_KEY=os.getenv("E2B_API_KEY")
  OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")

  client = OpenAI()

  with open(filepath, 'r') as file:
    code_dump = file.read()

  print(f"Executing: \n {code_dump}")

  with Sandbox(api_key=E2B_API_KEY) as sbx:
    exec = sbx.run_code(code_dump)

    text_dump = exec.logs.stdout[0]

    histplot_code = gen_histplot_code(text_dump, commodity = "potato", client = client, plot_type=plot_type)
    histplot_code = histplot_code.replace("```", "")
    histplot_code = histplot_code.replace("python", "")

    print(f"running viz code: \n {histplot_code}")
    with open("viz/histplot_code.py", "w") as file:
      file.write(histplot_code)

    exec_plot = sbx.run_code(histplot_code)

    hist = exec_plot.logs.stdout[0]
    image_bytes = base64.b64decode(hist)

    print("writing output viz_out.png")

    with open("viz/viz_out.png", "wb") as image_file:
      image_file.write(image_bytes)

