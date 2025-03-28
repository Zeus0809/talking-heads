import streamlit.components.v1 as components
import math

MESSAGE_WIDTH_PERCENTAGE = 0.8
FONT_SIZE = 16 # px
CONTAINER_WIDTH = 700 # px
LINE_HEIGHT_MULTIPLIER = 1.5
CHAR_WIDTH = 0.6 * FONT_SIZE
MAX_LINE_WIDTH = CONTAINER_WIDTH * MESSAGE_WIDTH_PERCENTAGE
MAX_CHARS_PER_LINE = 69
HEIGHT_REDUCER_MULTIPLIER = 10 # when message gets to 6 lines or longer, reduce the height by this multiplier * (total_lines - 5)

def estimate_content_width(text: str) -> int:
    content_width = len(text) * CHAR_WIDTH
    return min(content_width, MAX_LINE_WIDTH)

def estimate_content_height(text: str) -> int:
    total_lines = math.ceil(len(text) / MAX_CHARS_PER_LINE)
    line_height = FONT_SIZE * LINE_HEIGHT_MULTIPLIER
    content_height = total_lines * line_height # add padding
    if total_lines > 3:
        content_height -= HEIGHT_REDUCER_MULTIPLIER * (total_lines - 3)
    #print(f"content_height: {content_height}, total_lines: {total_lines}")
    return max(content_height, 32)

# This function defines css styles for model response boxes, produces an html string and embeds it into the webpage for every message.
def render_model_response(text: str, model_side: str) -> None:

    content_width = estimate_content_width(text)
    content_height = estimate_content_height(text)

    css = f"""
    <style>
    .model_response_container {{
        margin: 0;
        # border: 2px solid red;
        display: flex;
        justify-content: {model_side};
    }}
    .model_response {{ 
        display: flex;
        justify-content: center;
        font-family: monospace;
        padding: 0 0.5rem 0 0.5rem;
        border-radius: 0.5rem;
        width: {content_width}px;
        height: {content_height}px;
        transition: height 0.1s ease-in-out;
        transition: width 0.1s ease-in-out;
    }}
    .model_response p {{
        margin: 0.5rem;
        padding: 0;
        width: 100%;
    }}
    .model_left {{
        background-color: #d1feff;
    }}
    .model_right {{
        background-color: #fffad1;
    }}
    </style>
    """

    message_html = f"""
    {css}
    <div class="model_response_container">
        <div class="model_response model_{model_side}">
            <p>{text}</p>
        </div>
    </div>
    """

    # render the html string
    components.html(message_html, height = content_height + FONT_SIZE * 1.4)
