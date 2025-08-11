from langchain.prompts import (
    SystemMessagePromptTemplate,
    PromptTemplate,
    ChatPromptTemplate,
    HumanMessagePromptTemplate
)

# --- NEW, SIMPLIFIED PROMPT ---
system_prompt = """You are a precise formatting assistant. Your ONLY job is to take the list of products provided in the `context` section and format them into a clean markdown table.

**CRITICAL INSTRUCTIONS:**
1. Use ONLY the products and links exactly as provided in the `context` section. Do not filter, modify, or remove any products for ANY reason.
2. Present ALL products exactly as provided.
3. The final table MUST have the columns: "Full Name", "Price", and "URL".
4. For the "URL" column, use the exact, full, and unmodified link from the context.
5. Sort the table by price in ascending order (lowest to highest).
6. Do NOT interpret or apply any filtering based on the user query — trust the scraper results as final.

Use the following pieces of context to create the response.

----------------

{context}
"""


def get_prompt():
    """
    Generates a prompt for the conversational chain. This version is for formatting only.
    """
    prompt = ChatPromptTemplate(
        input_variables=['context', 'question'],
        messages=[
            SystemMessagePromptTemplate(
                prompt=PromptTemplate(
                    input_variables=['context'],
                    template=system_prompt, template_format='f-string',
                    validate_template=True
                )
            ),
            # The human message is now simpler, as the system prompt does all the work.
            HumanMessagePromptTemplate(
                prompt=PromptTemplate(
                    input_variables=['question'],
                    template='Please present the products for my request: "{question}"',
                    template_format='f-string',
                    validate_template=True
                )
            )
        ]
    )
    return prompt