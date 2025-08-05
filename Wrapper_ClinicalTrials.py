from typing import Optional
from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import BaseTool
from pydantic import Field

from ClinicalTrials import ClinicalTrialsAPIWrapper

class ClinicalTrialsQueryRun(BaseTool):
    """Tool that searches the ClinicalTrials.gov API."""

    name: str = "clinical_trials"
    description: str = (
        "A wrapper around ClinicalTrials.gov. "
        "Useful for when you need to answer questions about clinical trials, interventions, and study eligibility. "
        "Input should be a search query."
    )
    api_wrapper: ClinicalTrialsAPIWrapper = Field(default_factory=ClinicalTrialsAPIWrapper)

    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        # 默认查近15条 recruiting 试验
        results = self.api_wrapper.search_and_parse(query, status="recruiting", max_studies=15)
        if not results:
            return "No relevant clinical trials found."
        # 简要格式化输出检索结果
        output = []
        for item in results:
            output.append(
                f"nctId: {item['nctId']}\n"
                f"briefTitle: {item['briefTitle']}\n"
                f"overallStatus: {item['overallStatus']}\n"
                f"conditions: {item['conditions']}\n"
                f"interventionName: {item['interventionName']}\n"
                f"leadSponsorName: {item['leadSponsorName']}\n"
                f"briefSummary: {item['briefSummary']}\n\n"
                f"eligibilityCriteria: {item['eligibilityCriteria']}\n"
            )
        return "\n".join(output)

# 使用示例
if __name__ == "__main__":
    tool = ClinicalTrialsQueryRun()
    query = "lung cancer"# query example
    result = tool._run(query)
    print(f"Query: {query}\nResult:\n{result}")