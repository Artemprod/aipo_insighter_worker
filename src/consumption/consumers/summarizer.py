import asyncio
from typing import List

from langchain.chains import MapReduceDocumentsChain, ReduceDocumentsChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains.llm import LLMChain
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_text_splitters import CharacterTextSplitter

from src.consumption.consumers.interface import ISummarizer
from src.consumption.exeptions.summarize import NoResponseFromChatGptSummarization
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

    def setup_chains(self, assistant: AIAssistant, user_prompt: str):
        self.llm = ChatOpenAI(temperature=0, model=self.model, )
        # Set up templated prompts
        self.setup_map_template(assistant, user_prompt)
        self.setup_reduce_template(assistant, user_prompt)

        # Set up chains for processing documents
        self.map_chain = LLMChain(llm=self.llm, prompt=self.map_prompt, )
        self.reduce_chain = LLMChain(llm=self.llm, prompt=self.reduce_prompt, )
        self.document_combiner = self.create_document_combiner()

    def setup_map_template(self, assistant: AIAssistant, user_prompt: str):
        map_template = f"""
            Ниже представлен набор документов которые представляют часть текста:
             {'{docs}'}
             {assistant.assistant_prompt},
             {assistant.user_prompt_for_chunks},
             {user_prompt if user_prompt is not None else " "}
           Убедитесь, что ваш анализ помогает восстановить контекст, если эта часть будет рассматриваться отдельно от других частей документа.
           Полезный ответ->:"""
        self.map_prompt = PromptTemplate.from_template(map_template)

    def setup_reduce_template(self, assistant: AIAssistant, user_prompt: str):
        reduce_template = f"""
           Вы получили набор кратких резюме каждой части: 
           -> {'{docs}'}
           {assistant.assistant_prompt},
           {assistant.user_prompt},
           {user_prompt if user_prompt is not None else " "}
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

    async def summarize(self, transcribed_text, assistant: AIAssistant, user_prompt: str):
        self.setup_chains(assistant, user_prompt)
        self.setup_map_reduce_chain()
        split_docs = self.split_docs(text=transcribed_text)
        return self.map_reduce_chain.run(split_docs)

    async def __call__(self, transcribed_text, assistant: AIAssistant, user_prompt: str):
        task = asyncio.create_task(self.summarize(transcribed_text, assistant, user_prompt))
        return await task


class GptSummarizer(ISummarizer):

    def __init__(self,
                 gpt_client: GPTClient):
        self.gpt_client = gpt_client

    async def summarize(self, transcribed_text: str, assistant: AIAssistant, user_prompt: str) -> str:
        user_prompt = user_prompt if user_prompt is not None else " "
        try:
            messages: List[GPTMessage] = [
                GPTMessage(role=GPTRole.USER, content=assistant.user_prompt + user_prompt + transcribed_text)]
            system_message: GPTMessage = GPTMessage(role=GPTRole.SYSTEM, content=assistant.assistant_prompt)
            result = await self.gpt_client.complete(messages, system_message)
        except Exception as e:
            raise NoResponseFromChatGptSummarization(exception=e) from e
        else:
            return result

    async def __call__(self, transcribed_text: str, assistant: AIAssistant, user_prompt: str) -> str:
        return await self.summarize(transcribed_text, assistant, user_prompt)
