from dotenv import load_dotenv
import requests
import os
from ibm_watsonx_ai import APIClient, Credentials
from ibm_watsonx_ai.foundation_models.inference import ModelInference
from ibm_watsonx_ai.foundation_models.schema import TextChatParameters
from Models.Idea import Idea
import json
from prompts import prompt


load_dotenv()

WATSONX_PROJECT_ID = os.environ.get("WATSONX_PROJECT_ID")
WATSONX_URL = os.environ.get("WATSONX_URL")
AHA_API_KEY = os.environ.get("AHA_API_KEY")
IBM_IAM_API_KEY = os.environ.get("IBM_IAM_API_KEY")


def main():
    idea_ref = input("Enter the reference number of the idea: ")
    idea = fetch_idea(idea_ref)
    print(f"The selected Idea is: \n{idea.id}\n{idea.name}")
    all_ideas: list[Idea] = []
    created_since = "2024-01-01 00:00:00"
    current_page = 1
    # loop through pages and each idea and store them in a variable
    while True:
        response = requests.get(
            f"http://bigblue.aha.io/api/v1/products/IRISCART/ideas/?per_page=200&page={current_page}&created_since={created_since}", headers={"Authorization": f"Bearer {AHA_API_KEY}"}).json()

        num_pages = response["pagination"]["total_pages"]
        print(f"The current page is: {current_page}")
        print(f"The total number pages is: {num_pages}")

        # add the ideas to the list
        for _idea in response["ideas"]:
            _idea = Idea(_idea["id"], _idea["reference_num"],
                         _idea["name"], _idea["description"]["body"])
            all_ideas.append(_idea)

        # increment page and check if valid
        current_page += 1
        if current_page > num_pages:
            break
    # send to llm for analysis and linking
    analyse_ideas(idea, all_ideas)


def fetch_idea(idea_ref: str) -> Idea:
    response = requests.get(f"http://bigblue.aha.io/api/v1/products/IRISCART/ideas/IRISCART-I-{idea_ref}",
                            headers={"Authorization": f"Bearer {AHA_API_KEY}"}).json()
    idea = Idea(response["idea"]["id"], response["idea"]["reference_num"],
                response["idea"]["name"], response["idea"]["description"])
    return idea


def analyse_ideas(subject_idea: Idea, ideas: list[Idea]):
    credentials = Credentials(
        url="https://us-south.ml.cloud.ibm.com",
        api_key=os.environ.get("IBM_IAM_API_KEY")
    )
    client = APIClient(
        credentials, project_id=WATSONX_PROJECT_ID)
    MODEL_ID = "openai/gpt-oss-120b"
    model = ModelInference(api_client=client, model_id=MODEL_ID, params=TextChatParameters(
        include_reasoning=False, seed=1, temperature=0, max_tokens=2000), persistent_connection=False)
    for idea in ideas:
        response = model.chat(
            messages=[
                {"role": "user", "content": prompt(subject_idea, idea)}
            ])
        print("\n")
        print(f"Analysing Idea: {ideas.index(idea)}")
        print("----------------------------")
        print(response)
        verdict: str = json.loads(
            response["choices"][0]["message"]["content"])["verdict"]
        print("----------------------------")
        print(f"LLM Verdict: {verdict}")
        print("\n")

        # if the ideas relate, link them + comment reasoning
        if "true" in verdict:
            reason: str = json.loads(
                response["choices"][0]["message"]["content"])["reason"]
            link_ideas(subject_idea, idea, reason)


def link_ideas(idea: Idea, idea_to_link: Idea, reason: str):
    # check if the ideas are the same record
    if idea.id == idea_to_link.id:
        return
    payload = {
        "record_link": {
            "record_type": "idea",
            "record_id": idea_to_link.id,
            "link_type": 10
        }
    }
    # Link the ideas
    requests.post(
        f"https://bigblue.aha.io/api/v1/ideas/{idea.id}/record_links", json=payload, headers={"Authorization": f"Bearer {AHA_API_KEY}"})

    # Add a comment to explain reasoning
    comment = {"comment": {
        "body": f"Comment by watsonx:\n I have linked <a href=\"https://bigblue.aha.io/ideas/{idea_to_link.ref}\">{idea_to_link.ref}</a> to this idea. Reasoning: {reason}"}}
    requests.post(
        f"https://bigblue.aha.io/api/v1/ideas/{idea.id}/comments", json=comment, headers={"Authorization": f"Bearer {AHA_API_KEY}"})

    print("""
        ------------------------------
        ------------------------------
                IDEAS LINKED!
        ------------------------------
        ------------------------------
        """)


main()
