import pandas as pd
from pathlib import Path
import re

# Number of markdown files to keep and combine
nb_markdown_kept = 248
# Gemini:
# nb: gemini tokens
# 248: 666296

# folders
inputs_folders = Path("./inputs")
outputs_folders = Path("./outputs")
documentation_folders = Path("./nersc.gitlab.io")
markdowns_folders = documentation_folders / 'docs'

# input files
page_usage_csv_path = inputs_folders / 'Pages_and_screens_Page_title_and_screen_class.csv'
page_file_maps_path = documentation_folders / 'mkdocs.yml'

#------------------------------------------------------------------------------
# Load data

# Load the CSV file
df = pd.read_csv(page_usage_csv_path, header=9)

# Load the nav section from mkdocs.yml without using the yaml parser
with open(page_file_maps_path, 'r') as file:
    content = file.read()
    
# Extract just the nav section using a regex approach
nav_section_match = re.search(r'nav:(.*?)(?=\n[a-zA-Z#])', content, re.DOTALL)
nav_section = nav_section_match.group(1) if nav_section_match else ""

#------------------------------------------------------------------------------
# Process the navigation structure manually to create mapping

page_mappings = {}

# Function to extract page titles and their corresponding markdown files
def extract_mappings_from_nav(nav_text):
    # Pattern to match lines with markdown files
    pattern = r'^\s*-\s*(.*?):\s*(.*?\.md)$'
    
    # Find all matches
    for line in nav_text.split('\n'):
        match = re.match(pattern, line)
        if match:
            title = match.group(1).strip()
            path = match.group(2).strip()
            page_mappings[title] = path

# Extract mappings
extract_mappings_from_nav(nav_section)

# Function to match page titles from analytics with mkdocs titles
def match_page_title(analytics_title):
    """Find the best match for an analytics page title in the mkdocs structure"""
    # Clean the analytics title - often includes "NERSC Documentation" or other prefix/suffix
    cleaned_title = re.sub(r'NERSC Documentation.*$', '', analytics_title).strip()
    cleaned_title = cleaned_title.split(' | ')[0].strip()
    
    # Try direct match
    if cleaned_title in page_mappings:
        return page_mappings[cleaned_title]
    
    # Try fuzzy matching - find the closest match
    best_match = None
    best_score = 0
    
    for mkdocs_title in page_mappings.keys():
        # Simple word overlap score
        words_analytics = set(cleaned_title.lower().split())
        words_mkdocs = set(mkdocs_title.lower().split())
        overlap = len(words_analytics.intersection(words_mkdocs))
        
        if overlap > best_score and overlap > 0:
            best_score = overlap
            best_match = mkdocs_title
    
    return page_mappings.get(best_match, "Not found") if best_match else "Not found"

# Add file paths to the dataframe
df['File Path'] = df['Page title and screen class'].apply(match_page_title)

# Create a clean final dataframe with only the needed columns
final_df = df[['Page title and screen class', 'File Path', 'Views']]

# Filter out rows without a known path
final_df = final_df[final_df['File Path'] != "Not found"]

# Filter out pages with 0 views
final_df = final_df[final_df['Views'] > 0]

# Sort by number of views in descending order
final_df = final_df.sort_values(by='Views', ascending=False)

# Display the final dataframe
print("\nFinal Sorted Table of Pages with Known Paths and Views > 0:")
print(final_df)

# Create output folder if it doesn't exist
outputs_folders.mkdir(exist_ok=True)

# Save the results to a CSV file
final_df.to_csv(outputs_folders / 'pages_by_views.csv', index=False)

#------------------------------------------------------------------------------
# Combine top markdown files into a single output file

# Get the top N rows based on nb_markdown_kept
top_pages = final_df.head(nb_markdown_kept)

# Initialize the combined markdown content (no heading)
combined_markdown = ""

# Function to read a markdown file and add it to our combined markdown
def add_markdown_file(page_title, file_path):
    full_path = markdowns_folders / file_path
    try:
        with open(full_path, 'r', encoding='utf-8') as file:
            content = file.read()
            
        # Create a section divider with file information using the requested format
        divider = f"""
================================================================================
Page: {page_title}
Path: {file_path}  
================================================================================

"""
        return divider + content + "\n\n"
    except FileNotFoundError:
        return f"""
================================================================================
Page: {page_title}
Path: {file_path}  
================================================================================

*File not found at {full_path}*

"""

# Add each markdown file to the combined content
for _, row in top_pages.iterrows():
    markdown_content = add_markdown_file(
        row['Page title and screen class'], 
        row['File Path']
    )
    combined_markdown += markdown_content

# Write the combined markdown to the output file
output_file = outputs_folders / f'nersc_documentation_top{nb_markdown_kept}.txt'
with open(output_file, 'w', encoding='utf-8') as file:
    file.write(combined_markdown)

print(f"\nCombined markdown file created at: {output_file}")