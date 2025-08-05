
from typing import Optional
import sys
import os

from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import BaseTool
from pydantic import Field

# 假设BioRxivAPIWrapper已在BioRxiv.py中实现
from BioRxiv import BioRxivAPIWrapper

#src.tools.searchAPIchoose.
# 这是魔改了langchain的biorxiv搜索，增加了近五年检索和按照时间范围检索的逻辑（如有需要可扩展）。
class BioRxivQueryRun(BaseTool):
    """Tool that searches the BioRxiv API."""

    name: str = "bio_rxiv"
    description: str = (
        "A wrapper around BioRxiv. "
        "Useful for when you need to answer questions about preprints, biology, and life sciences. "
        "Input should be a search query.")
    api_wrapper: BioRxivAPIWrapper = Field(default_factory=BioRxivAPIWrapper)

    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the BioRxiv tool."""
        from datetime import date, timedelta
        # 默认查近10天
        end_date = date.today() - timedelta(days=1)
        start_date = end_date - timedelta(days=10)
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
        papers = self.api_wrapper.fetch_biorxiv_papers(start_date_str, end_date_str)
        filtered = self.api_wrapper.filter_papers_by_query(papers, query)
        if not filtered:
            return "No papers found matching the query or there was an error fetching data."
        # 格式化输出
        results = []
        for paper in filtered[:5]:  # 只返回前5条，防止输出过多
            title = paper.get('title', '')
            authors = paper.get('authors', '')
            doi = paper.get('doi', '')
            url = f"https://doi.org/{doi}" if doi else ''
            published_date = paper.get('date', '')
            abstract = paper.get('abstract', '')
            journal = paper.get('journal', '')
            year = paper.get('year', '')
            citations = paper.get('cited_by', '') if 'cited_by' in paper else ''
            results.append(f"Title: {title}\nAuthors: {authors}\nPublished: {published_date}\nDOI: {doi}\nURL: {url}\nAbstract: {abstract}\nCitations: {citations}\nJournal: {journal}\nYear: {year}\n")
        return '\n'.join(results)


# 示例用法
if __name__ == "__main__":
    tool = BioRxivQueryRun()
    query = "diabetes"
    result = tool._run(query)
    print(f"Query: {query}\nResult: {result}")
