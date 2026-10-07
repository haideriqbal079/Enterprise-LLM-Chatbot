from src.llm.groq_service import GroqService
from src.okf.loader import search_documents
from src.prompts.templates import build_prompt


questions = [
    "Who is the CEO of Try Soft AI?",
    "When was Try Soft AI founded?",
    "What are the working hours of Try Soft AI?",
    "What services does Try Soft AI provide?",
    "Who is the CFO of Try Soft AI?",
]


groq_service = GroqService()


for question in questions:
    print("\n" + "#" * 70)
    print(f"QUESTION: {question}")
    print("#" * 70)

    documents = search_documents(question)

    knowledge_context = "\n\n".join(
        document["content"]
        for document in documents
    )

    for prompt_type in ["concise", "grounded", "structured"]:
        prompt = build_prompt(
            prompt_type,
            knowledge_context,
            question,
        )

        response = groq_service.generate_response(prompt)

        print("\n" + "=" * 60)
        print(f"PROMPT: {prompt_type.upper()}")
        print("=" * 60)
        print(response)