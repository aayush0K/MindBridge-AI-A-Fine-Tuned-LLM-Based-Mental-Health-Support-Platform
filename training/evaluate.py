import json
import argparse
from pathlib import Path
from tqdm import tqdm

def load_jsonl(filepath):
    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line))
    return data

def generate_human_eval_sheet(test_data, output_csv):
    """
    Generates a CSV template for human evaluation based on the Likert scale.
    """
    import pandas as pd
    
    records = []
    # Take a sample of 20 conversations for manual evaluation
    sample = test_data[:20] if len(test_data) > 20 else test_data
    
    for i, row in enumerate(sample):
        user_msg = row["messages"][0]["content"]
        expected_response = row["messages"][1]["content"]
        
        records.append({
            "Test_ID": i+1,
            "User_Message": user_msg,
            "Expected_Response": expected_response,
            "Base_Model_Response": "", # To be filled by running inference script
            "FineTuned_Response": "", # To be filled by running inference script
            "Relevance_Score_1_to_5": "",
            "Empathy_Score_1_to_5": "",
            "Helpfulness_Score_1_to_5": "",
            "Specificity_Score_1_to_5": "",
            "Context_Score_1_to_5": ""
        })
        
    df = pd.DataFrame(records)
    df.to_csv(output_csv, index=False)
    print(f"Generated Human Evaluation Template at: {output_csv}")
    print("Run inference on both models, fill the CSV, and calculate averages.")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test_file", type=str, default="./datasets/test.jsonl")
    parser.add_argument("--output_eval_sheet", type=str, default="./human_evaluation_template.csv")
    args = parser.parse_args()
    
    test_data = load_jsonl(args.test_file)
    print(f"Loaded {len(test_data)} test cases.")
    
    generate_human_eval_sheet(test_data, args.output_eval_sheet)
    
if __name__ == "__main__":
    main()
