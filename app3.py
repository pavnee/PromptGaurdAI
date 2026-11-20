# ============================================================
# PROMPTGUARD AI 2.0
# Reliability Prediction Using Uncertainty Estimation
# and Selective Prediction
# MSc AIML Capstone Project
# ============================================================

import os
import re
import json
import time
import streamlit as st

from dotenv import load_dotenv
from google import genai
from google.genai import types


# ============================================================
# 1. CONFIGURATION
# ============================================================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = "gemini-3.5-flash"

# FIX 1: longer timeout + automatic retries (see analyze_with_gemini)
REQUEST_TIMEOUT_MS = 60000
MAX_RETRIES = 2

# SPEED: "minimal" = fastest, "low" = fast + good quality,
# "medium" = Gemini default (slower), "high" = slowest
THINKING_LEVEL = "low"

st.set_page_config(
    page_title="PromptGuard AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# 2. FUTURISTIC DESIGN
# ============================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(ellipse at 10% 5%,
        rgba(111, 57, 202, 0.20), transparent 35%),
        radial-gradient(ellipse at 90% 30%,
        rgba(0, 190, 220, 0.12), transparent 35%),
        #080B18;
    color: #F1F5FF;
}

[data-testid="stHeader"] {
    background: transparent;
}

.block-container {
    max-width: 1200px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

h1, h2, h3, h4 {
    font-family: 'Space Grotesk', sans-serif !important;
    color: #F4F2FF !important;
}

p, label, li {
    color: #C5C9DE;
}

.hero {
    position: relative;
    overflow: hidden;
    background: linear-gradient(
        120deg,
        rgba(104, 65, 190, 0.22),
        rgba(12, 190, 218, 0.10),
        rgba(24, 25, 55, 0.55)
    );
    border: 1px solid rgba(170, 145, 255, 0.25);
    border-radius: 25px;
    padding: 38px 35px;
    margin-bottom: 25px;
    box-shadow: 0 15px 55px rgba(0,0,0,0.25);
}

.hero h1 {
    font-size: 43px;
    margin-bottom: 8px;
    background: linear-gradient(90deg,#FFFFFF,#BBA6FF,#69E6F5);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero p {
    font-size: 15px;
    color: #BFC6E3;
    line-height: 1.8;
}

.orb-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 190px;
    perspective: 700px;
}

.orb {
    width: 145px;
    height: 145px;
    border-radius: 50%;
    position: relative;
    background: radial-gradient(
        circle at 35% 30%,
        #D8F8FF 0%,
        #8E78FF 18%,
        #623BCE 43%,
        #121A49 75%,
        #070A19 100%
    );
    box-shadow:
        0 0 25px #7957F5,
        0 0 65px rgba(108,75,245,0.65),
        inset -15px -15px 35px #080B2B,
        inset 8px 8px 25px rgba(255,255,255,0.45);
    animation: float 4s ease-in-out infinite,
               rotateOrb 12s linear infinite;
}

.orb:before {
    content: "";
    position: absolute;
    inset: -17px;
    border: 2px solid rgba(112,220,255,0.55);
    border-radius: 50%;
    transform: rotateX(65deg);
    box-shadow: 0 0 20px rgba(85,200,255,0.5);
}

.orb:after {
    content: "";
    position: absolute;
    inset: -29px;
    border: 1px solid rgba(176,120,255,0.5);
    border-radius: 50%;
    transform: rotateY(65deg);
}

@keyframes float {
    0%,100% { transform: translateY(0px) rotateX(8deg); }
    50% { transform: translateY(-17px) rotateX(-8deg); }
}

@keyframes rotateOrb {
    from { filter: hue-rotate(0deg); }
    to { filter: hue-rotate(35deg); }
}

.glass-card {
    background: linear-gradient(
        145deg,
        rgba(32,36,69,0.90),
        rgba(17,22,43,0.92)
    );
    border: 1px solid rgba(153,137,255,0.20);
    border-radius: 18px;
    padding: 23px;
    margin: 12px 0;
    box-shadow: 0 8px 30px rgba(0,0,0,0.20);
}

.metric-card {
    background: linear-gradient(
        135deg,
        rgba(105,72,210,0.20),
        rgba(22,31,61,0.85)
    );
    border: 1px solid rgba(152,126,255,0.28);
    border-radius: 17px;
    padding: 20px;
    text-align: center;
}

.metric-number {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 37px;
    font-weight: 700;
    background: linear-gradient(90deg,#BFA8FF,#63E6F5);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.section-label {
    color: #A99AFF;
    font-size: 12px;
    letter-spacing: 2px;
    font-weight: 700;
    text-transform: uppercase;
}

.issue-card {
    background: rgba(255,255,255,0.035);
    border: 1px solid rgba(255,190,100,0.22);
    border-left: 4px solid #F6B85F;
    border-radius: 12px;
    padding: 17px;
    margin: 12px 0;
}

.success-card {
    background: rgba(40,210,170,0.07);
    border: 1px solid rgba(40,210,170,0.28);
    border-radius: 13px;
    padding: 18px;
    margin: 12px 0;
}

.stTextArea textarea {
    background: #13182D !important;
    color: white !important;
    border: 1px solid #6254A5 !important;
    border-radius: 13px !important;
    font-size: 15px !important;
}

.stButton > button {
    background: linear-gradient(100deg,#754BE8,#427FEA,#20BFD1);
    color: white !important;
    border: none;
    border-radius: 12px;
    min-height: 47px;
    font-weight: 700;
    transition: all 0.3s ease;
}

.stButton > button:hover {
    box-shadow: 0 0 25px rgba(115,90,255,0.55);
    transform: translateY(-2px);
}

/* FIX 2: "Analyse My Prompt" is a FORM submit button, which the
   .stButton rule above does not reach, so it stayed white with
   faint text. These rules style it the same as the other buttons. */
.stFormSubmitButton > button,
[data-testid="stFormSubmitButton"] > button,
[data-testid="stBaseButton-secondaryFormSubmit"],
[data-testid="stBaseButton-primaryFormSubmit"] {
    background: linear-gradient(100deg,#754BE8,#427FEA,#20BFD1) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 12px !important;
    min-height: 47px;
    font-weight: 700 !important;
    transition: all 0.3s ease;
}

.stFormSubmitButton > button:hover,
[data-testid="stFormSubmitButton"] > button:hover,
[data-testid="stBaseButton-secondaryFormSubmit"]:hover,
[data-testid="stBaseButton-primaryFormSubmit"]:hover {
    box-shadow: 0 0 25px rgba(115,90,255,0.55);
    transform: translateY(-2px);
    color: #FFFFFF !important;
}

.stFormSubmitButton > button p,
.stFormSubmitButton > button span,
[data-testid="stFormSubmitButton"] > button p,
[data-testid="stFormSubmitButton"] > button span,
[data-testid="stBaseButton-secondaryFormSubmit"] p,
[data-testid="stBaseButton-secondaryFormSubmit"] span,
.stButton > button p,
.stButton > button span {
    color: #FFFFFF !important;
    font-weight: 700 !important;
}

.stProgress > div > div > div > div {
    background: linear-gradient(90deg,#8D65FF,#45D9EB);
}

hr {
    border-color: rgba(160,150,220,0.18);
}

[data-testid="stMetric"] {
    background: #171D36;
    border: 1px solid rgba(145,130,255,0.2);
    padding: 17px;
    border-radius: 14px;
}

[data-testid="stMetricValue"] {
    color: #BDAAFF;
}

footer {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)


# FIX 3 (styling): dashboard design, modelled on the reference image
st.markdown("""
<style>

.dash-welcome h2 {
    font-size: 30px;
    margin: 4px 0 2px 0;
}

.dash-welcome p {
    font-size: 14px;
    color: #9AA3C7;
    margin-bottom: 18px;
}

.dash-stat {
    background: linear-gradient(
        140deg,
        rgba(105,72,210,0.22),
        rgba(20,26,52,0.92)
    );
    border: 1px solid rgba(152,126,255,0.28);
    border-radius: 16px;
    padding: 16px 18px 10px 18px;
    height: 150px;
    box-shadow: 0 8px 28px rgba(0,0,0,0.22);
    position: relative;
    overflow: hidden;
}

.dash-stat-label {
    font-size: 12px;
    color: #A9B2D6;
    font-weight: 600;
}

.dash-stat-value {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 30px;
    font-weight: 700;
    color: #FFFFFF;
    margin-top: 4px;
    line-height: 1.1;
}

.dash-stat-sub {
    font-size: 11px;
    color: #5FE3C0;
    margin-top: 2px;
}

.dash-stat svg {
    position: absolute;
    right: 10px;
    bottom: 10px;
    opacity: 0.95;
}

.dash-panel {
    background: linear-gradient(
        145deg,
        rgba(32,36,69,0.90),
        rgba(15,20,42,0.94)
    );
    border: 1px solid rgba(153,137,255,0.22);
    border-radius: 18px;
    padding: 20px 22px;
    margin-top: 14px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.22);
}

.dash-panel-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 16px;
    font-weight: 600;
    color: #F4F2FF;
}

.dash-panel-big {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 30px;
    font-weight: 700;
    color: #FFFFFF;
}

.dash-legend {
    display: flex;
    gap: 16px;
    font-size: 12px;
    color: #A9B2D6;
    margin: 4px 0 6px 0;
}

.dash-dot {
    display: inline-block;
    width: 9px;
    height: 9px;
    border-radius: 50%;
    margin-right: 6px;
}

.dash-gauge-row {
    display: flex;
    justify-content: space-between;
    font-size: 12px;
    color: #B7BFDD;
    padding: 3px 0;
}

.dash-action {
    background: linear-gradient(
        140deg,
        rgba(105,72,210,0.18),
        rgba(20,26,52,0.92)
    );
    border: 1px solid rgba(152,126,255,0.25);
    border-radius: 15px;
    padding: 16px 18px;
    margin-top: 14px;
    height: 118px;
}

.dash-action-icon {
    font-size: 20px;
}

.dash-action-title {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 600;
    font-size: 14px;
    color: #F4F2FF;
    margin-top: 6px;
}

.dash-action-text {
    font-size: 12px;
    color: #9AA3C7;
    line-height: 1.5;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# 3. HERO SECTION
# ============================================================

left, right = st.columns([3, 1])

with left:

    st.markdown("""
    <div class="hero">
        <div class="section-label">AI RELIABILITY INTELLIGENCE</div>
        <h1>PromptGuard AI</h1>
        <p>
        Think better. Prompt better. Trust smarter.<br>
        Analyse prompts, detect uncertainty and improve
        the reliability of AI-generated responses.
        </p>
    </div>
    """, unsafe_allow_html=True)

with right:

    st.markdown("""
    <div class="orb-container">
        <div class="orb"></div>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# 4. GEMINI CLIENT
# ============================================================

@st.cache_resource
def get_client(api_key):

    return genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(timeout=REQUEST_TIMEOUT_MS)
    )


# ============================================================
# 5. PROMPT QUALITY SCORING
# ============================================================

def evaluate_prompt(prompt):

    words = prompt.lower().split()
    text = prompt.lower()

    vague_words = [
        "everything", "anything", "stuff",
        "things", "some", "good", "best",
        "properly", "whatever", "etc"
    ]

    task_verbs = [
        "explain", "describe", "compare",
        "analyse", "analyze", "create",
        "write", "calculate", "summarize",
        "summarise", "identify", "list",
        "evaluate", "design", "discuss",
        "define", "generate", "classify"
    ]

    output_indicators = [
        "table", "bullet", "paragraph",
        "word", "format", "example",
        "step", "heading", "list",
        "include", "avoid", "structure"
    ]

    context_indicators = [
        "because", "for a", "for my",
        "background", "context", "beginner",
        "student", "professional", "experience",
        "audience", "level", "using"
    ]

    vague_count = sum(
        len(re.findall(r"\b" + re.escape(w) + r"\b", text))
        for w in vague_words
    )

    has_task = any(
        re.search(r"\b" + re.escape(w) + r"\b", text)
        for w in task_verbs
    )

    has_output = any(w in text for w in output_indicators)
    has_context = any(w in text for w in context_indicators)

    # Five evaluation dimensions

    clarity = min(
        100,
        max(15, 55 + min(len(words), 20) * 1.5
            - vague_count * 12 + (15 if has_task else 0))
    )

    context = min(
        100,
        25 + (25 if has_context else 0)
        + (20 if len(words) >= 15 else 0)
        + (15 if len(words) >= 25 else 0)
    )

    specificity = min(
        100,
        max(15, 30 + min(len(words), 30) * 1.5
            - vague_count * 15
            + (15 if has_output else 0))
    )

    task_definition = 85 if has_task else 25

    output_requirements = (
        90 if has_output else
        35
    )

    dimensions = {
        "Clarity": round(clarity),
        "Context": round(context),
        "Specificity": round(specificity),
        "Task definition": round(task_definition),
        "Output requirements": round(output_requirements)
    }

    weights = {
        "Clarity": 0.25,
        "Context": 0.25,
        "Specificity": 0.20,
        "Task definition": 0.15,
        "Output requirements": 0.15
    }

    score = sum(
        dimensions[k] * weights[k]
        for k in dimensions
    )

    return round(score, 1), dimensions


# ============================================================
# 6. RESPONSE RELIABILITY ANALYSIS
# ============================================================

def _parse_json(text):
    """Parse the model's JSON, tolerating stray code fences."""

    cleaned = text.strip()

    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)

    return json.loads(cleaned)


def analyze_with_gemini(prompt):

    if not API_KEY:
        raise ValueError(
            "Gemini API key not found. Check your .env file."
        )

    client = get_client(API_KEY)

    instructions = f"""
You are PromptGuard AI, an AI reliability evaluator.

Analyse the following user prompt and generate an answer.

USER PROMPT:
{prompt}

Your tasks:

1. Give a useful, direct answer.
2. Find problems in the user's prompt.
3. Explain each problem in simple everyday English.
4. Explain why each problem matters.
5. Suggest a practical fix for each problem.
6. Create a better version of the prompt.
7. Identify uncertain parts of your generated answer.
8. Assess answer reliability using five dimensions.

Reliability dimensions (0 to 100):

relevance: Does the answer actually address the question?
evidence: Are important claims supported by reliable evidence
or established knowledge? Do not pretend to have verified sources.
completeness: Does the answer cover the important parts?
uncertainty_handling: Does the answer acknowledge limitations?
freshness: Is the information likely to remain current?

Be conservative and honest.

IMPORTANT:
- Do not confuse prompt quality with answer reliability.
- A well-written prompt does not guarantee a correct answer.
- Do not invent citations or sources.
- If information is uncertain, say so.
- Do not use complicated technical language when explaining
  prompt problems.
- Keep the answer useful but reasonably concise.
- Scores are estimates, not calibrated probabilities.

Return valid JSON only, using this structure:

{{
  "answer": "Your generated answer",

  "prompt_issues": [
    {{
      "title": "The problem in simple words",
      "explanation": "Explain the problem simply.",
      "impact": "Explain how this affects the answer.",
      "fix": "Explain what the user should change."
    }}
  ],

  "uncertainty_reasons": [
    "A simple explanation of uncertainty"
  ],

  "reliability_dimensions": {{
    "relevance": 80,
    "evidence": 70,
    "completeness": 85,
    "uncertainty_handling": 75,
    "freshness": 80
  }},

  "reliability_explanation": "Explain the overall assessment.",

  "improved_prompt": "A much clearer and more specific prompt.",

  "verification_needed": [
    "Claims that should be checked"
  ],

  "decision": "ANSWER"
}}

The decision must be one of:
ANSWER, QUALIFY, ABSTAIN.

Return no Markdown code fences.
"""

    # FIX 1: the 504 DEADLINE_EXCEEDED came from Gemini not finishing
    # inside the old 45 s limit. We now allow 120 s and retry
    # temporary server errors (503 / 504 / 429) with a short backoff.
    # max_output_tokens was also raised so long JSON is not cut off.

    response = None
    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):

        try:

            response = client.models.generate_content(
                model=MODEL,
                contents=instructions,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    max_output_tokens=4096,
                    response_mime_type="application/json",
                    # SPEED: Gemini 3.5 "thinks" before answering (default
                    # level is medium). "low" cuts that wait a lot.
                    thinking_config=types.ThinkingConfig(
                        thinking_level=THINKING_LEVEL
                    )
                )
            )

            break

        except Exception as e:

            last_error = e
            err = str(e)

            temporary = any(
                code in err
                for code in [
                    "503", "504", "429",
                    "DEADLINE_EXCEEDED",
                    "UNAVAILABLE"
                ]
            ) or "timeout" in err.lower()

            if temporary and attempt < MAX_RETRIES:
                time.sleep(2 * attempt)
                continue

            raise

    if response is None:
        raise last_error

    if not response.text:
        raise ValueError("Gemini returned an empty response.")

    result = _parse_json(response.text)

    required = [
        "answer",
        "prompt_issues",
        "uncertainty_reasons",
        "reliability_dimensions",
        "reliability_explanation",
        "improved_prompt",
        "verification_needed",
        "decision"
    ]

    for field in required:
        if field not in result:
            raise ValueError(
                "Missing information in Gemini response: " + field
            )

    # Calculate reliability using fixed weights

    dimensions = result["reliability_dimensions"]

    reliability_weights = {
        "relevance": 0.25,
        "evidence": 0.25,
        "completeness": 0.20,
        "uncertainty_handling": 0.15,
        "freshness": 0.15
    }

    reliability_score = 0

    for key, weight in reliability_weights.items():

        value = float(dimensions[key])

        if not 0 <= value <= 100:
            raise ValueError("Invalid reliability dimension.")

        reliability_score += value * weight

    result["reliability_score"] = round(
        reliability_score, 1
    )

    decision = result["decision"].upper()

    if decision not in ["ANSWER", "QUALIFY", "ABSTAIN"]:
        decision = "QUALIFY"

    result["decision"] = decision
    result["model_used"] = MODEL

    return result


# ============================================================
# 7. SESSION STATE
# ============================================================

if "result" not in st.session_state:
    st.session_state.result = None

if "improved_result" not in st.session_state:
    st.session_state.improved_result = None

if "original_prompt" not in st.session_state:
    st.session_state.original_prompt = ""

# Dashboard history (one entry per analysed prompt)
if "history" not in st.session_state:
    st.session_state.history = []


# ============================================================
# 7B. DASHBOARD
# ============================================================

def sparkline_svg(values, color):
    """Tiny trend line shown inside the stat cards."""

    w, h = 90, 30

    if len(values) < 2:
        return (
            f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'<line x1="0" y1="{h-4}" x2="{w}" y2="{h-4}" '
            f'stroke="{color}" stroke-width="2" '
            f'stroke-dasharray="4 4" opacity="0.5"/></svg>'
        )

    lo, hi = min(values), max(values)
    span = (hi - lo) or 1

    pts = []

    for i, v in enumerate(values):
        x = i * (w / (len(values) - 1))
        y = h - 4 - ((v - lo) / span) * (h - 8)
        pts.append(f"{x:.1f},{y:.1f}")

    return (
        f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
        f'<polyline points="{" ".join(pts)}" fill="none" '
        f'stroke="{color}" stroke-width="2.2" '
        f'stroke-linecap="round" stroke-linejoin="round"/></svg>'
    )


def stat_card_html(label, value, sub, spark):

    return (
        '<div class="dash-stat">'
        f'<div class="dash-stat-label">{label}</div>'
        f'<div class="dash-stat-value">{value}</div>'
        f'<div class="dash-stat-sub">{sub}</div>'
        f'{spark}'
        '</div>'
    )


def performance_chart_svg(quality, reliability):
    """Line chart: prompt quality vs answer reliability per analysis."""

    w, h = 620, 230
    pl, pr, pt, pb = 38, 16, 14, 26

    parts = [
        f'<svg width="100%" viewBox="0 0 {w} {h}" '
        f'xmlns="http://www.w3.org/2000/svg">'
    ]

    # Grid + y labels
    for g in (0, 25, 50, 75, 100):
        y = h - pb - (g / 100) * (h - pt - pb)
        parts.append(
            f'<line x1="{pl}" y1="{y:.1f}" x2="{w-pr}" y2="{y:.1f}" '
            f'stroke="rgba(160,150,220,0.15)" stroke-width="1"/>'
            f'<text x="{pl-8}" y="{y+4:.1f}" fill="#7F89B0" '
            f'font-size="11" text-anchor="end">{g}</text>'
        )

    n = len(quality)

    if n == 0:
        parts.append(
            f'<text x="{w/2}" y="{h/2}" fill="#8992B5" font-size="13" '
            f'text-anchor="middle">Run your first analysis '
            f'to see performance trends</text>'
        )
        parts.append("</svg>")
        return "".join(parts)

    def xy(i, v):
        if n == 1:
            x = (pl + (w - pr)) / 2
        else:
            x = pl + i * ((w - pl - pr) / (n - 1))
        y = h - pb - (v / 100) * (h - pt - pb)
        return x, y

    for series, color in (
        (quality, "#9B7BFF"),
        (reliability, "#45D9EB")
    ):

        pts = [xy(i, v) for i, v in enumerate(series)]

        if n > 1:
            path = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
            parts.append(
                f'<polyline points="{path}" fill="none" '
                f'stroke="{color}" stroke-width="2.6" '
                f'stroke-linecap="round" stroke-linejoin="round"/>'
            )

        for x, y in pts:
            parts.append(
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" '
                f'fill="{color}"/>'
            )

        # Highlight the latest point
        lx, ly = pts[-1]
        parts.append(
            f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="7" fill="{color}" '
            f'opacity="0.28"/>'
            f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="4.5" fill="#FFFFFF"/>'
        )

    # x labels (analysis number)
    step = max(1, n // 8)

    for i in range(0, n, step):
        x, _ = xy(i, 0)
        parts.append(
            f'<text x="{x:.1f}" y="{h-8}" fill="#7F89B0" '
            f'font-size="11" text-anchor="middle">#{i+1}</text>'
        )

    parts.append("</svg>")
    return "".join(parts)


def gauge_svg(value):
    """Semicircle confidence gauge."""

    value = max(0, min(100, value))

    return (
        '<svg width="100%" viewBox="0 0 200 125" '
        'xmlns="http://www.w3.org/2000/svg">'
        '<defs><linearGradient id="gaugeGrad" x1="0" y1="0" x2="1" y2="0">'
        '<stop offset="0%" stop-color="#F6B85F"/>'
        '<stop offset="45%" stop-color="#45D9EB"/>'
        '<stop offset="100%" stop-color="#8D65FF"/>'
        '</linearGradient></defs>'
        '<path d="M 20 105 A 80 80 0 0 1 180 105" fill="none" '
        'stroke="rgba(160,150,220,0.18)" stroke-width="14" '
        'stroke-linecap="round" pathLength="100"/>'
        '<path d="M 20 105 A 80 80 0 0 1 180 105" fill="none" '
        'stroke="url(#gaugeGrad)" stroke-width="14" '
        f'stroke-linecap="round" pathLength="100" '
        f'stroke-dasharray="{value:.1f} 100"/>'
        f'<text x="100" y="88" fill="#FFFFFF" font-size="30" '
        f'font-weight="700" text-anchor="middle" '
        f'font-family="Space Grotesk, sans-serif">{value:.1f}</text>'
        '<text x="100" y="106" fill="#9AA3C7" font-size="10" '
        'text-anchor="middle">Overall Score</text>'
        '</svg>'
    )


def render_dashboard():
    """Dashboard: welcome, stat cards, performance chart,
    confidence gauge and quick-action cards."""

    history = st.session_state.history

    total = len(history)
    quality = [h["prompt_quality"] for h in history]
    reliability = [h["reliability"] for h in history]

    avg_quality = sum(quality) / total if total else None
    avg_reliability = sum(reliability) / total if total else None

    answer_count = sum(
        1 for h in history if h["decision"] == "ANSWER"
    )
    answer_rate = (answer_count / total * 100) if total else None

    def fmt(v):
        return f"{v:.1f}%" if v is not None else "—"

    def sub(values, empty="Run an analysis to begin"):
        if not values:
            return empty
        return f"Latest: {values[-1]:.1f}%"

    st.markdown("""
    <div class="dash-welcome">
        <div class="section-label">YOUR DASHBOARD</div>
        <h2>Welcome back</h2>
        <p>Here's what's happening with your prompts and AI answers.</p>
    </div>
    """, unsafe_allow_html=True)

    # ---- Stat cards ----

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(
            stat_card_html(
                "Prompts Analysed",
                str(total),
                "This session" if total else "Run an analysis to begin",
                sparkline_svg(
                    list(range(1, total + 1)), "#9B7BFF"
                )
            ),
            unsafe_allow_html=True
        )

    with c2:
        st.markdown(
            stat_card_html(
                "Avg Prompt Quality",
                fmt(avg_quality),
                sub(quality),
                sparkline_svg(quality, "#45D9EB")
            ),
            unsafe_allow_html=True
        )

    with c3:
        st.markdown(
            stat_card_html(
                "Avg Answer Reliability",
                fmt(avg_reliability),
                sub(reliability),
                sparkline_svg(reliability, "#5FE3C0")
            ),
            unsafe_allow_html=True
        )

    with c4:
        decision_trend = [
            100 if h["decision"] == "ANSWER"
            else 50 if h["decision"] == "QUALIFY"
            else 0
            for h in history
        ]
        st.markdown(
            stat_card_html(
                "Ready-to-Answer Rate",
                fmt(answer_rate),
                (f"{answer_count} of {total} prompts"
                 if total else "Run an analysis to begin"),
                sparkline_svg(decision_trend, "#F6B85F")
            ),
            unsafe_allow_html=True
        )

    # ---- Chart + gauge ----

    chart_col, gauge_col = st.columns([2, 1])

    with chart_col:

        big = (
            f"{(avg_quality + avg_reliability) / 2:.1f}"
            if total else "—"
        )

        st.markdown(
            '<div class="dash-panel">'
            '<div class="dash-panel-title">Prompt Performance Index</div>'
            f'<div class="dash-panel-big">{big}</div>'
            '<div class="dash-legend">'
            '<span><span class="dash-dot" '
            'style="background:#9B7BFF"></span>Prompt quality</span>'
            '<span><span class="dash-dot" '
            'style="background:#45D9EB"></span>Answer reliability</span>'
            '</div>'
            + performance_chart_svg(quality, reliability) +
            '</div>',
            unsafe_allow_html=True
        )

    with gauge_col:

        latest = history[-1] if history else None
        dims = latest["dims"] if latest else {}

        overall = (
            latest["reliability"] if latest else 0
        )

        def dim_row(label, key, color):
            val = dims.get(key)
            txt = f"{float(val):.0f}%" if val is not None else "—"
            return (
                '<div class="dash-gauge-row">'
                f'<span><span class="dash-dot" '
                f'style="background:{color}"></span>{label}</span>'
                f'<span>{txt}</span></div>'
            )

        st.markdown(
            '<div class="dash-panel">'
            '<div class="dash-panel-title">AI Confidence Index</div>'
            + gauge_svg(overall) +
            dim_row("Relevance", "relevance", "#8D65FF")
            + dim_row("Evidence", "evidence", "#45D9EB")
            + dim_row("Completeness", "completeness", "#F6B85F") +
            '</div>',
            unsafe_allow_html=True
        )

    # ---- Quick actions ----

    st.markdown(
        '<div class="section-label" style="margin-top:22px">'
        'WHAT PROMPTGUARD DOES</div>',
        unsafe_allow_html=True
    )

    actions = [
        ("🛡️", "Analyse Prompts",
         "Score clarity, context and specificity."),
        ("🔎", "Detect Uncertainty",
         "See what could make an answer unreliable."),
        ("✨", "Improve Prompts",
         "Get a clearer, better-structured prompt."),
        ("📈", "Compare Results",
         "Test the improved prompt, before vs after."),
    ]

    a1, a2, a3, a4 = st.columns(4)

    for col, (icon, title, text) in zip(
        (a1, a2, a3, a4), actions
    ):
        with col:
            st.markdown(
                '<div class="dash-action">'
                f'<div class="dash-action-icon">{icon}</div>'
                f'<div class="dash-action-title">{title}</div>'
                f'<div class="dash-action-text">{text}</div>'
                '</div>',
                unsafe_allow_html=True
            )

    st.divider()


# The dashboard is drawn into this slot after any new analysis has run,
# so the numbers are always up to date.
dashboard_slot = st.empty()


# ============================================================
# 8. PROMPT INPUT
# ============================================================

st.markdown("""
<div class="section-label">START YOUR ANALYSIS</div>
<h2>What would you like to ask AI?</h2>
""", unsafe_allow_html=True)

with st.form("prompt_form"):

    prompt = st.text_area(
        "Enter your prompt",
        value=st.session_state.original_prompt,
        placeholder=(
            "Example: Explain machine learning to a beginner, "
            "compare its major types and give practical examples..."
        ),
        height=125
    )

    submitted = st.form_submit_button(
        "✦  Analyse My Prompt",
        use_container_width=True
    )


if submitted:

    if not prompt.strip():

        st.warning("Please enter a prompt first.")

    elif len(prompt.strip()) < 3:

        st.warning("Please enter a meaningful question.")

    else:

        st.session_state.result = None
        st.session_state.improved_result = None
        st.session_state.original_prompt = prompt

        try:

            with st.spinner(
                "✦ PromptGuard is analysing your question..."
            ):

                result = analyze_with_gemini(prompt)

                st.session_state.result = result

                # Record this analysis for the dashboard
                q_score, _ = evaluate_prompt(prompt)

                st.session_state.history.append({
                    "prompt_quality": q_score,
                    "reliability": result["reliability_score"],
                    "decision": result["decision"],
                    "dims": {
                        k: float(v)
                        for k, v in
                        result["reliability_dimensions"].items()
                    }
                })

        except Exception as e:

            error = str(e)

            if "503" in error:
                st.error(
                    "Gemini is temporarily overloaded. "
                    "Please try again shortly."
                )

            elif "504" in error or "DEADLINE_EXCEEDED" in error:
                st.error(
                    "Gemini took too long to respond (even after "
                    "automatic retries). Please try again in a "
                    "moment or use a shorter prompt."
                )

            elif "429" in error:
                st.error(
                    "API request limit reached. "
                    "Please wait and try again."
                )

            elif "timeout" in error.lower():
                st.error(
                    "The request took too long. "
                    "Please try a shorter prompt."
                )

            else:
                st.error(
                    f"Analysis failed: {type(e).__name__}: {error}"
                )


# Draw the dashboard (above the input) with up-to-date data
with dashboard_slot.container():
    render_dashboard()


# ============================================================
# 9. RESULTS
# ============================================================

if st.session_state.result:

    result = st.session_state.result

    prompt_score, prompt_dimensions = evaluate_prompt(
        st.session_state.original_prompt
    )

    reliability_score = result["reliability_score"]

    st.divider()

    st.markdown("""
    <div class="section-label">YOUR ANALYSIS IS READY</div>
    <h2>AI Intelligence Report</h2>
    """, unsafe_allow_html=True)

    st.caption("Powered by " + result["model_used"])

    # ---------------- DECISION ----------------

    decision = result["decision"]

    decision_text = {
        "ANSWER": "Ready to answer",
        "QUALIFY": "Answer with caution",
        "ABSTAIN": "More information needed"
    }

    if decision == "ANSWER":
        st.success("✓ " + decision_text[decision])

    elif decision == "QUALIFY":
        st.warning("⚠ " + decision_text[decision])

    else:
        st.error("✕ " + decision_text[decision])

    # ---------------- SCORES ----------------

    st.subheader("Your AI Performance Overview")

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(f"""
        <div class="metric-card">
            <div class="section-label">PROMPT QUALITY</div>
            <div class="metric-number">{prompt_score:.1f}%</div>
            <p>How clearly you asked your question</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:

        st.markdown(f"""
        <div class="metric-card">
            <div class="section-label">ANSWER RELIABILITY</div>
            <div class="metric-number">{reliability_score:.1f}%</div>
            <p>AI-assisted estimate of answer reliability</p>
        </div>
        """, unsafe_allow_html=True)

    st.caption(
        "These are two different measurements. "
        "Prompt quality does not guarantee answer correctness."
    )

    # ---------------- AI ANSWER ----------------

    st.divider()

    st.subheader("🤖 Your AI Answer")

    st.markdown(
        '<div class="glass-card">',
        unsafe_allow_html=True
    )

    st.markdown(result["answer"])

    st.markdown("</div>", unsafe_allow_html=True)

    # ---------------- RELIABILITY ----------------

    st.divider()

    st.subheader("🛡️ Why this reliability score?")

    st.write(result["reliability_explanation"])

    dimensions = result["reliability_dimensions"]

    display_names = {
        "relevance": "Answer relevance",
        "evidence": "Evidence support",
        "completeness": "Completeness",
        "uncertainty_handling": "Handling uncertainty",
        "freshness": "Information freshness"
    }

    for key, label in display_names.items():

        value = float(dimensions[key])

        st.write(f"**{label} — {value:.0f}%**")

        st.progress(int(value))

    st.caption(
        "The reliability estimate is AI-assisted and not "
        "yet experimentally calibrated against ground-truth answers."
    )

    # ---------------- PROMPT ISSUES ----------------

    st.divider()

    st.markdown("""
    <div class="section-label">LET'S IMPROVE YOUR QUESTION</div>
    <h2>What could be better?</h2>
    """, unsafe_allow_html=True)

    issues = result["prompt_issues"]

    if issues:

        for index, issue in enumerate(issues, start=1):

            st.markdown(f"""
            <div class="issue-card">
                <h4>⚠️ {index}. {issue['title']}</h4>
                <p><b>What's happening?</b><br>
                {issue['explanation']}</p>
                <p><b>Why does it matter?</b><br>
                {issue['impact']}</p>
                <p><b>How to fix it?</b><br>
                {issue['fix']}</p>
            </div>
            """, unsafe_allow_html=True)

    else:

        st.success(
            "No major prompt problems were identified."
        )

    # ---------------- UNCERTAINTY ----------------

    st.divider()

    st.subheader("🔎 What might make the answer uncertain?")

    for reason in result["uncertainty_reasons"]:

        st.info("💡 " + str(reason))

    # ---------------- VERIFICATION ----------------

    with st.expander("📚 Information worth double-checking"):

        for item in result["verification_needed"]:
            st.write("• " + str(item))

    # ---------------- IMPROVED PROMPT ----------------

    st.divider()

    st.markdown("""
    <div class="section-label">PROMPT OPTIMIZATION</div>
    <h2>Meet your improved prompt</h2>
    """, unsafe_allow_html=True)

    improved_prompt = result["improved_prompt"]

    st.text_area(
        "Your optimized question",
        value=improved_prompt,
        height=145,
        key="improved_prompt_box"
    )

    st.code(improved_prompt, language="text")

    st.button(
        "📋 Copy the improved prompt",
        on_click=lambda: st.toast(
            "Select and copy the improved prompt above."
        )
    )

    # ---------------- TEST IMPROVED PROMPT ----------------

    st.divider()

    st.subheader("🚀 Test the improved prompt")

    st.write(
        "Generate a second answer using your optimized prompt "
        "and compare the two results."
    )

    if st.button(
        "Test Improved Prompt",
        use_container_width=True
    ):

        try:

            with st.spinner(
                "Testing your improved prompt..."
            ):

                new_result = analyze_with_gemini(
                    improved_prompt
                )

                st.session_state.improved_result = new_result

        except Exception as e:

            st.error(
                f"Comparison failed: {type(e).__name__}: {e}"
            )

    # ---------------- COMPARISON ----------------

    if st.session_state.improved_result:

        new_result = st.session_state.improved_result

        new_prompt_score, new_dimensions = evaluate_prompt(
            improved_prompt
        )

        new_reliability = new_result["reliability_score"]

        st.divider()

        st.header("📈 Before vs After")

        st.write(
            "See how the improved prompt performs under "
            "the same evaluation framework."
        )

        c1, c2 = st.columns(2)

        with c1:

            st.metric(
                "Original Prompt Quality",
                f"{prompt_score:.1f}%"
            )

            st.metric(
                "Original Answer Reliability",
                f"{reliability_score:.1f}%"
            )

        with c2:

            st.metric(
                "Improved Prompt Quality",
                f"{new_prompt_score:.1f}%",
                delta=f"{new_prompt_score - prompt_score:+.1f} points"
            )

            st.metric(
                "Improved Answer Reliability",
                f"{new_reliability:.1f}%",
                delta=f"{new_reliability - reliability_score:+.1f} points"
            )

        st.info(
            "A better prompt can improve clarity and relevance, "
            "but it cannot guarantee factual accuracy. "
            "Reliability scores are estimates and may vary "
            "between AI generations."
        )

        st.subheader("Improved AI Answer")

        st.markdown(new_result["answer"])

        with st.expander("See improved reliability analysis"):

            for key, label in display_names.items():

                st.write(
                    f"**{label}:** "
                    f"{new_result['reliability_dimensions'][key]}%"
                )


# ============================================================
# 10. FOOTER
# ============================================================

st.divider()

st.markdown("""
<div style="text-align:center; padding:20px;">
    <h3 style="
        background:linear-gradient(90deg,#B99AFF,#56DFF0);
        -webkit-background-clip:text;
        -webkit-text-fill-color:transparent;">
        ✦ PromptGuard AI
    </h3>
    <p style="color:#8992B5;font-size:12px;">
        Artificial Intelligence & Machine Learning
        <br>
        Reliability Prediction Using Uncertainty
        Estimation and Selective Prediction
        <br><br>
        Built with Python, Streamlit and Gemini AI
    </p>
</div>
""", unsafe_allow_html=True)
