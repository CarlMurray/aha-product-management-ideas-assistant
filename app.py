from dotenv import load_dotenv
import requests
import os
from ibm_watsonx_ai import APIClient, Credentials
from ibm_watsonx_ai.foundation_models.inference import ModelInference
from ibm_watsonx_ai.foundation_models.schema import TextChatParameters
from Models.Idea import Idea
import json
from prompts import strict_prompt, loose_prompt, recommendations_prompt


load_dotenv()

WATSONX_PROJECT_ID = os.environ.get("WATSONX_PROJECT_ID")
WATSONX_URL = os.environ.get("WATSONX_URL")
AHA_API_KEY = os.environ.get("AHA_API_KEY")
IBM_IAM_API_KEY = os.environ.get("IBM_IAM_API_KEY")


def main():
    global prompt
    idea_ref = input("Enter the reference number of the idea: ")
    prompt_type = input(
        "How strict do you want idea correlation? (strict or loose)")
    if prompt_type == "loose":
        prompt = loose_prompt
    else:
        prompt = strict_prompt
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
    linked_ideas: list[Idea] = []
    comment: str = """
        <strong>Comment by watsonx</strong>
        <h3>I have linked the following ideas to this one:</h3>
        """
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
        if ("true" in verdict) | (verdict == True):
            reason: str = json.loads(
                response["choices"][0]["message"]["content"])["reason"]
            link_ideas(subject_idea, idea, reason)
            linked_ideas.append(idea)
            comment += f"""<div><strong><a href="https://bigblue.aha.io/ideas/ideas/{idea.ref}">{idea.ref}</a> | {idea.name}</strong></div><div><span>{idea.description}</span></div><p><strong>Reasoning:</strong> {reason}</p><hr>"""
    rec_response = write_recommendations(subject_idea, linked_ideas, model)
    comment += f"""<h3>Here are some recommendations:</h3>"""
    comment += "<p><strong>Themes</strong></p>"
    comment += "<ol>"
    for theme in rec_response["themes"]:
        comment += f"<li>{theme}</li>"
    comment += "</ol>"
    comment += "<br>"
    comment += "<p><strong>Recommendations</strong></p>"
    comment += "<ol>"
    for rec in rec_response["recommendations"]:
        comment += f"<li>{rec}</li>"
    comment += "</ol>"
    write_comment(comment, subject_idea)


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

    print("""
        ------------------------------
        ------------------------------
                IDEAS LINKED!
        ------------------------------
        ------------------------------
        """)


def write_recommendations(subject_idea: Idea, linked_ideas: list[Idea], model: ModelInference):
    dict_ideas: list[dict] = []
    for i in linked_ideas:
        dict_ideas.append(i.__dict__)
    response = model.chat(
        messages=[
            {"role": "user", "content": recommendations_prompt(
                subject_idea, json.dumps(dict_ideas))}
        ])
    # tied to llm response format
    print(response)
    themes = json.loads(response["choices"][0]["message"]["content"])["themes"]
    # tied to llm response format
    recommendations = json.loads(response["choices"][0]["message"]["content"])[
        "recommendations"]
    return {"themes": themes, "recommendations": recommendations}


def write_comment(comment: str, subject_idea: Idea):
    body = {"comment": {
        "body": comment}}
    requests.post(
        f"https://bigblue.aha.io/api/v1/ideas/{subject_idea.id}/comments", json=body, headers={"Authorization": f"Bearer {AHA_API_KEY}"})


main()
