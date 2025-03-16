# talking-heads
A practice project involving two LLMs talking to each other in a web interface after the user introduces the first prompt.

## LLM usage of RAM when running:
1) Mistral 7B - 5.7GB
2) DeepSeek-R1 - 5.6GB
3) Llama2 - 8.3GB

## Conversation Structure

The application maintains two separate data structures to handle conversations:

### Conversation Log vs. Chat History

**Conversation Log:**
- **Purpose**: Maintains a chronological record of the AI models' conversation for display in the UI
- **Structure**: Contains only messages from the AI models (no user messages)
- **Format**: Each entry includes:
  ```python
  {
      "role": "assistant",
      "content": "The message content",
      "model": "model_name"  # Identifies which model generated the response
  }
  ```
- **Usage**: Used to render the conversation in the chat interface so users can see the exchange between models

**Chat History:**
- **Purpose**: Provides context to each individual model for generating responses
- **Structure**: Separate history for each model, containing only what that model needs to see
- **Format**: Standard LLM message format:
  ```python
  {
      "role": "user" or "assistant",
      "content": "The message content"
  }
  ```
- **Usage**: Sent to the Ollama API to give each model the context it needs to generate appropriate responses

### Why Both Are Needed:

1. **Different Perspectives for Different Models**:
   - Each model needs its own version of the conversation history
   - When Model A responds, Model B sees that response as a user message
   - This separation allows each model to maintain its own "perspective" of the conversation

2. **UI Display vs. API Requirements**:
   - The `conversation_log` includes metadata (like which model said what) needed for UI display
   - The `chat_history` is formatted specifically for the Ollama API requirements

3. **Complete Record vs. Contextual Information**:
   - `conversation_log` maintains the record of model responses for display
   - `chat_history` contains what each model needs to know to generate its next response

### Conversation Flow:

1. User asks a question to Model A
   - The initial prompt is displayed at the top of the UI
   - Added to Model A's `chat_history` as a user message (but not to the conversation log)

2. Model A responds
   - Added to `conversation_log` as an assistant message with Model A identified
   - Added to Model A's `chat_history` as an assistant message
   - Added to Model B's `chat_history` as a user message (so Model B can respond to it)

3. Model B responds
   - Added to `conversation_log` as an assistant message with Model B identified
   - Added to Model B's `chat_history` as an assistant message
   - Added to Model A's `chat_history` as a user message

This dual-structure approach creates the illusion of two AI models having a conversation with each other while maintaining appropriate context for each model.

### Automatic Conversation Loop

The application implements an automatic conversation loop using Streamlit's rerun functionality. After the initial user prompt and first model response, a continuous cycle begins where each model takes turns responding. The app checks which model responded last, gets a response from the other model, updates both the conversation log and chat histories, and then triggers another rerun. This creates a seamless back-and-forth conversation that continues automatically until the user clicks "STOP CONVERSATION", with no need for user intervention between turns.

### Chat UI Design

The chat interface displays only the LLM responses, creating a clean back-and-forth conversation view:

1. **Left Model Messages**: Positioned on the left side of the screen with a robot avatar (🤖)
2. **Right Model Messages**: Positioned on the right side of the screen with an alien avatar (👽)

The user's initial prompt is displayed separately at the top of the interface, keeping the chat area focused exclusively on the conversation between the two AI models. This approach uses Streamlit's column system to position messages on different sides of the screen while leveraging the built-in chat message styling. Each model has its own visual identity through both positioning and unique avatars, making it easy to follow the exchange between the two AI systems.


