from Models.Idea import Idea


def strict_prompt(subject_idea: Idea, idea_to_compare: Idea):
    return (f"""
Goal: You are a helpful assistant. You help Product Managers on IBM Cloud Pak for AIOps to relate Idea submissions made via Aha!(Product Management software) so that they can find related and similar ideas together.
Task: You will be given an idea to compare with another idea. Your job is to decide whether the ideas relate to the same thing in the product, such as the same are, the same UX, the same concept, the same feature, or are essentially equivalent ideas. You should be strict about deciding whether or not ideas can be considered as related. The ideas should describe the same opportunity, user need, or problem. Avoid weak correlations where there is only slight overlap in the ideas. We want to find strong signals that an Idea is worth pursuing.
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


def loose_prompt(subject_idea: Idea, idea_to_compare: Idea):
    return (f"""
Goal: You are a helpful assistant. You help Product Managers on IBM Cloud Pak for AIOps to relate Idea submissions made via Aha!(Product Management software) so that they can find related and similar ideas together.
Task: You will be given an idea to compare with another idea. Your job is to decide whether the ideas relate to the same thing in the product, such as the same are, the same UX, the same concept, the same feature, or are essentially equivalent ideas. The outcome is to help Product Managers triage Ideas and gather the full picture, taking into account any similar or related ideas when doing so. You should be somewhat loose in how you determine if ideas are related. Ideas could be considered related if they simply have overlapping themes and relate to the same area of the product, domain or user job to be done.
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
I want to be able to integrate servicenow with AIOps so I can send change records to AIOps to use as context for incidents and alerts.

Output: {{"verdict": "true", "reason":"[a brief explanation as to why you returned a verdict of true]"}}
Explanation for context: While these ideas don't refer to exactly the same type of capability, they both relate to change management and using such data in the context of incident management, therefore you should return a true verdict in cases like this.
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


def recommendations_prompt(idea: Idea, linked_ideas: str):
    return (f"""
Goal: You are a helpful assistant. You help Product Managers on IBM Cloud Pak for AIOps to generate actionable product recommendations based on Idea submissions made via Aha! (Product Management software). Your task is to review a primary idea and a set of linked or related ideas, then provide concrete, product-specific recommendations that could inform the roadmap, backlog, or feature prioritization.

Context:
IBM Cloud Pak for AIOps is an AI-driven operations platform that helps IT Operations teams detect, diagnose, and resolve incidents across hybrid cloud environments. It includes components such as:
- Event Manager (Alert and Incident Management)
- Metric and Log Anomaly Detection
- Runbook Automation (with integration to Watson Orchestrate and RBA)
- Topology and Dependency Mapping
- Integrations with external systems (ServiceNow, Instana, Turbonomic, etc.)
- AI Model Management and Training Pipelines
- Policy-based Noise Reduction and Correlation

Task:
Given an Aha! Idea and a list of related or linked ideas, analyze them collectively and produce specific recommendations for Product Management. Focus on how these ideas could influence the AIOps product, such as new capabilities, UX improvements, integrations, or enhancements to AI-driven automation. Format your output in plain text - no markup, no html.

Your recommendations should:
- Be **specific to Cloud Pak for AIOps** (avoid generic SaaS or IT advice)
- Reference relevant product areas (e.g., Event Grouping, Change Risk Prediction, Runbook Automation)
- Identify **themes or opportunities** (e.g., “Improved ServiceNow integration for change-event correlation”)
- Suggest **potential actions** (e.g., “Explore unified UI for topology and incident visualization”)
- Avoid repeating the input ideas verbatim—synthesize insights instead

Expected response format:
{{
  "themes": [
    "brief summary of 2-3 key themes that emerge from the ideas"
  ],
  "recommendations": [
    "specific, actionable product recommendations related to IBM Cloud Pak for AIOps",
    "each recommendation should be relevant to AIOps capabilities or user workflows"
  ]
}}

<example>
Here is the subject idea:
AIOps should automatically correlate ServiceNow change records with alerts to reduce noise from planned maintenance

Here are the linked ideas:
- AIOps should detect planned outages and suppress alerts during them
- Integrate ServiceNow Change Management with AIOps so that incidents are enriched with change context
- Provide a UI to visualize which alerts are linked to change events

Output:
{{
  "themes": [
    "Change-aware incident correlation",
    "Noise suppression during planned maintenance"
  ],
  "recommendations": [
    "Introduce a 'Change Awareness' module that leverages ServiceNow change events to enhance alert correlation and root cause identification.",
    "Develop a maintenance window management capability integrated with topology and event pipelines to automatically suppress alerts during approved changes.",
    "Enhance the AIOps UI to visualize change-event relationships within incident timelines."
  ]
}}
</example>

Here is the subject idea:
{idea.name}\n{idea.description}

Here are the linked ideas:
{linked_ideas}
"""
    )
