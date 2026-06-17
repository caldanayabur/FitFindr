# FitFindr — planning.md

> Complete this document before writing any implementation code.
> Your spec and agent diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Your planning.md will be reviewed as part of your submission.
> Update it before starting any stretch features.

---

## Tools

List every tool your agent will use. For each tool, fill in all four fields.
You must have at least 3 tools. The three required tools are listed — add any additional tools below them.

### Tool 1: search_listings

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->
Searches the mock listings dataset for items matching the description, optional size, and optional maximum price provided by the user. Returns a list of matching listing dictionaries, sorted by relevance (best match first) and returns an empty list if nothing matches.

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `description` (str): This is the text description of the listed item.
- `size` (str): The size category of the item (e.g., "W30 L30", "M").
- `max_price` (float): The maximum price the user is willing to pay for the item.

**What it returns:**
<!-- Describe the return value — what fields does a result contain? -->
Each listing dictionary contains the following fields: "id", "title", "description", "category", "style_tags" (list), "size", "condition", "price" (float), "colors" (list), "brand", "platform".

**What happens if it fails or returns nothing:**
<!-- What should the agent do if no listings match? -->
Returns an empty list if nothing matches.
---

### Tool 2: suggest_outfit

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->
It takes a new item (the one the user is interested in) and the user's existing wardrobe, and suggests 1-2 complete outfits that incorporate the new item.

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `new_item` (dict): A listed item dictionary that the user is interested in styling.
- `wardrobe` (dict): The user’s wardrobe, structured as a dictionary with an "items" list, where each item includes id, name, category, colors, style_tags, and optional notes.

**What it returns:**
<!-- Describe the return value -->
It returns a non-empty string of an outfit suggestion that styles the new item with pieces form the user's wardrobe.

**What happens if it fails or returns nothing:**
<!-- What should the agent do if the wardrobe is empty or no outfit can be suggested? -->
If the wardrobe is empty, it offers general styling advice for the item.

---

### Tool 3: create_fit_card

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->
Generates a short, shareable description of a complete outfit, the kind you might post on Instagram/TikTok.

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `outfit` (str): The string from suggest_outfit that describes the complete outfit, including the new item and how it’s styled with pieces from the user’s wardrobe.
- `new_item` (dict): The listed item dictionary that the user is interested in styling, which is the centerpiece of the outfit.

**What it returns:**
<!-- Describe the return value -->
It returns a 2–4 sentence string usable as an Instagram/TikTok caption.

**What happens if it fails or returns nothing:**
<!-- What should the agent do if the outfit data is incomplete? -->
If outfit is empty or missing, the agent returns a descriptive error message string.
---

### Additional Tools (if any)

<!-- Copy the block above for any tools beyond the required three -->

---

## Planning Loop

**How does your agent decide which tool to call next?**
<!-- Describe the logic your planning loop uses. What does it look at? What conditions change its behavior? How does it know when it's done? -->
The agent starts by initializing the session using _new_session().

Next, it parses the user query to extract three pieces of information: description, size, and max_price. This is done using simple string matching and splitting. For example, it looks for "under $" to find the maximum price and "size" to find the size. The rest of the query is treated as the description. The parsed values are stored in session["parsed"].

The agent then calls the search_listings() tool using these parsed parameters. The results (a list of matching items) are stored in session["search_results"].

If search_listings() returns an empty list, the agent determines that no items match the user’s request. In this case, it sets session["error"] to a helpful message and stops the process early, returning the session without calling any other tools.

If the search returns results, the agent selects the top item from the list (the best match) and stores it in session["selected_item"].

Next, the agent calls suggest_outfit() using the selected_item and the wardrobe. The generated outfit suggestion is stored in session["outfit_suggestion"].

After that, the agent calls create_fit_card() using the outfit suggestion and the selected item. The resulting fit card is stored in session["fit_card"].

The process is complete after the fit card is created, and the agent returns the final session.

---

## State Management

**How does information from one tool get passed to the next?**
<!-- Describe how your agent stores and accesses state within a session. What data is tracked? How is it passed between tool calls? -->

The agent uses a session dictionary to store and share information between steps. Each piece of data is saved under a specific key and reused by later tool calls.

After parsing the query, the extracted values (description, size, max_price) are stored in session["parsed"]. These values are then passed as inputs to the search_listings() tool.

The results from search_listings() are stored in session["search_results"]. This is a list of matching items. The agent then selects the top item from this list and stores it in session["selected_item"].

The selected_item is passed as input to the suggest_outfit() tool, along with the wardrobe. The resulting outfit suggestion is stored in session["outfit_suggestion"].

Finally, the outfit_suggestion and selected_item are passed to create_fit_card(), and the result is stored in session["fit_card"].

---

## Error Handling

For each tool, describe the specific failure mode you're handling and what the agent does in response.

| Tool | Failure mode | Agent response |
|------|-------------|----------------|
| search_listings | No results match the query | The agent sets session["error"] to a helpful message (e.g., "No listings found matching your criteria. Try adjusting your search.") and stops the process early without calling any further tools. |
| suggest_outfit | Wardrobe is empty | The agent still calls suggest_outfit(), but the tool may return a limited or empty outfit suggestion. The agent can include a message indicating that the wardrobe is empty and suggest adding items. |
| create_fit_card | Outfit input is missing or incomplete | The agent sets session["error"] to a message indicating that a valid outfit could not be generated and stops the process without creating a fit card. |

---

## Architecture

<!-- Draw a diagram of your agent showing how the components connect:
     User input → Planning Loop → Tools (search_listings, suggest_outfit, create_fit_card)
                                                                          ↕
                                                                   State / Session
     Show what triggers each tool, how state flows between them, and where error paths branch off.
     ASCII art, a Mermaid diagram (https://mermaid.js.org/syntax/flowchart.html), or an embedded
     sketch are all fine. You'll share this diagram with an AI tool when asking it to implement
     the planning loop and each individual tool. -->

User Query
    │
    ▼
Planning Loop ───────────────────────────────────────────────┐
    │                                                        │
    │  Parse query → session["parsed"]                       │
    │                                                        │
    ├─► search_listings(description, size, max_price)        │
    │       │                                                │
    │       ▼                                                │
    │   session["search_results"] = [items...]               │
    │       │                                                │
    │       ├─► if empty →                                   │
    │       │      session["error"] = "No listings found"    │
    │       │      ▼                                         │
    │       │   RETURN session (STOP)                        │
    │       │                                                │
    │       ▼                                                │
    │   session["selected_item"] = results[0]                │
    │                                                        │
    ├─► suggest_outfit(selected_item, wardrobe)              │
    │       │                                                │
    │       ▼                                                │
    │   session["outfit_suggestion"] = {...}                 │
    │                                                        │
    │       ├─► if wardrobe empty → (continue with fallback) │
    │                                                        │
    └─► create_fit_card(outfit_suggestion, selected_item)    │
            │                                                │
            ├─► if missing input →                           │
            │      session["error"] = "Invalid outfit"       │
            │      ▼                                         │
            │   RETURN session (STOP)                        │
            │                                                │
            ▼                                                │
        session["fit_card"] = {...}                          │
            │                                                │
            ▼                                                │
        RETURN session (DONE) ◄──────────────────────────────┘

---

## AI Tool Plan

<!-- For each part of the implementation below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, your agent diagram)
     - What you expect it to produce
     - How you'll verify the output matches your spec before moving on

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Tool 1 spec (inputs, return value, failure mode) and ask it to implement
     search_listings() using load_listings() from the data loader — then test it against 3 queries
     before trusting it" is a plan. -->

**Milestone 3 — Individual tool implementations:**


**Milestone 4 — Planning loop and state management:**

---

## A Complete Interaction (Step by Step)

Write out what a full user interaction looks like from start to finish — tool call by tool call. Use a specific example query.

**Example user query:** "I'm looking for a vintage graphic tee under $30. I mostly wear baggy jeans and chunky sneakers. What's out there and how would I style it?"

**Step 1:**
<!-- What does the agent do first? Which tool is called? With what input? -->

**Step 2:**
<!-- What happens next? What was returned from step 1? What tool is called now? -->

**Step 3:**
<!-- Continue until the full interaction is complete -->

**Final output to user:**
<!-- What does the user actually see at the end? -->
