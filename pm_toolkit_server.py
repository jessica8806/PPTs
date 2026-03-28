"""
Standalone server for PM Operations Toolkit.
Run: python pm_toolkit_server.py
Then open http://localhost:5001/pm-toolkit
"""

import os
import json
import anthropic
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)


def _api_key():
    return os.environ.get("ANTHROPIC_API_KEY", "")


@app.route("/")
@app.route("/pm-toolkit")
def pm_toolkit():
    return render_template("pm_toolkit.html")


@app.route("/api/pm/triage", methods=["POST"])
def pm_triage():
    if not _api_key():
        return jsonify({"error": "ANTHROPIC_API_KEY not set on server"}), 500
    data = request.get_json(force=True)
    task_board = data.get("taskBoard", "")
    rush_request = data.get("rushRequest", "")

    client = anthropic.Anthropic(api_key=_api_key())
    system = (
        "You are an expert project management assistant at a digital marketing agency. "
        "When given a task board and a rush request, analyse team capacity and return a "
        "JSON object with exactly these keys:\n"
        "  lockedTasks: array of objects {name, hoursRemaining, dueDate, reason}\n"
        "  moveableTasks: array of objects {name, hoursRemaining, dueDate, suggestion}\n"
        "  timeline: string — a concise recommended timeline for the rush request\n"
        "  draftResponse: string — a fully written, professional client-facing message "
        "the PM can copy and send, confirming whether the rush can be accommodated and "
        "stating the timeline. Address it to the client from the rush request.\n"
        "Return ONLY the JSON object, no markdown fences, no extra text."
    )
    user_msg = (
        f"Current Task Board:\n{task_board}\n\n"
        f"Rush Request:\n{rush_request}"
    )
    try:
        resp = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            system=system,
            messages=[{"role": "user", "content": user_msg}],
        )
        result = json.loads(resp.content[0].text)
        return jsonify(result)
    except json.JSONDecodeError as e:
        return jsonify({"error": f"Failed to parse AI response: {e}", "raw": resp.content[0].text}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/pm/deadline-reset", methods=["POST"])
def pm_deadline_reset():
    if not _api_key():
        return jsonify({"error": "ANTHROPIC_API_KEY not set on server"}), 500
    data = request.get_json(force=True)
    client_name = data.get("clientName", "")
    project_name = data.get("projectName", "")
    original_deadline = data.get("originalDeadline", "")
    revised_deadline = data.get("revisedDeadline", "")
    reason = data.get("reason", "")
    additional_context = data.get("additionalContext", "")
    tone = data.get("tone", "Professional")

    client = anthropic.Anthropic(api_key=_api_key())
    system = (
        "You are an expert project management communication specialist. "
        "Write a client-facing deadline reset message that: "
        "(1) briefly acknowledges the change, "
        "(2) clearly states the revised timeline, "
        "(3) explains the reason without over-apologising, "
        "(4) ends with a specific next step or action item. "
        f"Tone: {tone}. "
        "Return ONLY the message text, no subject line, no JSON, no markdown. "
        "Write in first-person plural (we/our) as the agency team."
    )
    user_msg = (
        f"Client: {client_name}\n"
        f"Project: {project_name}\n"
        f"Original deadline: {original_deadline}\n"
        f"Revised deadline: {revised_deadline}\n"
        f"Reason for change: {reason}\n"
        f"Additional context: {additional_context}"
    )
    try:
        resp = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=800,
            system=system,
            messages=[{"role": "user", "content": user_msg}],
        )
        return jsonify({"message": resp.content[0].text.strip()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/pm/brief-audit", methods=["POST"])
def pm_brief_audit():
    if not _api_key():
        return jsonify({"error": "ANTHROPIC_API_KEY not set on server"}), 500
    data = request.get_json(force=True)
    brief = data.get("brief", "")
    deliverable = data.get("deliverable", "")
    deliverable_type = data.get("deliverableType", "Copy")

    client = anthropic.Anthropic(api_key=_api_key())
    system = (
        "You are a rigorous quality assurance specialist at a digital marketing agency. "
        "Compare a deliverable against its original brief and surface every gap. "
        "Return a JSON object with exactly these keys:\n"
        "  summary: object {met: number, partial: number, missing: number}\n"
        "  requirements: array of objects {requirement: string, status: 'Met'|'Partial'|'Missing', note: string}\n"
        "  revisionBrief: string — a single consolidated message the PM can paste and send "
        "directly to the team listing all flagged items with clear instructions for each.\n"
        "Extract every distinct requirement from the brief and evaluate each one. "
        "Return ONLY the JSON object, no markdown fences, no extra text."
    )
    user_msg = (
        f"Deliverable Type: {deliverable_type}\n\n"
        f"Original Brief:\n{brief}\n\n"
        f"Deliverable:\n{deliverable}"
    )
    try:
        resp = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            system=system,
            messages=[{"role": "user", "content": user_msg}],
        )
        result = json.loads(resp.content[0].text)
        return jsonify(result)
    except json.JSONDecodeError as e:
        return jsonify({"error": f"Failed to parse AI response: {e}", "raw": resp.content[0].text}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("\n  PM Operations Toolkit → http://localhost:5001/pm-toolkit\n")
    app.run(host="0.0.0.0", port=5001, debug=False)
