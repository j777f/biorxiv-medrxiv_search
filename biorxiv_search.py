import requests
import json
from datetime import date, timedelta

def fetch_biorxiv_papers(start_date, end_date, server='biorxiv'):
    """
    从bioRxiv或medRxiv的API获取指定主题，指定日期范围内的论文。

    Args:
        按照指定日期范围获取论文档案。默认设置获得十天内的论文。
        日期范围可以在主函数中修改。
        start_date (str): 开始日期，格式为 'YYYY-MM-DD'.
        end_date (str): 结束日期，格式为 'YYYY-MM-DD'.
        server (str): 服务器，使用'biorxiv' .

    Returns:
        list: 包含论文档案的列表，如果请求失败则返回None.
    """
    # 支持自动翻页，获取所有论文
    # API每页最多返回100条，需用cursor翻页
    all_papers = []
    cursor = 0
    while True:
        url = f"https://api.biorxiv.org/details/{server}/{start_date}/{end_date}/{cursor}"
        print(f"Getting data from: {url}")
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            papers = data.get('collection', [])
            if not papers:
                break
            all_papers.extend(papers)
            # API返回的count字段为本次返回数量，total为总数
            count = data.get('count', 0)
            if count < 100:
                break
            cursor += 100
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            break
        except json.JSONDecodeError:
            print("Failed to parse JSON response.")
            break
    return all_papers

def print_papers_details(papers):
    """
    以可读的格式打印论文的详细信息。

    Args:
        papers (list): 从API获取的论文档案列表。
    """
    if not papers:
        print("Found no papers or there was an error fetching data.")
        return

    print("Results:")
    print(f"Successfully fetched {len(papers)} papers.\n")

    for paper in papers:
        title = paper.get('title', '')
        authors = paper.get('authors', '')
        doi = paper.get('doi', '')
        journal = paper.get('journal', '')
        year = paper.get('year', '')
        published_date = paper.get('date', '')
        abstract = paper.get('abstract', '')
        citations = paper.get('cited_by', '') if 'cited_by' in paper else ''
        # 构建论文的URL
        paper_url = f"https://doi.org/{doi}"

        print(f"Title: {title}")
        print(f"Authors: {authors}")
        print(f"Journal: {journal}")
        print(f"DOI: {doi}")
        print(f"URL: {paper_url}")
        print(f"Year: {year}")
        print(f"Citations: {citations}")
        print(f"Published: {published_date}")
        print(f"Abstract: {abstract}")
        print("\n")

def filter_papers_by_query(papers, query):
    """
    根据关键词过滤论文，标题或摘要包含query即保留。
    """
    if not query:
        return papers
    query_lower = query.lower()
    filtered = []
    for paper in papers:
        title = paper.get('title', '').lower()
        abstract = paper.get('abstract', '').lower()
        if query_lower in title or query_lower in abstract:
            filtered.append(paper)
    return filtered

if __name__ == "__main__":
    # --- 设置参数 ---
    # 获取昨天的日期作为结束日期
    end_date = date.today() - timedelta(days=1)
    # 获取十天前的日期作为开始日期
    start_date = end_date - timedelta(days=10)
    # 格式化为 'YYYY-MM-DD' 字符串
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')

    print(f"Fetching bioRxiv papers from {start_date_str} to {end_date_str}...")

    # 用户输入关键词
    query = input("Query：").strip()
    # 调用函数获取论文
    papers_collection = fetch_biorxiv_papers(start_date_str, end_date_str)
    # 根据query过滤
    filtered_papers = filter_papers_by_query(papers_collection, query)
    # 打印结果
    if filtered_papers:
        print_papers_details(filtered_papers)
    else:
        print("No papers found matching the query or there was an error fetching data.")
