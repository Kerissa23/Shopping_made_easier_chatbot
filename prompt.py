
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