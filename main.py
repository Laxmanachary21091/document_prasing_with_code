import os
import re
import json
import openai
from pathlib import Path
from openai import OpenAI
from PyPDF2 import PdfReader
from google.colab import userdata
from unstructured.partition.pdf import partition_pdf
from tenacity import retry, wait_random_exponential, stop_after_attempt


OPENAI_API_KEY = userdata.get('OPEN_AI_KEY')
model_ID = userdata.get('GPT_MODEL')
os.environ ["OPENAI_API_KEY"] = OPENAI_API_KEY
client = OpenAI (api_key = OPENAI_API_KEY)



def extract_text_from_pdf(pdf_path: str):
"""
   extract text content from a PDF file using the unstructured library.
"""
      elements = partition_pdf(pdf_path, strategy="hi_res")
      return "\n".join([str(element) for element in elements])


def read_prompt(prompt_path: str):
    Read the prompt for research paper parsing from a text file.
    with open(prompt_path, "r") as f:
    return f.read()



@retry (wait=wait_random_exponential(min=1, max=120), stop=stop_after_attempt(10)
def completion_with_backoff(**kwargs):
     return client.chat.completions.create(**kwargs)



def extract_metadata(content: str, prompt_path: str, model_id: str):
"""Use GPT model to extract metadata from the research paper content based on t"""
    prompt_data = read_prompt(prompt_path)
    try:
        response = completion_with_backoff(
        model=model_id,
        messages=[
        1,
        {"role": "system", "content": prompt_data},
        {"role": "user", "content": content}
        temperature=0.2,)
    response_content = response.choices [0].message.content 
    except Exception as e:
         print(f"Error calling OpenAI API: {e}")
    return {}

def process_research_paper (pdf_path: str, prompt: str,output_folder: str, model_id: str):
"""Process a single research paper through the entire pipeline."""
  print(f"Processing research paper: {pdf_path}")
  try:

     content = extract_text_from_pdf(pdf_path)

     metadata = extract_metadata(content, prompt, model_id)

    output_filename = Path (pdf_path).stem + ".json"
               
    output_path = os.path.join (output_folder, output_filename)
    with open(output_path, 'w') as f:
          json.dump(metadata, f, indent=2)
    print(f"Saved metadata to {output_path}")
 except Exception as:

 print(f"Error processing (pdf_path}: {e}")



pdf_path = "./data/1706.03762v7.pdf"
prompt_path = "./data/prompts/scientific_papers_prompt.txt"
output_folder = "./data/extracted_metadata"
process_research_paper (pdf_path, prompt_path, output_folder, model_ID)


