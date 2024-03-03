import re
import openai
from typing import List, Any, Dict, Tuple, Optional, cast 
from llama_index.schema import Document, NodeRelationship, RelatedNodeInfo

class MarkdownDocsReader(BaseReader):
    def __init__(self, *args: Any, remove_hyperlinks: bool = True, remove_images: bool = True, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._remove_hyperlinks = remove_hyperlinks
        self._remove_images = remove_images

    def markdown_to_docs(self, markdown_text: str, filename: str) -> List[Document]:
        markdown_docs: List[Document] = []
        lines = markdown_text.split("\n")
        header_stack = []
        current_header_level = 0
        current_text = ""
        current_code_block = ""

        for line in lines:
            header_match = re.match(r'^(#+)\s+(.*)', line)
            code_match = re.match(r'^```', line)
            
            if header_match:
                if current_text.strip():
                    self._add_document(markdown_docs, current_text, filename, header_stack, "text")
                    current_text = ""

                header_level = len(header_match.group(1))
                header_text = header_match.group(2).strip()

                while len(header_stack) >= header_level:
                    header_stack.pop()
                header_stack.append(header_text)
                current_header_level = header_level

            elif code_match:
                if current_code_block:
                    current_code_block += line + "\n"
                else:
                    if current_text.strip():
                        self._add_document(markdown_docs, current_text, filename, header_stack, "text")
                        current_text = ""
                    current_code_block = line + "\n"
            else:
                if current_code_block:
                    current_code_block += line + "\n"
                else:
                    current_text += line + "\n"

        if current_text.strip():
            self._add_document(markdown_docs, current_text, filename, header_stack, "text")
        if current_code_block.strip():
            self._add_document(markdown_docs, current_code_block, filename, header_stack, "code")

        return markdown_docs

    def _add_document(self, markdown_docs: List[Document], text: str, filename: str, header_stack: List[str], content_type: str):
        header_path = "/".join(header_stack) if header_stack else "Root"
        markdown_docs.append(
            Document(
                text=text.strip(),
                metadata={
                    "File Name": filename,
                    "Content Type": content_type,
                    "Header Path": header_path
                }
            )
        )

# Rest of your code remains the same
