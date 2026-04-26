from django.shortcuts import render
import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
import math
import json
import re



# 1. Profanity List
PROFANE_WORDS = {
    "anal","anus","arse","ass","ballsack","balls","bastard","bastards",
    "bitch","bitches","bitching","biatch","bloody","blowjob","bollock",
    "bollok","boner","boob","bugger","bullshit","bum","butt","buttplug",
    "clitoris","cock","coon","crap","crappy","cunt","damn","goddamn",
    "dick","dildo","fag","feck","fellatio","fuck","fucks","fucker",
    "fucked","fucking","homo","jerk","moron","morons","penis","piss",
    "poop","prick","pussy","scrotum","shit","shits","shitty","slut",
    "slutty","spank","tit","turd","twat","vagina","wank","whore","wtf",
    "bonehead","dickhead","douche","asshole","arsehole","screw","screws",
    "screwed","suck","sucks","sucker","sucking","prostitute","hooker",
    "motherfucker","fanny","hell","yuck"
}

def detect_profanity(text):
    words = text.lower().replace(".", " ").replace(",", " ").split()
    return [w for w in words if w in PROFANE_WORDS]



# 2. Sanitize Input (Markdown, URLs, Badges)
def clean_text(text):
    # Remove markdown images: ![alt](url)
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)

    # Remove markdown links: [text](url)
    text = re.sub(r'\[.*?\]\(.*?\)', '', text)

    # Remove raw URLs
    text = re.sub(r'http\S+', '', text)

    return text.strip()



# 3. Load API Key
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / "dataset/apiKey/api_key.env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)



# 4. LLM Helper (Safe JSON)
def run_llm(prompt):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    content = response.choices[0].message.content

    if not content or not content.strip():
        return "{}"

    return content


def safe_json_loads(raw, fallback):
    try:
        return json.loads(raw)
    except Exception:
        print("\n\n===== INVALID JSON FROM LLM =====")
        print(raw)
        print("=================================\n\n")
        return fallback



# 5. Regression Equations
def comment_length_reg(comment_len):
    return 40.33 - 4.36 * math.log(comment_len)

def relevance_reg(percent_rel):
    return 39.88 - 24.85 * math.log(percent_rel)

def tone_reg(percent_tone):
    return 109.47 + 18.29 * math.log(percent_tone)

def toxicity_reg(percent_tox):
    return 126.12 + 30.66 * math.log(percent_tox)



# 6. Calculator View
def calculator(request):
    context = {}

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        comment = request.POST.get("comment", "").strip()

        # Save original text for display
        context["title"] = title
        context["comment"] = comment

        # Cleaned text for LLM
        clean_title = clean_text(title)
        clean_comment = clean_text(comment)

        
        # 1. Length checks
        title_len = len(title)
        comment_len = len(comment)

        context["title_len"] = title_len
        context["comment_len"] = comment_len

        if comment_len < 50:
            context["rec_comment_length"] = (
                "Your comment is shorter than recommended. "
                "Consider adding more detail to improve clarity."
            )

        
        # 2. Comment length regression
        try:
            rt_comment = comment_length_reg(comment_len)
        except:
            rt_comment = "na"

        context["rt_comment"] = rt_comment

        
        # 3. Tone + Relevance LLM
        tone_rel_prompt = f"""
Analyze the following issue.

Summary: {clean_title}
Description: {clean_comment}

Respond ONLY with valid JSON.
No explanations. No markdown. No extra text.

Return exactly:
{{
  "tone": "",
  "tone_keywords": "",
  "relevant": "",
  "relevant_keywords": ""
}}
"""

        tone_rel_raw = run_llm(tone_rel_prompt)

        tone_rel = safe_json_loads(
            tone_rel_raw,
            {
                "tone": "neutral",
                "tone_keywords": "",
                "relevant": "Yes",
                "relevant_keywords": ""
            }
        )

        tone = tone_rel.get("tone", "neutral")
        relevant = tone_rel.get("relevant", "Yes")
        tone_keywords = tone_rel.get("tone_keywords", "")
        relevant_keywords = tone_rel.get("relevant_keywords", "")

        context["tone"] = tone
        context["relevant"] = relevant
        context["tone_keywords"] = tone_keywords
        context["relevant_keywords"] = relevant_keywords

        
        # 4. Relevance regression
        if relevant.lower() == "yes" and relevant_keywords:
            rel_len = len(relevant_keywords)
            percent_rel = rel_len / max(title_len, 1)

            try:
                rt_relevance = relevance_reg(percent_rel)
            except:
                rt_relevance = "na"

            context["rt_relevance"] = rt_relevance
        else:
            context["rt_relevance"] = "na"
            context["rec_relevance"] = (
                "Your comment may not be relevant to the issue title. "
                "Consider improving clarity or alignment."
            )

        
        # 5. Tone regression
        if tone.lower() not in ["neutral", "professional"] and tone_keywords:
            tone_len = len(tone_keywords)
            percent_tone = tone_len / max(comment_len, 1)

            try:
                rt_tone = tone_reg(percent_tone)
            except:
                rt_tone = "na"

            context["rt_tone"] = rt_tone
            context["rec_tone"] = (
                "Your tone may be perceived as unprofessional. "
                f"The following keywords are contributing to the tone: {tone_keywords}"
            )
        else:
            context["rt_tone"] = "na"

        
        # 6. Toxicity detection (Hybrid)
        profanity_hits = detect_profanity(comment)
        context["profanity_hits"] = profanity_hits

        tox_prompt = f"""
Identify toxic words in the following text.

Text: {clean_comment}

Respond ONLY with valid JSON:
{{
  "toxic_keywords": ""
}}
"""

        tox_raw = run_llm(tox_prompt)

        tox = safe_json_loads(
            tox_raw,
            {"toxic_keywords": ""}
        )

        llm_toxic_keywords = tox.get("toxic_keywords", "")

        # Normalize to list
        if isinstance(llm_toxic_keywords, str):
            llm_list = llm_toxic_keywords.split()
        elif isinstance(llm_toxic_keywords, list):
            llm_list = llm_toxic_keywords
        else:
            llm_list = []

        combined_toxic = set()

        if profanity_hits:
            combined_toxic.update(profanity_hits)

        combined_toxic.update(llm_list)
        combined_toxic = list(combined_toxic)
        context["toxic_keywords"] = ", ".join(combined_toxic)

        
        # 7. Toxicity regression
        if combined_toxic:
            tox_len = len(" ".join(combined_toxic))
            percent_tox = tox_len / max(comment_len, 1)

            try:
                rt_tox = toxicity_reg(percent_tox)
            except:
                rt_tox = "na"

            context["rt_tox"] = rt_tox
            context["rec_toxicity"] = (
                "Your comment contains harmful or inappropriate language. "
                f"Consider removing: {', '.join(combined_toxic)}"
            )
        else:
            context["rt_tox"] = "na"

        
        # 8. Final predicted resolution time
        values = [
            v for v in [
                context["rt_comment"],
                context["rt_relevance"],
                context["rt_tone"],
                context["rt_tox"]
            ] if v != "na"
        ]

        context["final_prediction"] = sum(values) / len(values) if values else "na"

    return render(request, "calculator.html", context)



# 7. Basic Pages
def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')