# TravelBuddy

A friendly console travel agent that guides a weekend getaway through **trip type → accommodation → activity**, with exactly three choices per step. Mountain trips get mountain activities, beach trips get coastal activities, and city breaks get city activities.

## Setup and run

Follow the parent [setup instructions](../README.md), including your OpenRouter API key. From the repository root:

```powershell
.venv\Scripts\python -m travel_buddy
```

`OPENROUTER_MODEL` defaults to the assignment's `meta-llama/llama-3-8b-instruct`. If unavailable or temporarily rate limited, the client tries `OPENROUTER_FALLBACK_MODEL`, defaulting to OpenRouter's free-model router `openrouter/free`. Availability and quotas depend on the provider. A different available free model ID can be configured in `.env` without changing code.

## Example conversation

Illustrative transcript (the application owns menu wording):

```text
TravelBuddy: Hi, I'm TravelBuddy! Let's plan an amazing weekend getaway.
Let's choose your trip type!
1. Beach
2. Mountains
3. City break
You: Mountains
TravelBuddy: Great choice!
Let's choose your accommodation!
1. Cozy guesthouse
2. Boutique hotel
3. Camping
You: I want to stay on the Moon
TravelBuddy: No worries! Please choose one of the options below, or describe it another way.
[The same accommodation menu is shown.]
You: 1
TravelBuddy: Great choice!
Let's choose your activity!
1. Scenic hiking
2. Wildlife watching
3. Stargazing
You: I'd love to look at the stars
TravelBuddy: Great choice!
Your weekend getaway is ready!
Trip: Mountains
Stay: Cozy guesthouse
Activity: Stargazing
Have a wonderful adventure! Type restart to plan another trip, or exit to leave.
You: exit
TravelBuddy: Goodbye! Safe travels and happy adventures!
```

## Decisions

- A small explicit state machine controls valid options and the final itinerary. OpenRouter interprets natural language; its JSON selection is validated before advancing. This prevents invented activities or malformed LLM output from corrupting state.
- The full in-memory user/assistant history is sent with each model request, alongside confirmed choices and the current step. History lasts for the current process/web session.
- Numbered answers and exact labels are accepted locally for instant navigation. Natural-language preferences go through OpenRouter with the complete conversation context. Invalid or ambiguous responses repeat the current menu; service failures preserve all confirmed choices.
- `exit` is handled before the API call, so users can always leave. `restart` starts a new itinerary in the same conversation; the UI's new-trip button creates a fresh conversation.
- Friendly menu text is deterministic so that the three-option requirement stays reliable. The optional web UI adds back navigation, a readable itinerary, and a downloadable plan. Back navigation removes only the latest confirmed choice and records the change in conversation history.

## Live acceptance checklist

1. Run a full Mountains → Cozy guesthouse → Stargazing conversation.
2. Try the Moon answer during accommodation; confirm it stays on accommodation.
3. Try a natural paraphrase and numbered answers.
4. Complete Beach and City break trips and confirm their activities fit.
5. Type `exit` at the first and middle steps; confirm clean termination.
6. Try an invalid API key; confirm a readable error and no lost choices.

The optional web UI uses this same bot: run `python -m streamlit run web_app.py` from the repository root.
