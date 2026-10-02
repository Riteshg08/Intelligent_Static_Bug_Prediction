from pydantic import BaseModel
from typing import Optional

class FunctionExtractionResult(BaseModel):
    file_path: str
    language: str
    function_name: str
    qualified_name: str
    start_line: int
    end_line: int
    source_text: str
    content_hash: str
