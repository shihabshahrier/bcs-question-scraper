# BCS Question Scraper

A Python script to scrape BCS (Bangladesh Civil Service) preliminary exam questions from 10minuteschool.com. The script downloads questions from BCS 10th to 43rd and saves them in a structured CSV format.

## Features

- Downloads question pages for BCS exams (10th to 43rd)
- Handles different URL slug patterns
- Parses questions, options, correct answers, and explanations
- Saves data in CSV format with structured columns
- Includes retry logic for different URL patterns
- Respects rate limiting with delays between requests

## Requirements

```
requests
beautifulsoup4
pandas
```

Install dependencies using:

```sh
pip install -r requirements.txt
```

## Usage

1. Run the script:
```sh
python main.py
```

2. The script will:
   - Create a `downloaded_html` directory for cached HTML files
   - Download question pages for each BCS exam
   - Parse the content and extract structured data
   - Save results to `bcs_10_to_43.csv`

## Output Format

The generated CSV file contains the following columns:
- bcs_number: The BCS exam number
- question: The question text
- option_a: First option
- option_b: Second option
- option_c: Third option
- option_d: Fourth option
- correct_option: The correct answer (A, B, C, or D)
- explanation: Explanation for the correct answer

## Notes

- The script uses a delay between requests to avoid overwhelming the server
- Already downloaded files are skipped to avoid unnecessary requests
- Multiple URL patterns are tried for each exam year