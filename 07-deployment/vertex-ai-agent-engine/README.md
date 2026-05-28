---
adk_version: "1.28"
level: intermediate
languages: [python]
---

# Vertex AI Agent Engine

## Concept

Google's managed platform for deploying ADK agents. Handles scaling, authentication, monitoring, and API management. The simplest path to production on GCP.

## Deployment

```bash
# Install the Vertex AI SDK
pip install google-cloud-aiplatform

# Deploy your agent
gcloud ai agents deploy \
    --agent=./agent.py \
    --display-name="customer-support" \
    --region=us-central1 \
    --service-account=agent-sa@project.iam.gserviceaccount.com
```

## Agent Configuration

```python
# agent.py — deployable to Vertex AI
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
import vertexai

vertexai.init(project="my-project", location="us-central1")

agent = Agent(
    name="customer-support",
    model="gemini-2.5-flash",
    instruction="You are a customer support agent for an e-commerce platform.",
    tools=[
        FunctionTool(lookup_order),
        FunctionTool(process_return),
        FunctionTool(check_inventory),
    ],
)

# Vertex AI requires this entrypoint
def create_agent():
    return agent
```

## Calling the Deployed Agent

```python
from google.cloud import aiplatform

endpoint = aiplatform.AgentEndpoint(
    agent_name="projects/my-project/locations/us-central1/agents/customer-support",
)

response = endpoint.predict(
    instances=[{"input": "Where is my order #12345?"}],
    parameters={"session_id": "user-789"},
)

print(response.predictions[0])
```

## Vertex AI vs Self-Hosted

| | Vertex AI | Self-Hosted (GKE/Cloud Run) |
|---|---|---|
| **Setup time** | 5 minutes | Days |
| **Auto-scaling** | Built-in | Manual config |
| **Auth** | IAM, built-in | DIY with API gateway |
| **Monitoring** | Integrated with Cloud Monitoring | DIY with OTel+LGTM |
| **Cost** | Per-request + model | Per-resource |
| **Vendor lock-in** | High | Low |
| **Custom models** | Gemini only | Any (LiteLLM) |

## Pitfalls

- **Region availability**: Vertex AI Agent Engine is not available in all regions. Deploy in `us-central1` or `europe-west4`.
- **Cold start**: First request after deployment takes 30-60s. Warm-up requests or keep-alive pings mitigate this.
- **Cost opacity**: Vertex AI bundles agent runtime + LLM costs. Hard to separate for cost attribution. Export billing data to BigQuery for granular analysis.
