import asyncio

from langchain.chains import MapReduceDocumentsChain, ReduceDocumentsChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains.llm import LLMChain
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_text_splitters import CharacterTextSplitter

from container import publisher, postgres_database_repository
from domain.enteties.IOdataenteties.queue_enteties import TranscribedTextId
from domain.enteties.databse_enteties.tranascribed_text_model import TranscribedText


class DocumentSummarizer:
    def __init__(self, llm):
        self.llm = llm
        self.max_response_tokens = 4000

    def setup_chains(self):
        # Set up templated prompts
        self.setup_map_template()
        self.setup_reduce_template()

        # Set up chains for processing documents
        self.map_chain = LLMChain(llm=self.llm, prompt=self.map_prompt,)
        self.reduce_chain = LLMChain(llm=self.llm, prompt=self.reduce_prompt,)
        self.document_combiner = self.create_document_combiner()

    def setup_map_template(self):
        map_template = """
         Ниже представлен набор документов которые представляют часть текста из лекции или из обучающего материалы:
          {docs}
          Пожалуйста, обратите внимание на следующее:->
        1. Идентификация ключевых идей: Определите и выделите ключевые идеи и тезисы, описанные в этой части текста.
        2. Связь с общей темой лекции: Предложите, как эти идеи могут быть связаны с общей темой лекции, если это возможно.
        3. Запись особенностей стиля или методов преподавания, использованных в данной части.
        
        Убедитесь, что ваш анализ помогает восстановить контекст, если эта часть будет рассматриваться отдельно от других частей документа.
        
        На основе этого списка документов определите, пожалуйста, основные темы. 
        Полезный ответ->:"""
        self.map_prompt = PromptTemplate.from_template(map_template)

    def setup_reduce_template(self):
        reduce_template = """
        Вы получили набор кратких резюме каждой части лекции: 
        -> {docs}
        Ваша задача: ->
        1. Анализируя предоставленные резюме, сформулируйте окончательное, обобщенное резюме всей лекции, консолидируя основные тезисы и темы.
        2. Из полученных кратких резюме выделите ключевые пункты для формулирования домашнего задания, которое будет укреплять понимание освещенных тем и обсуждений.
        3. Определите и составьте список рекомендуемых книг, который основан на анализе всех резюме которые вы получили. Эти книги должны быть полезны для дальнейшего изучения материала и выполнения домашнего задания. Список должен содержать только реально существующие публикации.
        Убедитесь, что ваше консолидированное резюме обеспечивает ясное и всеобъемлющее понимание всех ключевых моментов и педагогических методов, презентованных в видеозаписи лекции.   
        Скомпилированый ответ:"""
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
            token_max=4000)

    def setup_map_reduce_chain(self):
        # Define the map-reduce process for document summarization
        self.map_reduce_chain = MapReduceDocumentsChain(
            llm_chain=self.map_chain,
            reduce_documents_chain=self.document_combiner,
            document_variable_name="docs",
            return_intermediate_steps=False)

    def split_docs(self, text):
        print(text)
        text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=100)
        docs = [Document(page_content=x) for x in text_splitter.split_text(text)]
        return docs

def run_langchain(text):
    #gpt-3.5-turbo-0125
    llm = ChatOpenAI(temperature=0,model="gpt-3.5-turbo-0125", )
    summarizer = DocumentSummarizer(llm)
    summarizer.setup_chains()
    summarizer.setup_map_reduce_chain()
    split_docs = summarizer.split_docs(text=text)
    return summarizer.map_reduce_chain.run(split_docs)

@publisher.publish(queue="summary")
async def summarize_text(text_id) ->str:
    # Получить текст
    text:TranscribedText = await postgres_database_repository.get_transcribed_text_by_id(result_id=text_id)
    # Отправить в лонгченй и Получить результат саммари
    result = run_langchain(text=text.text)
    #Сохранить результат
    summary_id = await postgres_database_repository.save_summary_text(text=result, addressee=None)
    return TranscribedTextId(
        id_text=summary_id,
        addressee=None,
        description=None,
    ).json()




if __name__ == "__main__":
    asyncio.run(summarize_text(text_id=19))