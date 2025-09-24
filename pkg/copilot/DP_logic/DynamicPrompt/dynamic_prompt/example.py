from prompt_builder import PromptBuilder
from retriever import Retriever

question = "What is the average CPU usage over the past 6 hours?"
retriever = Retriever()
context = retriever.query(question)

prompt = PromptBuilder() \
    .with_context(context) \
    .with_user_question(question) \
    .with_overrides() \
    .with_golden_examples() \
    .with_additional_info() \
    .build()

print(prompt)