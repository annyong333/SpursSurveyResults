"""Survey generator — creates Google Forms surveys and fetches responses.

Uses the Google Forms API v1 with service account credentials for
creating post-match rating surveys and retrieving responses.
"""

from __future__ import annotations

import logging
import os
from typing import Any

from spurs_survey.models import MatchData

logger = logging.getLogger(__name__)

# Rating scale descriptions shown once at the top of the survey.
RATING_SCALE_DESCRIPTION = (
    "Rating Scale Guide:\n"
    "0 — Worst Performance of the Year Contender\n"
    "1 — Abysmal\n"
    "2 — Very Poor\n"
    "3 — Poor\n"
    "4 — Below Average\n"
    "5 — Average\n"
    "6 — Above Average\n"
    "7 — Good\n"
    "8 — Very Good\n"
    "9 — Excellent\n"
    "10 — Perfect Performance"
)

# 0–10 integer choices used for every rating question.
RATING_CHOICES = [str(i) for i in range(11)]


# ---------------------------------------------------------------------------
# Section type constants
# ---------------------------------------------------------------------------

SECTION_RATING_SCALE = "rating_scale_description"
SECTION_TEAM_RATING = "team_rating"
SECTION_OPPONENT_RATING = "opponent_rating"
SECTION_COACH_STARTING_XI = "coach_starting_eleven"
SECTION_COACH_TACTICS = "coach_on_field_tactics"
SECTION_COACH_SUBS = "coach_substitutions"
SECTION_REFEREE_RATING = "referee_rating"
SECTION_STARTER_RATING = "starter_rating"
SECTION_SUB_RATING = "sub_rating"
SECTION_MOTM = "motm_vote"


# ---------------------------------------------------------------------------
# Pure survey structure builder (testable without API)
# ---------------------------------------------------------------------------

def build_survey_structure(match_data: MatchData) -> list[dict[str, Any]]:
    """Build the survey section definitions from match data.

    Returns a list of dicts, each describing one survey section/question.
    The order matches the requirements:
      1. Rating scale description header
      2. Team rating
      3. Opponent rating
      4. Coach ratings (3 questions)
      5. Referee rating
      6. Starting player ratings (one per starter)
      7. Substitute player ratings (one per sub, if any)
      8. Man of the Match vote

    Each dict has:
      - ``"type"``: one of the SECTION_* constants
      - ``"title"``: question/section title text
      - ``"choices"``: list of string options (for rating or MOTM)
      - ``"player_name"``: (player sections only) the player's name
    """
    sections: list[dict[str, Any]] = []

    opponent = (
        match_data.away_team
        if match_data.is_tottenham_home
        else match_data.home_team
    )

    # 1. Rating scale description header
    sections.append({
        "type": SECTION_RATING_SCALE,
        "title": "Rating Scale",
        "description": RATING_SCALE_DESCRIPTION,
        "choices": [],
    })

    # 2. Team rating
    sections.append({
        "type": SECTION_TEAM_RATING,
        "title": "Tottenham Hotspur — Team Rating",
        "choices": RATING_CHOICES,
    })

    # 3. Opponent rating
    sections.append({
        "type": SECTION_OPPONENT_RATING,
        "title": f"{opponent} — Team Rating",
        "choices": RATING_CHOICES,
    })

    # 4. Coach ratings (3 questions)
    coach_name = match_data.coach or "Manager"
    sections.append({
        "type": SECTION_COACH_STARTING_XI,
        "title": f"{coach_name} — Starting Eleven Selection",
        "choices": RATING_CHOICES,
    })
    sections.append({
        "type": SECTION_COACH_TACTICS,
        "title": f"{coach_name} — On-Field Tactics",
        "choices": RATING_CHOICES,
    })
    sections.append({
        "type": SECTION_COACH_SUBS,
        "title": f"{coach_name} — Substitution Decisions",
        "choices": RATING_CHOICES,
    })

    # 5. Referee rating
    sections.append({
        "type": SECTION_REFEREE_RATING,
        "title": "Referee Rating",
        "choices": RATING_CHOICES,
    })

    # 6. Starting player ratings
    for player in match_data.starting_players:
        sections.append({
            "type": SECTION_STARTER_RATING,
            "title": f"{player.name} — Rating",
            "choices": RATING_CHOICES,
            "player_name": player.name,
        })

    # 7. Substitute player ratings (only if there are subs)
    sub_names = [sub.player_in for sub in match_data.substitutions]
    for name in sub_names:
        sections.append({
            "type": SECTION_SUB_RATING,
            "title": f"{name} — Rating",
            "choices": RATING_CHOICES,
            "player_name": name,
        })

    # 8. Man of the Match vote
    all_player_names = [p.name for p in match_data.starting_players] + sub_names
    sections.append({
        "type": SECTION_MOTM,
        "title": "Man of the Match",
        "choices": all_player_names,
    })

    return sections


# ---------------------------------------------------------------------------
# Google Forms API integration
# ---------------------------------------------------------------------------

def _get_forms_service():
    """Build an authenticated Google Forms API service.

    Expects the environment variable ``GOOGLE_APPLICATION_CREDENTIALS`` to
    point to a service account JSON key file, or
    ``GOOGLE_FORMS_CREDENTIALS_FILE`` as an explicit override.
    """
    from google.oauth2 import service_account
    from googleapiclient.discovery import build

    creds_file = os.environ.get(
        "GOOGLE_FORMS_CREDENTIALS_FILE",
        os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", ""),
    )
    if not creds_file:
        raise RuntimeError(
            "No Google credentials found. Set GOOGLE_FORMS_CREDENTIALS_FILE "
            "or GOOGLE_APPLICATION_CREDENTIALS to a service account JSON key file."
        )

    scopes = [
        "https://www.googleapis.com/auth/forms.body",
        "https://www.googleapis.com/auth/forms.responses.readonly",
    ]
    credentials = service_account.Credentials.from_service_account_file(
        creds_file, scopes=scopes,
    )
    return build("forms", "v1", credentials=credentials)


def _build_form_requests(sections: list[dict[str, Any]]) -> list[dict]:
    """Convert our section dicts into Google Forms API batchUpdate requests."""
    requests_list: list[dict] = []
    index = 0

    for section in sections:
        sec_type = section["type"]

        if sec_type == SECTION_RATING_SCALE:
            # Add a text item (description only, no question)
            requests_list.append({
                "createItem": {
                    "item": {
                        "title": section["title"],
                        "description": section.get("description", ""),
                        "textItem": {},
                    },
                    "location": {"index": index},
                }
            })
            index += 1

        elif sec_type == SECTION_MOTM:
            # Multiple choice (radio) question
            requests_list.append({
                "createItem": {
                    "item": {
                        "title": section["title"],
                        "questionItem": {
                            "question": {
                                "required": False,
                                "choiceQuestion": {
                                    "type": "RADIO",
                                    "options": [
                                        {"value": name} for name in section["choices"]
                                    ],
                                },
                            }
                        },
                    },
                    "location": {"index": index},
                }
            })
            index += 1

        else:
            # Rating question — scale (0–10) as radio choices
            requests_list.append({
                "createItem": {
                    "item": {
                        "title": section["title"],
                        "questionItem": {
                            "question": {
                                "required": False,
                                "scaleQuestion": {
                                    "low": 0,
                                    "high": 10,
                                    "lowLabel": "Worst Performance of the Year Contender",
                                    "highLabel": "Perfect Performance",
                                },
                            }
                        },
                    },
                    "location": {"index": index},
                }
            })
            index += 1

    return requests_list


def create_survey(match_data: MatchData) -> str:
    """Create a Google Form survey and return the shareable (responder) link.

    Raises
    ------
    RuntimeError
        If Google credentials are not configured.
    """
    service = _get_forms_service()

    opponent = (
        match_data.away_team
        if match_data.is_tottenham_home
        else match_data.home_team
    )
    form_title = (
        f"r/coys Post-Match Ratings | "
        f"Tottenham vs {opponent} | "
        f"{match_data.competition} {match_data.matchday} | "
        f"{match_data.date}"
    )

    # Step 1: Create an empty form
    form_body = {"info": {"title": form_title}}
    created_form = service.forms().create(body=form_body).execute()
    form_id = created_form["formId"]
    responder_uri = created_form.get("responderUri", "")

    # Step 2: Build and apply the survey structure
    sections = build_survey_structure(match_data)
    api_requests = _build_form_requests(sections)

    if api_requests:
        service.forms().batchUpdate(
            formId=form_id,
            body={"requests": api_requests},
        ).execute()

    logger.info("Created survey: %s (form_id=%s)", form_title, form_id)

    return responder_uri or f"https://docs.google.com/forms/d/{form_id}/viewform"


def fetch_responses(form_id: str) -> list[dict]:
    """Retrieve all responses from a Google Form.

    Returns a list of dicts, each keyed by question title with the
    respondent's answer as the value.
    """
    service = _get_forms_service()

    # Get the form structure to map question IDs → titles
    form = service.forms().get(formId=form_id).execute()
    qid_to_title: dict[str, str] = {}
    for item in form.get("items", []):
        question = item.get("questionItem", {}).get("question", {})
        qid = question.get("questionId")
        if qid:
            qid_to_title[qid] = item.get("title", "")

    # Fetch all responses
    resp = service.forms().responses().list(formId=form_id).execute()
    raw_responses = resp.get("responses", [])

    parsed: list[dict] = []
    for response in raw_responses:
        answers = response.get("answers", {})
        row: dict[str, str] = {}
        for qid, answer_data in answers.items():
            title = qid_to_title.get(qid, qid)
            text_answers = answer_data.get("textAnswers", {}).get("answers", [])
            if text_answers:
                row[title] = text_answers[0].get("value", "")
        parsed.append(row)

    return parsed
