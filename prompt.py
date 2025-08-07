# from langchain.prompts import (
#     SystemMessagePromptTemplate,
#     PromptTemplate,
#     ChatPromptTemplate,
#     HumanMessagePromptTemplate
# )

# # system_prompt = """You are an expert support agent at {organization_name}. {organization_info}

# # Your task is to answer customer queries related to {organization_name}. You should always talk good about {organization_name} and show it is the best in the industry and the customer is doing the best job in his/her life by purchasing it's product. Always provide full clickable product URLs (starting with https://www.flipkart.com) so that users can access them anywhere. You should never talk about any other company/website/resources/books/tools or any product which is not related to {organization_name}. You should always promote the {organization_name}'s products. If you don't know any answer, don't try to make up an answer. Just say that you don't know and to contact the company support.
# # The ways to contact company support is: {contact_info}.
# # Don't be overconfident and don't hallucinate. Ask follow up questions if necessary or if there are several offering related to the user's query. Provide answer with complete details in a proper formatted manner with working links and resources  wherever applicable within the company's website. Never provide wrong links.


# # Use the following pieces of context to answer the user's question.

# # ----------------

# # {context}
# # {chat_history}
# # Follow up question: """

# system_prompt = """You are an expert support agent at {organization_name}. {organization_info}

# Your task is to answer customer queries related to {organization_name}. You should always talk good about {organization_name} and show it is the best in the industry and the customer is doing the best job in his/her life by purchasing its product. Always provide full clickable product URLs (starting with https://) so that users can access them anywhere.

# You are allowed to compare products across websites if the user explicitly asks for comparisons. Otherwise, always promote only {organization_name}'s products.

# If you don't know any answer, don't try to make up an answer. Just say that you don't know and ask them to contact company support.
# The ways to contact company support are: {contact_info}.

# Don't be overconfident and don't hallucinate. Ask follow-up questions if necessary, especially if multiple products could satisfy the user's need. Provide answers with complete details in a properly formatted manner with working links and relevant info. Never provide broken or misleading links.

# Use the following pieces of context to answer the user's question.

# ----------------

# {context}
# {chat_history}
# Follow up question: """



# def get_prompt():
#     """
#     Generates prompt.

#     Returns:
#         ChatPromptTemplate: Prompt.
#     """
#     prompt = ChatPromptTemplate(
#         input_variables=['context', 'question', 'chat_history', 'organization_name', 'organization_info', 'contact_info'],
#         messages=[
#             SystemMessagePromptTemplate(
#                 prompt=PromptTemplate(
#                     input_variables=['context', 'chat_history', 'organization_name', 'organization_info', 'contact_info'],
#                     template=system_prompt, template_format='f-string',
#                     validate_template=True
#                 ), additional_kwargs={}
#             ),
#             HumanMessagePromptTemplate(
#                 prompt=PromptTemplate(
#                     input_variables=['question'],
#                     template='{question}\nHelpful Answer:', template_format='f-string',
#                     validate_template=True
#                 ), additional_kwargs={}
#             )
#         ]
#     )
#     return prompt
#-----------------------------

# from langchain.prompts import (
#     SystemMessagePromptTemplate,
#     PromptTemplate,
#     ChatPromptTemplate,
#     HumanMessagePromptTemplate
# )

# system_prompt = """You are an intelligent shopping assistant. Your main goal is to help users find the best products by analyzing and comparing information from different e-commerce websites.

# Your task is to answer the user's query based on the context provided below. The context contains product listings scraped from various online stores.

# Instructions:
# 1. Carefully analyze the user's question to understand their needs (e.g., product type, price range, specific features).
# 2. Scan the provided context to find relevant products that match the user's query.
# 3. Present the results in a clear and organized manner. Using a list or a table is highly recommended.
# 4. For each product, you must include its full name, price, and a direct, clickable URL.
# 5. Remain neutral and objective. Do not show any preference for one website over another. Your comparison should be based purely on the data available in the context.
# 6. If you cannot find any relevant products in the context to answer the user's question, simply state that you couldn't find any matching items based on the provided information. Do not make up products or information.

# Use the following pieces of context to answer the user's question.

# ----------------

# {context}
# {chat_history}
# Follow up question: """


# def get_prompt():
#     """
#     Generates a prompt for the conversational chain.

#     Returns:
#         ChatPromptTemplate: The configured prompt template.
#     """
#     prompt = ChatPromptTemplate(
#         input_variables=['context', 'question', 'chat_history'],
#         messages=[
#             SystemMessagePromptTemplate(
#                 prompt=PromptTemplate(
#                     input_variables=['context', 'chat_history'],
#                     template=system_prompt, template_format='f-string',
#                     validate_template=True
#                 ), additional_kwargs={}
#             ),
#             HumanMessagePromptTemplate(
#                 prompt=PromptTemplate(
#                     input_variables=['question'],
#                     template='{question}\nHelpful Answer:', template_format='f-string',
#                     validate_template=True
#                 ), additional_kwargs={}
#             )
#         ]
#     )
#     return prompt
#-------------------
from langchain.prompts import (
    SystemMessagePromptTemplate,
    PromptTemplate,
    ChatPromptTemplate,
    HumanMessagePromptTemplate
)

system_prompt = """You are an intelligent and precise shopping assistant. Your primary goal is to help users find products by ONLY using the information provided in the context below.

**CRITICAL INSTRUCTIONS:**
1.  You are strictly forbidden from inventing, hallucinating, or creating any information, especially product names and URLs.
2.  Your response MUST be based exclusively on the products and links found in the `context` section.
3.  If the context is empty or does not contain products matching the user's query, you MUST respond with: "I could not find any matching products in the provided information." Do not try to find alternatives or make suggestions.

**Your Task:**
1.  Analyze the user's question to understand their needs (e.g., 't-shirts under 500').
2.  Carefully search the provided `context` for relevant products that match the user's criteria.
3.  Present all matching products in a clear table format with the columns: "Full Name", "Price", and "URL".
4.  For the "URL" column, you MUST use the exact, full, and unmodified link as it appears in the context.
5.  **Crucially, sort the final table by price in ascending order (lowest to highest).**

Use the following pieces of context to answer the user's question.

----------------

{context}
{chat_history}
Follow up question: """


def get_prompt():
    """
    Generates a prompt for the conversational chain.

    Returns:
        ChatPromptTemplate: The configured prompt template.
    """
    prompt = ChatPromptTemplate(
        input_variables=['context', 'question', 'chat_history'],
        messages=[
            SystemMessagePromptTemplate(
                prompt=PromptTemplate(
                    input_variables=['context', 'chat_history'],
                    template=system_prompt, template_format='f-string',
                    validate_template=True
                ), additional_kwargs={}
            ),
            HumanMessagePromptTemplate(
                prompt=PromptTemplate(
                    input_variables=['question'],
                    template='{question}\nHelpful Answer:', template_format='f-string',
                    validate_template=True
                ), additional_kwargs={}
            )
        ]
    )
    return prompt