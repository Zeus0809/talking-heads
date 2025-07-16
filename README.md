# Talking Heads AI

**Talking Heads AI** is a lightweight web application built with [Streamlit](https://streamlit.io), a Python-based UI framework commonly used for data-driven projects. It enables interactive conversations between two locally hosted large language models (LLMs) powered by [Ollama](https://ollama.com). Users can customize each model’s system prompt and control conversation flow, including turn limits and context retainment.

Watch the [demo](https://www.youtube.com/watch?v=Aq96Z8TsOK4) here.

---

## 🧠 Backend Structure

The app relies on Streamlit’s `session_state` to manage all runtime data, such as:

- Model selections
- System prompts
- Initial user prompt
- Conversation log

When the app launches, it queries the local Ollama server to fetch available models. After the initial user prompt is submitted:

1. It is sent to the selected model.
2. The response is then passed as a prompt to the opposing model.
3. This loop continues until a turn limit is reached.

If the **Use Context** option is enabled, each model receives a custom-formatted history of prior messages along with the current prompt—structured from that model’s point of view.

A **Clear Conversation** button lets users reset the chat history while preserving model settings and UI state.

---

## 🖼️ Frontend Structure

The interface is fully built with Streamlit and enhanced with:

- **Custom CSS** for layout tweaks (e.g., chat column styling)
- A **custom Python rendering function** that uses embedded iframes to create polished message bubbles—an improvised solution to achieve a more intuitive, chat-like interface
- Responses are streamed using ollama's chat streaming function.

---

## ⚠️ Challenges & Tradeoffs

While Streamlit offered rapid prototyping, it introduced some limitations:

- **UI customization is limited** — Streamlit’s support for HTML/CSS is restrictive, making visual polish time-consuming.
- **Frequent re-renders** — The app reruns from top to bottom on each interaction, which complicates control flow.
- **Session state handling** — Managing persistent yet mutable state under Streamlit’s reactivity model required a lot of trial and error.

These constraints also blocked the implementation of some features—like a **Pause Conversation** button that would temporarily halt the exchange and allow resume or clear actions.

---

## 🔭 What’s Next

- Test and integrate more open-source models to explore performance differences
- Improve reliability and UI polish
- Possibly scale into a multi-user or feature-rich app depending on feedback

---

To try the app, send me an email at [ikkit2002@gmail.com](mailto:ikkit2002@gmail.com) or DM me on [LinkedIn](https://www.linkedin.com/in/illia-kozlov-6828b7291/).

