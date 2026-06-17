# FitFindr

FitFindr is an AI agent that helps users find secondhand clothing and style it. Given a natural language query, it searches a mock dataset of thrifted listings, picks the best match, suggests outfits using the user's wardrobe, and generates a shareable caption — all in a fixed planning loop.

## Video Walkthrough

https://github.com/user-attachments/assets/47412272-76fa-4881-8158-7a51f7ccc2dc

## Setup

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project root with your Groq API key:

```
GROQ_API_KEY=your_key_here
```

Run the app:

```bash
python app.py
```

---

## Tool Inventory

### Tool 1: `search_listings`

**Purpose:** Searches the mock listings dataset for items matching the description, optional size, and optional maximum price provided by the user. Returns a list of matching listing dictionaries, sorted by relevance (best match first), and returns an empty list if nothing matches.

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `description` | `str` | The text description of what the user is looking for (e.g., `"vintage graphic tee"`). |
| `size` | `str \| None` | The size category of the item (e.g., `"M"`, `"W30 L30"`). `None` skips size filtering. Matching is case-insensitive substring. |
| `max_price` | `float \| None` | The maximum price the user is willing to pay (inclusive). `None` skips price filtering. |

**Output:** Each listing dictionary contains the following fields: `id`, `title`, `description`, `category`, `style_tags` (list), `size`, `condition`, `price` (float), `colors` (list), `brand`, `platform`. Returns an empty list if nothing matches.

---

### Tool 2: `suggest_outfit`

**Purpose:** It takes a new item (the one the user is interested in) and the user's existing wardrobe, and suggests 1–2 complete outfits that incorporate the new item.

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `new_item` | `dict` | A listing dictionary for the item the user is considering buying. |
| `wardrobe` | `dict` | The user's wardrobe, structured as a dictionary with an `"items"` key containing a list of wardrobe item dicts (each with `id`, `name`, `category`, `colors`, `style_tags`, optional `notes`). |

**Output:** It returns a non-empty string of an outfit suggestion that styles the new item with pieces from the user's wardrobe. If the wardrobe is empty, the LLM gives general styling advice for the item instead.

---

### Tool 3: `create_fit_card`

**Purpose:** Generates a short, shareable description of a complete outfit — the kind you might post on Instagram or TikTok.

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `outfit` | `str` | The outfit suggestion string returned by `suggest_outfit`, describing how the new item is styled with wardrobe pieces. |
| `new_item` | `dict` | The listing dictionary for the thrifted item, which provides the title, price, and platform for the caption. |

**Output:** A 2–4 sentence string written like a real OOTD post — casual, specific, and authentic. It naturally mentions the item name, price, and platform once each. If `outfit` is empty or whitespace-only, it returns a descriptive error message string without raising an exception.

---

## Planning Loop

The agent starts by initializing the session using `_new_session()`.

Next, it parses the user query to extract three pieces of information: description, size, and max_price. It uses regex to do this — looking for `"under $X"` to find the maximum price and `"size X"` to find the size. The rest of the query becomes the description. The parsed values are stored in `session["parsed"]`.

The agent then calls `search_listings()` using the parsed parameters. The results are stored in `session["search_results"]`. If the list is empty, the agent sets `session["error"]` to a helpful message and returns early — `suggest_outfit` is never called.

If the search returns results, the agent selects the top item from the list and stores it in `session["selected_item"]`.

Next, it calls `suggest_outfit()` using the selected item and the user's wardrobe. The outfit suggestion is stored in `session["outfit_suggestion"]`.

After that, it calls `create_fit_card()` using the outfit suggestion and the selected item. The result is stored in `session["fit_card"]`.

The process is complete after the fit card is created, and the agent returns the final session. It does not loop back or retry — each step runs exactly once and either completes or stops early with an error.

---

## State Management

The agent uses a session dictionary to store and share information between steps. Each piece of data is saved under a specific key and reused by later tool calls.

After parsing the query, the extracted values (description, size, max_price) are stored in `session["parsed"]` and passed as inputs to `search_listings()`.

The results from `search_listings()` are stored in `session["search_results"]`. The agent then selects the top item from this list and stores it in `session["selected_item"]`.

The selected item is passed as input to `suggest_outfit()`, along with the wardrobe. The resulting outfit suggestion is stored in `session["outfit_suggestion"]`.

Finally, the outfit suggestion and selected item are passed to `create_fit_card()`, and the result is stored in `session["fit_card"]`.

| Key | Written by | Read by |
|-----|-----------|---------|
| `session["query"]` | `_new_session` | reference only |
| `session["parsed"]` | Step 2 (query parsing) | Step 3 (`search_listings`) |
| `session["search_results"]` | Step 3 | Step 4 (top-item selection) |
| `session["selected_item"]` | Step 4 | Steps 5 and 6 |
| `session["wardrobe"]` | `_new_session` | Step 5 (`suggest_outfit`) |
| `session["outfit_suggestion"]` | Step 5 | Step 6 (`create_fit_card`) |
| `session["fit_card"]` | Step 6 | Gradio output |
| `session["error"]` | Steps 3 or 6 (failure paths) | `handle_query` in `app.py` |

Nothing is passed between functions directly as arguments beyond what the function spec requires — all intermediate results live in the session dict.

---

## Error Handling

For each tool, describe the specific failure mode you're handling and what the agent does in response.

| Tool | Failure mode | Agent response |
|------|-------------|----------------|
| search_listings | No results match the query | The agent returned the following message: "No listings found matching your criteria. Try broadening your search or adjusting the size or price." |
| suggest_outfit | Wardrobe is empty | The agent returned the following message:<br><br>"You've found a cute thrifted gem. That Y2K baby tee with a butterfly print is perfect for anyone who loves a nostalgic, playful vibe. Since it's a graphic tee, it's pretty versatile, but I'd say it pairs really well with pieces that complement its sweet, feminine aesthetic.<br><br>For a head-to-toe look, you could pair this tee with some high-waisted jeans or a flowy skirt in a neutral color like beige, white, or light blue. The white, pink, and purple hues in the butterfly print will add a pop of color to your outfit, so you can keep the rest of your look relatively simple. If you want to lean into the cottagecore style tag, you could throw on a pair of distressed denim shorts and some sneakers for a casual, laid-back look.<br><br>To add some extra flair to your outfit, consider layering a cardigan or a kimono over the tee. A pastel-colored cardigan would be a great match, as it'll enhance the soft, dreamy quality of the butterfly print. You could also add a wide-brimmed hat, a choker, or a pair of layered necklaces to give your look a more bohemian feel.<br><br>In terms of shoes, you've got a few options. Sneakers are a great choice for a casual look, but you could also wear ankle boots or sandals to dress it up slightly. The goal is to balance the sweetness of the butterfly print with more grounded pieces.<br><br>Since you don't have a wardrobe on file yet, this tee could be a great starting point for building a new aesthetic. You could use it as an anchor piece and add other items that fit the Y2K or cottagecore vibe." |
| create_fit_card | Outfit input is missing or incomplete | The agent sets session["error"] to: "Error: no outfit suggestion available — run suggest_outfit first to generate outfit ideas." |


**Concrete testing examples:**

- **`search_listings` — no results:** Running `search_listings("designer ballgown", size="XXS", max_price=5)` returned `[]` because no listing in the dataset costs under $5. The unit test `test_search_empty_results` confirms this returns an empty list and does not raise. In `run_agent`, a follow-up test with the query `"designer ballgown size XXS under $5"` confirmed that `session["error"]` was set and `session["outfit_suggestion"]` remained `None`.

- **`suggest_outfit` — empty wardrobe:** Running `suggest_outfit(SAMPLE_ITEM, {"items": []})` (mocked LLM) returned a non-empty styling paragraph. The test also covers a wardrobe dict with no `"items"` key at all (`{}`), which the tool handles via `.get("items", [])` — also confirmed by `test_suggest_outfit_missing_items_key`.

- **`create_fit_card` — empty outfit:** Calling `create_fit_card("", SAMPLE_ITEM)` and `create_fit_card("   ", SAMPLE_ITEM)` both returned the error message string. Neither raised an exception. Both are covered by `test_create_fit_card_empty_outfit` and `test_create_fit_card_whitespace_outfit`.

---

## Spec Reflection

The overall architecture matched the plan exactly — three tools, a linear planning loop, a session dict for state, and early return on empty search results.

One thing that changed: the planning doc described query parsing as "simple string matching and splitting." The actual implementation uses `re.search()` with patterns for `"under $X"` and `"size X"`, then strips those clauses from the remaining string to get the description. This was more reliable than plain splits because queries don't always have predictable word order or spacing (e.g., `"size M vintage tee under $30"` vs `"vintage tee, size M, under $30"`).

A second small change: `suggest_outfit` was also written to handle a wardrobe dict that is missing the `"items"` key entirely (not just an empty list). This came up during testing when passing `{}` as a wardrobe, which the plan hadn't anticipated. The fix — using `.get("items", [])` — is a one-liner but the test case made it explicit.

---

## AI Usage

### Instance 1: Implementing `search_listings`

I gave Claude Code the Tool 1 spec from `planning.md` — the input parameter table, the return value description, and the TODO list in the function docstring. I asked it to filter by price and size first, then score remaining listings by keyword overlap with the description.

Claude produced the keyword-scoring loop using a set of lowercased description words and checking membership across a joined string of title, description, category, brand, style tags, and colors. I kept the scoring logic as-is but added `listing.get("brand") or ""` instead of just `listing.get("brand")` because some brand values in the dataset are `null` (which would crash `.join()` if not handled). I also explicitly tested the size filter with `"S"` and confirmed it matched listings sized `"S/M"` — the case-insensitive substring approach was intentional.

### Instance 2: Implementing `run_agent`

I gave Claude Code the Planning Loop, State Management, and Architecture sections of `planning.md`. I asked it to follow the seven steps described and use regex for query parsing instead of plain string splitting.

Claude produced the full `run_agent` function including the regex patterns for price and size extraction, the clause-stripping for the description, and the early-return guard on empty search results. I verified the output by printing `session["selected_item"]` and the inputs actually passed to `suggest_outfit` to confirm they were the same dict. I also ran the no-results query (`"designer ballgown size XXS under $5"`) and confirmed that `session["error"]` was set and `suggest_outfit` was never called.
