from langchain.document_loaders.text import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
from langchain_community.vectorstores import chroma
import streamlit as st
from langchain.chains.combine_documents.stuff import create_stuff_documents_chain
from langchain_openai import ChatOpenAI, OpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
import openai

load_dotenv()



def isLatest(Query: str):
    model = 'gpt-4'
    messages = [
        {"role": "system", "content": "Your task is to determine whether to use an online or offline model based on the user's query. Respond with `Yes` if the user's query requires access to the latest information, such as real-time data or recent events. Respond with `No` if the query involves calculations, historical information, or does not specifically require up-to-date data. Note that queries asking for calculations or interpretations of current rules, like the new tax regime, without needing real-time data should not be considered as requiring an online model."},
        {"role": "user", "content": Query}
    ]
    response = openai.chat.completions.create(
        messages=messages,
        model=model
    )
    return response.choices[0].message.content.strip()

def Perplexity(Query: str):
    model = 'sonar-medium-online'
    APIKEY = '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'
    messages = [
        {"role": "system", "content": "You are part of 1 Finance's online Tax assistants, specialising in Indian law. Your task is to retrieve up to date information about the Indian tax laws, updates etc based on the user input. If the user query is unclear, please let the user know that it is unclear - don't generate unverified or unsubstantiated output. Keep it concise. Moreover, refuse to return answers for non india tax laws/updates related queries"},
        {"role": "user", "content": Query}
    ]
    client = openai.OpenAI(api_key=APIKEY, base_url='https://api.perplexity.ai')
    response = client.chat.completions.create(
        model=model,
        messages=messages
    )
    return response.choices[0].message.content.strip()


def VectorStore(path='DB.txt'):
    loader = TextLoader(file_path=path)
    document = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=400, add_start_index=True)
    chunks = splitter.split_documents(documents=document)
    if not chunks:
        raise ValueError('No document chunks found. please reviwe your code')
    store = chroma.Chroma.from_documents(chunks, OpenAIEmbeddings())
    return store

def RetrievalChain(vectorStore):
    LLM = ChatOpenAI(model='gpt-4-turbo')
    Retriever = vectorStore.as_retriever(search_type='similarity')

    prompt = ChatPromptTemplate.from_messages([
        ("system", "Your task is to assist users with their Tax related query. Do your absolute best to assist them with their queries. If you don't know, say you don't know."),
        MessagesPlaceholder(variable_name='chat_history'),
        ("user", "{input}")
    ])
    chain = create_history_aware_retriever(LLM, Retriever, prompt)
    return chain

def RAGChain(retreiverChain):
    LLM = ChatOpenAI(model='gpt-4-turbo')
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
        You are 1 Finance's personal tax assistant. Tasked with calculating user's tax liability. Follow the steps outlined below to assist users in the best possible manner. Note: Only address their tax related queries, ask probing/clarifying if user instructions are not clear. DO NOT answer anything that doesn't have to do with tax.

        Here are the steps you should ideally perform before spitting an answer.

        1. Determine Gross Total Income
        `Calculate Income from All Sources: Include salary/wages, income from house property (rent), profits from business or profession, capital gains (short and long term), and income from other sources like interest, dividends, etc.
        Clubbing of Income: Include income of spouse, minor children, etc., if applicable under the law.
        2. Calculate Deductions
        Identify Eligible Deductions: Deductions are available under various sections of the Income Tax Act, 1961, such as 80C (investments in PPF, EPF, life insurance, etc.), 80D (medical insurance), 80E (education loan interest), and many others.
        Calculate Total Deductions: Sum up all the deductions for which you are eligible.
        3. Determine Taxable Income
        Subtract Deductions from Gross Total Income: Deduct the total calculated deductions from your gross total income to arrive at your taxable income. Deduct ₹50,000 as standard deduction if the income is from salary
        4. Apply the Applicable Tax Slabs
        Identify the Correct Tax Regime: Choose between the old and the new tax regimes based on which one is more beneficial for you.
        Calculate Tax Based on Slabs: Apply the income tax rates as per the tax slabs of the chosen regime to your taxable income. The Indian tax system is progressive, so different portions of your income will be taxed at different rates.
        5. Add Cess
        Health and Education Cess: Add `4%` of the total tax as cess.
        6. Calculate Rebate and Relief
        Rebate under Section 87A: If applicable, deduct the rebate (for individuals with taxable income up to a certain limit).
        Relief under Section 89: If you've received arrears of salary, you might be eligible for relief under this section.
        7. Account for Advance Tax and TDS
        Deduct TDS and Advance Tax Paid: Subtract any tax already deducted at source (TDS) and any advance tax you have paid during the financial year from your total tax liability.
        8. Calculate Final Tax Liability
        Include Interest: If applicable, add interest under sections 234A, 234B, and 234C for late filing or payment of taxes.
        Total Tax Due or Refund: The result is your final tax liability. If the amount is negative, you are eligible for a refund: \n\n{context}
        """),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}")
    ])

    stuffChain = create_stuff_documents_chain(LLM, prompt)
    return create_retrieval_chain(retreiverChain, stuffChain)

def get_response(user_input):
    if isLatest(user_input) == 'Yes' or isLatest(user_input) == 'yes':
        print('Utilising Perplexity to fetch latest result!')
        response = Perplexity(user_input)
        return response
    retriever_chain = RetrievalChain(st.session_state.vector_store)
    conversation_rag_chain = RAGChain(retriever_chain)
    
    response = conversation_rag_chain.invoke({
        "chat_history": st.session_state.chat_history,
        "input": user_input
    })
    print(response)

    return response['answer']

# app config
st.set_page_config(page_title="1 Finance ChatBot", page_icon="🤖")
st.title("1 Finance ChatBot")

# Set the default website URL
# website_url = "https://1finance.co.in/sitemap.xml"

# GeneralDatabase = 'General Database.csv'


if "vector_store" not in st.session_state:
    st.session_state.vector_store = VectorStore(path='DB.txt')

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        AIMessage(content="Hey there! I am 1 Finance's personal tax assitant. How may I be of service?"),
    ]

# User input
user_query = st.chat_input("Type your message here...")
if user_query:
    response = get_response(user_query)
    st.session_state.chat_history.append(HumanMessage(content=user_query))
    st.session_state.chat_history.append(AIMessage(content=response))

# Display conversation
for message in st.session_state.chat_history:
    if isinstance(message, AIMessage):
        with st.chat_message("AI"):
            st.write(message.content)
    elif isinstance(message, HumanMessage):
        with st.chat_message("Human"):
            st.write(message.content)