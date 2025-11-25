import logging
import requests

logger = logging.getLogger(__name__)


def get_minutes_of_meeting(conversation):
    def create_overlapping_chunks(text, chunk_size=500, overlap=50):
        words = text.split()
        chunks = []
        start = 0

        while start < len(words):
            end = min(start + chunk_size, len(words))
            chunk = " ".join(words[start:end])
            chunks.append(chunk)
            start += chunk_size - overlap

        return chunks

    def generate_summary(chunk):
        url = "http://localhost:11434/api/generate"

        prompt = """The conversation is given below:
        ======
        {conversation}
        ======

        You are provided with the above conversation. Try to infer speaker labels. Develop a comprehensive summary points using the following Instructions given below.

        ### Instructions Begin ###
        1. You will analyse the part of conversation and provide me comprehensive summary in bullet points.
        2. You will stick to the facts of the conversations and ensure all points are clear and thorough.
        3. If any part of the conversation is unclear, think step by step based on the context of the conversation, and then try to summarize it.
        4. Provide a thorough capture of the information captured. Capture all key points and concluding statements.
        5. Make sure you capture all key themes
        6. Never add points that were not discussed in the initial conversation
        ### Instructions End ###

        Generate a comprehensive bullet point based summary using the above conversation and Instructions."""

        payload = {
            "model": "llama3.2",
            "prompt": prompt.format(conversation=chunk),
            "stream": False,
        }

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json()["response"]
        except requests.exceptions.RequestException as e:
            print(f"Error calling Ollama API: {str(e)}")
            raise

    try:
        chunks = create_overlapping_chunks(conversation)
        summaries = []

        for i, chunk in enumerate(chunks):
            print(f"Processing chunk {i + 1}/{len(chunks)}")
            summary = generate_summary(chunk)
            print(f"Summary: {summary}")
            summaries.append(summary)

        if len(summaries) > 1:
            combined_text = "\n\n".join(summaries)
            final_summary = combined_text
        else:
            final_summary = summaries[0]

        return final_summary

    except Exception:
        logger.exception("Error in summarization")
        raise
