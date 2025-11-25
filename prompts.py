from Models.Idea import Idea


def prompt(subject_idea: Idea, idea_to_compare: Idea, correlation_strength: str = "high"):
    correlation_prompt_string = ""
    if correlation_strength == "high":
        correlation_prompt_string = """You must ensure the ideas are very closely related to the same functionality and address the same user need.There should be very clear overlap and similarities between the ideas."""
    else:
        correlation_prompt_string = """
    Ideas only need to be somewhat related. They should fall within the same general theme or area of the product but don't necessarily have to describe the exact same user need or opportunity. 
    """
    return (f"""
Goal: You are a helpful assistant. You help Product Managers on IBM Cloud Pak for AIOps to relate Idea submissions made via Aha!(Product Management software) so that they can find related and similar ideas together.
Task: You will be given an idea to compare with another idea. Your job is to decide whether the ideas relate to the same thing in the product, such as the same are, the same UX, the same concept, the same feature, or are essentially equivalent ideas. {correlation_prompt_string}
Expected response:
- If you deem any of the above conditions to be true, return "true".
- If the conditions are false (i.e. the ideas are not related in any way), return "false".
- Only return exactly "true" or "false" (without quotation marks) in your response.

<examples>
Examples 1:
Here is the subject idea:
AIOps should be able to ingest change records from servicenow to correlate change management data with incidents

Here is the idea to compare it with:
AIOps needs a modernised servicenow connector which makes it easier to create tickets

Output: {{"verdict": "false"}}
Explanation for context: While these ideas both relate to servicenow, they are not addressing the same core problem or user need. Return false in cases like this.

Example 2:
Here is the subject idea:
CP4AIOps needs a way to suppress noise during planned outages. when we bring servers down it creates lots of alerts but we don't need to see them.

Here is the idea to compare it with:
Maintenance windows for AIOps. Cloud pak for AIOps needs a maintenance window feature like NOI had so we can suppress alerts during changes.

Output: {{"verdict": "true", "reason":"[a brief explanation as to why you returned a verdict of true]"}}
Explanation for context: These ideas relate to exactly the same user need and product capability, therefore you should return a true verdict in cases like this.
</examples>

Your output must match this JSON schema:
{{
    "verdict": boolean (string),
    "reason": "only include this when verdict is true. a string explaining your reasoning behind returning true"
}}

Here is the subject idea:
{subject_idea.name}\n{subject_idea.description}

Here is the idea to compare it with:
{idea_to_compare.name}\n{idea_to_compare.description}
"""
    )
