import asyncio
from typing import List

from langchain.chains import MapReduceDocumentsChain, ReduceDocumentsChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains.llm import LLMChain
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_text_splitters import CharacterTextSplitter

from abc import ABC, abstractmethod

from src.consumption.consumers.interface import ISummarizer
from src.consumption.models.consumption.asssistant import AIAssistant
from src.services.openai_api_package.chat_gpt_package.client import GPTClient
from src.services.openai_api_package.chat_gpt_package.model import GPTMessage, GPTRole


class DocumentSummarizer(ISummarizer):

    def __init__(self, model="gpt-3.5-turbo-0125", max_response_tokens=4000):
        self.model = model
        self.max_response_tokens = max_response_tokens
        self.llm = None
        self.map_reduce_chain = None
        self.map_prompt = None
        self.reduce_prompt = None
        self.document_combiner = None
        self.reduce_chain = None
        self.map_chain = None

    def setup_chains(self, assistant: AIAssistant):
        self.llm = ChatOpenAI(temperature=0, model=self.model, )
        # Set up templated prompts
        self.setup_map_template(assistant)
        self.setup_reduce_template(assistant)

        # Set up chains for processing documents
        self.map_chain = LLMChain(llm=self.llm, prompt=self.map_prompt, )
        self.reduce_chain = LLMChain(llm=self.llm, prompt=self.reduce_prompt, )
        self.document_combiner = self.create_document_combiner()

    def setup_map_template(self, assistant: AIAssistant):
        map_template = f"""
            Ниже представлен набор документов которые представляют часть текста:
             {'{docs}'}
             {assistant.assistant_prompt},
             {assistant.user_prompt_for_chunks}
           Убедитесь, что ваш анализ помогает восстановить контекст, если эта часть будет рассматриваться отдельно от других частей документа.
           Полезный ответ->:"""
        self.map_prompt = PromptTemplate.from_template(map_template)

    def setup_reduce_template(self, assistant: AIAssistant):
        reduce_template = f"""
           Вы получили набор кратких резюме каждой части: 
           -> {'{docs}'}
           {assistant.assistant_prompt},
           {assistant.user_prompt}
           Скомпилированный ответ:"""
        self.reduce_prompt = PromptTemplate.from_template(reduce_template)

    def create_document_combiner(self):
        # Define document processing chains
        return ReduceDocumentsChain(
            combine_documents_chain=StuffDocumentsChain(
                llm_chain=self.reduce_chain,
                document_variable_name="docs"),
            collapse_documents_chain=StuffDocumentsChain(
                llm_chain=self.reduce_chain,
                document_variable_name="docs"),
            token_max=self.max_response_tokens)

    def setup_map_reduce_chain(self):
        # Define the map-reduce process for document summarization
        self.map_reduce_chain = MapReduceDocumentsChain(
            llm_chain=self.map_chain,
            reduce_documents_chain=self.document_combiner,
            document_variable_name="docs",
            return_intermediate_steps=False)

    @staticmethod
    def split_docs(text):
        text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=100)
        docs = [Document(page_content=x) for x in text_splitter.split_text(text)]
        return docs

    async def summarize(self, transcribed_text, assistant: AIAssistant):
        self.setup_chains(assistant)
        self.setup_map_reduce_chain()
        split_docs = self.split_docs(text=transcribed_text)
        return self.map_reduce_chain.run(split_docs)

    async def __call__(self, transcribed_text, assistant: AIAssistant):
        return await self.summarize(transcribed_text, assistant)


class GptSummarizer(ISummarizer):

    def __init__(self, gpt_client: GPTClient):
        self.gpt_client = gpt_client

    async def summarize(self, transcribed_text: str, assistant: AIAssistant) -> str:
        user_message = GPTMessage(role=GPTRole.USER, content=assistant.user_prompt + transcribed_text)
        system_message = GPTMessage(role=GPTRole.SYSTEM, content=assistant.assistant_prompt)
        return await self.gpt_client.complete(user_message, system_message)

    async def __call__(self, transcribed_text: str, assistant: AIAssistant) -> str:
        return await self.summarize(transcribed_text, assistant)
