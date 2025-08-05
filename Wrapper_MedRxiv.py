from typing import Optional
from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import BaseTool
from pydantic import Field

from MedRxiv import MedRxivAPIWrapper

class MedRxivQueryRun(BaseTool):
    """Tool that searches the MedRxiv API."""

    name: str = "med_rxiv"
    description: str = (
        "A wrapper around MedRxiv. "
        "Useful for when you need to answer questions about preprints, medicine, and health sciences. "
        "Input should be a search query.")
    api_wrapper: MedRxivAPIWrapper = Field(default_factory=MedRxivAPIWrapper)

    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        from datetime import date, timedelta
        # 默认查近10天
        end_date = date.today() - timedelta(days=1)
        start_date = end_date - timedelta(days=10)
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
        papers = self.api_wrapper.fetch_medrxiv_papers(start_date_str, end_date_str)
        filtered = self.api_wrapper.filter_papers_by_query(papers, query)
        if not filtered:
            return "No papers found matching the query or there was an error fetching data."
        # 格式化输出
        results = []
        for paper in filtered[:5]:  # 只返回前5条，防止输出过多
            title = paper.get('title', '')
            authors = paper.get('authors', '')
            doi = paper.get('doi', '')
            journal = paper.get('journal', '')
            year = paper.get('year', '')
            url = f"https://doi.org/{doi}" if doi else ''
            published_date = paper.get('date', '')
            abstract = paper.get('abstract', '')
            citations = paper.get('cited_by', '') if 'cited_by' in paper else ''
            results.append(f"Title: {title}\nAuthors: {authors}\nPublished: {published_date}\nURL: {url}\nAbstract: {abstract}\nCitations: {citations}\nJournal: {journal}\nYear: {year}\n")
        return '\n'.join(results)

# 示例用法
if __name__ == "__main__":
    tool = MedRxivQueryRun()
    query = "covid-19"
    result = tool._run(query)
    print(f"Query: {query}\nResult: {result}")
