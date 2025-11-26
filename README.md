# Todo

- [ ] App should only add a single comment to idea with linked ideas + reasoning to avoid notification spam.
- [ ] Explore creating and attaching a note or document to the idea instead of commenting. We want to preserve tracability without cluttering comments etc.
- [ ] Make a Chrome extension POC which injects UI elements for users to trigger the automation.

# How to deploy:

1. Install Docker or equivalent.
2. Clone the repo.
3. In the root folder add a `.env` file with:
   - `WATSONX_PROJECT_ID` - The ID of a project in your watsonx.ai instance.
   - `WATSONX_URL` - The endpoint of your watsonx instance e.g. `https://us-south.ml.cloud.ibm.com`
   - `AHA_API_KEY` - Aha! API key
   - `IBM_IAM_API_KEY` - IBM Cloud API key
4. `sudo docker build . -t aha-app`
5. `sudo docker run -i --env-file .env aha-app`
6. When prompted in the console for an idea, enter `2046` to use the test idea created for this purpose.

# Prerequisites

1. Aha! API key
2. IBM Cloud API key
3. docker installed
4. watsonx.ai account

# About

- App to automatically find and link related Aha! Ideas.
- Uses LLM service (IBM watsonx) to analyse and compare ideas.
- Aha! API enables automatic linking of Aha! records i.e. linking similar ideas together.
- Automatically leaves a comment on Idea with LLM reasoning for why they're linked for transparency/explainability.

# Detailed flow

1. User (Product Manager) enters in the reference number of an Idea e.g. PRODUCT-I-{Ref_num}
2. App fetches all Ideas in Aha! from the given `created_since` date.
3. Loops through all Ideas individually, using an LLM to compare them with the user's specified Idea to see if the Ideas are related (i.e. same functionality request, overlapping theme, etc.)
4. If the Ideas are related, as determined by the LLM, the records are linked in Aha! so the user can easily see related ideas.
5. A comment is also submitted on the user's Idea, explaining which Ideas have been linked, and the rationale for doing so.
