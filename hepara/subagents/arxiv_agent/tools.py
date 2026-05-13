import os
from arxivflow import arXivFlow
from collections import Counter

CATEGORIES = os.getenv("CATEGORIES")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")

def _calculate_relevance(row_keywords: str | list[str], search_keywords: list[str]) -> int:
    """
    Calculates the relevance score for a paper based on its keywords and the search keywords.
    Match papers (up to 5) based on keywords.
    """
    if not row_keywords:
        return 0
    if isinstance(row_keywords, str):
        row_k_list = [k.strip().lower() for k in row_keywords.split(',') if k.strip()]
    elif isinstance(row_keywords, list):
        row_k_list = [str(k).strip().lower() for k in row_keywords if str(k).strip()]
    else:
        return 0
        
    search_k_lower = [k.lower() for k in search_keywords]
    matches = set(search_k_lower) & set(row_k_list)
    return len(matches)

def recommend_by_trends(max_results: int=100) -> dict:
    """
    Recommends latest papers based on trending topics in the last week.
    It finds the most frequent keywords in the latest papers and recommends papers matching those keywords.
    """
    if not CATEGORIES or not OLLAMA_MODEL:
        return {"error": "Error: One or more required environment variables (CATEGORIES, OLLAMA_MODEL) not set in .env file."}
    
    categories = [cat.strip() for cat in CATEGORIES.split(',') if cat.strip()]
    # Initialize arXivFlow and fetch data
    flow = arXivFlow(categories=categories, ollama_model=OLLAMA_MODEL, max_results=max_results)
    flow.set_client_parameters(delay_seconds=3.0, num_retries=3)
    df = flow.get_arxiv_data(download_pdfs=False)

    if df is None or df.empty:
        return {"error": "Error:No papers found for the specified categories."}
    
    # Drop duplicates based on arXiv ID to ensure unique recommendations
    id_col = "arXiv ID"  # Default column name for arXiv ID
    if id_col:
        df = df.drop_duplicates(subset=[id_col])

    if 'Keywords' not in df.columns:
        return {"error": "Error: The papers database does not contain a 'Keywords' column."}
    
    all_keywords = []
    for k_val in df['Keywords'].dropna():
        if isinstance(k_val, str):
            all_keywords.extend([k.strip() for k in k_val.split(',') if k.strip()])
        elif isinstance(k_val, list):
            all_keywords.extend([str(k).strip() for k in k_val if str(k).strip()])  

    if all_keywords:
        counts = Counter(all_keywords)
        top_trending = counts.most_common(3)
        search_keywords = [k for k, _ in top_trending] # Get top 3 trending keywords
        keyword_counts = {k: c for k, c in top_trending}
    else:
        return {"error": "Error: No keywords found in the database to determine trends."}
    
    df['relevance_score'] = df['Keywords'].apply(lambda x: _calculate_relevance(x, search_keywords))
    
    # Filter for relevant papers and then pick top 5
    relevant_df = df[df['relevance_score'] > 0]
    
    if relevant_df.empty:
        return {"error": f"Error: No papers matched the keywords: {', '.join(search_keywords)}"}
    
    top_papers = relevant_df.sort_values(by='relevance_score', ascending=False).head(5)

    report = {"keywords": keyword_counts, "papers": []}

    for _, row in top_papers.iterrows():
        title = row.get('Title', row.get('title', 'No Title'))
        arxiv_id = row.get('arXiv ID', row.get('arxiv_id', row.get('id', 'N/A')))
        
        report['papers'].append({
            "title": title,
            "arxiv_id": arxiv_id,
        })
    return report