import requests
import json
import os
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from dotenv import load_dotenv

load_dotenv()
console = Console()

# Ini adalah "tiket" rahasia yang dipake Web Upwork
# (Kita ambil dari network tab, ini aman karena cuma nge-query data publik)
GRAPHQL_URL = "https://www.upwork.com/api/graphql/v1"

def search_upwork(keyword):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Origin": "https://www.upwork.com",
        "Referer": f"https://www.upwork.com/nx/search/jobs/?q={keyword}"
    }
    
    # Query GraphQL buat cari proyek
    payload = {
        "query": """
        query SearchJobs($query: String!) {
            search(query: $query) {
                jobs {
                    id
                    title
                    description
                    budget {
                        amount
                        currency
                    }
                    type
                }
            }
        }
        """,
        "variables": {"query": keyword}
    }
    
    console.print(f"[cyan]Searching for '{keyword}' via API...[/cyan]")
    try:
        res = requests.post(GRAPHQL_URL, json=payload, headers=headers, timeout=10)
        res.raise_for_status()
        data = res.json()
        
        jobs = data.get("data", {}).get("search", {}).get("jobs", [])
        return jobs
    except Exception as e:
        console.print(f"[danger]API Error: {e}[/danger]")
        return []

def main():
    keyword = Prompt.ask("\nEnter project keyword").strip()
    if not keyword: return
    
    jobs = search_upwork(keyword)
    
    if not jobs:
        console.print("[warning]No projects found. Maybe Upwork changed the API key.[/warning]")
        return
        
    table = Table(title="Upwork API Results", header_style="bold magenta")
    table.add_column("No", style="cyan")
    table.add_column("Title", style="green")
    table.add_column("Budget", style="yellow")
    
    for i, job in enumerate(jobs[:10]):
        budget = f"${job.get('budget', {}).get('amount', 'N/A')}" if job.get('budget') else "N/A"
        table.add_row(str(i+1), job.get('title', 'No Title')[:50]+"...", budget)
        
    console.print("\n", table, "\n")

if __name__ == "__main__":
    main()
