import os
from dotenv import load_dotenv
import pandas as pd
from rapidfuzz.fuzz import partial_ratio, ratio
from openai import OpenAI
import json


def detect_columns(df):
    print(df.columns)
    headers = list(df.columns)

    prompt = f"""
    You are a smart assistant helping to understand the schema of an Excel sheet. You will be given a list of column headers. Your task is to identify important columns and return a JSON object mapping standard field names to the actual column names from the sheet.

    Please:
    - Map the following fields based on column header names:
        - Style ID → may appear as "style id", "id", "sid", "STYLE ID", etc.
        - Style Description → may appear as "style", "style descr", "style description", etc.
        - Color → may appear as "color", "clr", "shade", etc.
        - Date Columns → these are columns where the header looks like a date (e.g. "2024/12/04", "june 4", "12-06", "2024-june-05" etc.). Normalize all dates to format: yyyy-mm-dd and use them directly as keys in the JSON.

    🧠 Example 1:

    Input:
    ["STYLE", "ID", "CLR", "2024/12/05", "2024-june-04", "June 06"]

    Output:
    {{
    "style_id": "ID",
    "style_description": "STYLE",
    "color": "CLR",
    "2024-12-05": "2024/12/05",
    "2024-06-04": "2024-june-04",
    "2024-06-06": "June 06"
    }}

    🧠 Example 2:

    Input:
    ["sid", "style descr", "shade", "12-06", "2024-02-24"]

    Output:
    {{
    "style_id": "sid",
    "style_description": "style descr",
    "color": "shade",
    "2024-12-06": "dec-06",
    "2024-02-24": "2024-feb-24"
    }}

    Now apply the same logic for the following column headers:

    {headers}

    Respond ONLY with the JSON object. Do not explain or include any other text.
    """

    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You're a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.0,
    )
    response_text = completion.choices[0].message.content.strip()
    if response_text.startswith("```"):
        response_text = response_text.strip("```json").strip("```").strip()
    try:
        parsed_json = json.loads(response_text)
        return parsed_json
    except json.JSONDecodeError:
        return "Failed to parse JSON. Raw output:"
    


def get_confidence(mapped_json: dict) -> pd.DataFrame:
    records = []

    for normalized_key, original_col in mapped_json.items():
        # Normalize for better comparison
        norm_key_clean = normalized_key.lower().replace("_", "").strip()
        orig_col_clean = original_col.lower().replace("_", "").strip()

        # Calculate similarity score
        score = max(
            partial_ratio(norm_key_clean, orig_col_clean),
            ratio(norm_key_clean, orig_col_clean)
        ) / 100.0  # Convert to range [0, 1]

        records.append({
            "key": normalized_key,
            "value": original_col,
            "score": round(score, 3)
        })

    return pd.DataFrame(records)

def ai_column_formatter(df, header_row=None, num_rows=None):
    # Handle optional header_row
    if header_row is not None and str(header_row).strip() != "":
        header_row = int(header_row)

        if header_row >= len(df):
            raise IndexError("Header row index is out of range.")
        
        headers = df.iloc[header_row].astype(str).tolist()
        df = df.iloc[header_row + 1:].copy()
        df.columns = headers
        df.reset_index(drop=True, inplace=True)

    # Handle optional num_rows
    if num_rows is not None and str(num_rows).strip() != "":
        num_rows = int(num_rows)
        df = df.head(num_rows)

    # Ensure all data is string before detection
    df = df.astype(str)
    
    # Call your column detection logic
    column_mapping = detect_columns(df)
    df_scores = get_confidence(column_mapping)

    return df_scores, column_mapping, df

def process_dataframe(parsed_json,df):
    original_columns = list(parsed_json.values())
    
    df_subset = df[original_columns].copy()
    rename_mapping = {v: k for k, v in parsed_json.items()}
    df_renamed = df_subset.rename(columns=rename_mapping)
    return df_renamed
