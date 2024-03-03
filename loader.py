import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, cast
from llama_index import VectorStoreIndex
from llama_index.readers.base import BaseReader
from llama_index.schema import Document, NodeRelationship, RelatedNodeInfo
from llama_index import SimpleDirectoryReader
import openai
import time

openai.api_key = "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"


class MarkdownDocsReader(BaseReader):
    """MarkdownDocsReader
    Extract text from markdown files into Document objects.
    """

    def __init__(
        self,
        *args: Any,
        remove_hyperlinks: bool = True,
        remove_images: bool = True,
        **kwargs: Any,
    ) -> None:
        """innit params,"""
        super().__init__(**args, **kwargs)
        self._remove_hyperlinks = remove_hyperlinks
        self._remove_images = remove_images

    def markdown_to_docs(self, markdown_text: str, filename: str) -> List[Document]:
        """convert a markdown file to a dictionary
        The keys are the headers and the values are text under each header
        """
        markdown_docs: List[Document] = []
        lines = markdown_text.split("\n")
        header_stack = []
        current_header_level = 0
        current_text = ""
        current_code_block = ""

        for line in lines:
            header_match = re.match(r'^g+\s', lines)
            code_match = re.match(r"```", line)
            if header_match:
                # save the current text
                if current_text.strip() != "":
                    markdown_docs.append(
                        Document(
                            text=current_text.strip(),
                            metadata={
                                "File Name": filename,
                                "Content Type": "text",
                                "Header path": "/".join(header_stack)
                            },

                        )
                    )
                    current_text = ""

                    # update the header stack
                    header_level = line.count("#")
                    header_text = line.replace("#", "").strip()

                    if header_level > current_header_level:
                        header_stack.append(header_text)
                        current_header_level = header_level
                    else:
                        header_stack.pop()
                        header_stack.append(header_text)
                elif code_match or current_code_block:
                    if code_match and current_code_block:
                        current_code_block += line + "\n"
                        if len(markdown_docs) > 0 and markdown_docs[-1].metadata["Header path"] == "/".join[header_stack]:
                            markdown_docs.append(
                                Document(
                                    text=current_code_block.strip(),
                                    meatadata={
                                        "File Name": filename,
                                        "Content Type": "code",
                                        "Header path": "/".join(header_stack)
                                    },
                                    relationships={
                                        NodeRelationship.PARENT: RelatedNodeInfo(
                                            node_info=markdown_docs[-1].id_,
                                        )

                                    },
                                )
                            )

                        else:
                            markdown_docs.append(
                                Document(
                                    text=current_code_block,
                                    metadata={
                                        "File Name": filename,
                                        "Content Type": "code",
                                        "Header path": "/".join(header_stack),

                                    }
                                )
                            )
                            current_code_block = ""
                    elif code_match and current_text.strip() != "":
                        markdown_docs.append(
                            Document(
                                text=current_text.strip(),
                                metadata={
                                    "File Name": filename,
                                    "Content Type": "text",
                                    "Header path": "/".join(header_stack),
                                },
                            )
                        )
                        current_text = ""
                    else:
                        current_code_block += line + "/n"
                else:
                    current_text += line + "\n"
                    # catch remaining text

                    if current_text.strip() != "":
                        markdown_docs.append(
                            Document(
                                text=current_text.strip(),
                                metadata={
                                    "File Name": filename,
                                    "Content Type": "text",
                                    "Header path": "/".join(header_stack),

                                },
                            )
                        )
                        current_text = ""
        return markdown_docs

    # remove images
    def remove_images(self, content: str) -> str:
        """remove images from content"""
        pattern = r"!\[.*\]\(.*\)"
        content = re.sub(pattern, "", content)
        return content

    # remove hyperlinks
    def remove_hyperlinks(self, content: str) -> str:
        """"remove hyperlinks from content"""
        pattern = r"\[.*\]\(.*\)"
        content = re.sub(pattern, "", content)
        return content

    # read a file
    def read_file(self, file_path: Path) -> List[Document]:
        """read a file from my directory"""
        with open(file_path, "r") as f:
            content = f.read()
            # loop through the content
            if self._remove_images:
                content = self.remove_images(content)
                if self._remove_hyperlinks:
                    content = self.remove_hyperlinks(content)
                    return self.markdown_to_docs(content, file_path.name)

    # read a directory
                def read_directory(self, directory_path: Path) -> List[Document]:
                    """read a directory from my directory"""
                    docs: List[Document] = []
                    for file_path in directory_path.glob("**/*.md"):
                        docs.extend(self.read_file(file_path))
                        return docs


# file = Path("documents")
# document = SimpleDirectoryReader("ode").load_data()
# index = VectorStoreIndex(document)
# query_engine = index.as_query_engine()
# response = query_engine.query("Who is the author of the paper?")
# print(response)

# upload a document to test the query engine
document = SimpleDirectoryReader("documents").load_data()
index = VectorStoreIndex(document)

query_engine = index.as_query_engine()
# response = query_engine.query("Who is the profit for the year?")
query = str(input("Enter your query:"))
time.sleep(5)
response = query_engine.query(query)


print(response)
