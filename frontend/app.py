import os
import base64
import dotenv
import flask
import json

app = flask.Flask(__name__)

# Definition of the global variables
dotenv.load_dotenv("config.env")


def loadScores():
    """
    Load scores from the scores.json file located in the parent directory.

    Returns:
        dict: A dictionary containing the scores and maximum score.
    """
    parentDir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    scoreDir = os.path.join(parentDir, "score")

    # Intialize the data structure
    data = {"score": [], "maximumScore": {}}

    mas_stage_path = os.path.join(scoreDir, "maxStage.json")
    if os.path.exists(mas_stage_path):
        with open(mas_stage_path) as f:
            data["maximumScore"] = json.load(f)["maximumScore"]

    # Load all trigram score files
    for filename in os.listdir(scoreDir):
        if filename.endswith(".json") and len(os.path.splitext(filename)[0]) == 3:
            file_path = os.path.join(scoreDir, filename)
            trigram = os.path.splitext(filename)[0]
            with open(file_path) as f:
                file_data = json.load(f)
                file_data["player"] = trigram
                data["score"].append(file_data)

    print("Loaded scores from:", data)

    # Sort scores by player name
    data["score"].sort(key=lambda x: (x["value"], x["lastUpdated"]), reverse=True)
    return data


@app.route("/")
@app.route("/terminal")
def terminal():
    """
    Render the page for in Browser SSH terminal.

    Returns:
        str: Rendered HTML of the terminal page.
    """
    return flask.render_template(
        "terminal.html",
        hostname=os.getenv("FRONTENDHOST"),
        username=os.getenv("HOSTSSHUSERNAME"),
        password=base64.b64encode(os.getenv("HOSTSSHPASSWORD").encode("ascii")).decode(
            "utf-8"
        ),
    )


@app.route("/ssh")
def ssh():
    """
    Render the page for in Browser SSH terminal.

    Returns:
        str: Rendered HTML of the terminal page.
    """
    return flask.render_template(
        "terminal2.html",
        hostname=os.getenv("FRONTENDHOST"),
        username=os.getenv("PLAYERSSHUSERNAME"),
        password=base64.b64encode(
            os.getenv("PLAYERSSHPASSWORD").encode("ascii")
        ).decode("utf-8"),
    )


@app.route("/scoreboard")
def scoreBoard():
    """
    Render the scoreboard page with scores and maximum score.

    Returns:
        str: Rendered HTML of the scoreboard page.
    """
    data = loadScores()
    return flask.render_template(
        "scoreboard.html", maximumScore=data["maximumScore"], scores=data["score"]
    )


@app.route("/combined")
def combined_scoreboard():
    """
    Combine scoreboards from multiple clusters by parsing their HTML.
    Returns:
        str: Rendered HTML of the combined scoreboard page.
    """
    import requests
    import re
    import ipaddress

    def parse_scoreboard_html(url):
        """Parse HTML scoreboard page to extract scores using regex"""
        scores = []
        max_score = 100

        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                html = response.text

                # Remove newlines to make regex easier
                html = html.replace("\n", " ").replace("\r", "")

                # Extract max score from aria-valuemax
                max_match = re.search(r'aria-valuemax="(\d+)"', html)
                if max_match:
                    max_score = int(max_match.group(1))

                # Find all agent blocks - pattern for the complete col div
                pattern = r'<div class="col-[^"]*">\s*<div class="mb-3">\s*<h5>(\d+)\.\s*Agent:\s*([^(]+)\s*a\.k\.a\.\s*([^(]+)\s*\((\d+)%\)</h5>.*?<div class="progress".*?aria-valuenow="(\d+)".*?</div>\s*<div>\s*([^<]+)\s*</div>'

                matches = re.finditer(pattern, html, re.DOTALL)

                for match in matches:
                    # No need of rank = match.group(1)
                    agent_username = match.group(2).strip()
                    agent_trigram = match.group(3).strip()
                    # No need of percentage = int(match.group(4))
                    aria_value = int(match.group(5))
                    timing_text = match.group(6).strip()

                    score_entry = {
                        "player": agent_trigram,
                        "value": aria_value,  # Use aria-valuenow directly
                        "lastUpdated": "",
                        "finishedTime": "",
                        "duration": "",
                        "username": agent_username,
                    }

                    # Parse timing info
                    if "Finished at" in timing_text:
                        finished_match = re.search(
                            r"Finished at\s*([^/]+?)\s*/\s*Duration:\s*(.+)",
                            timing_text,
                        )
                        if finished_match:
                            score_entry["finishedTime"] = finished_match.group(
                                1
                            ).strip()
                            score_entry["duration"] = finished_match.group(2).strip()
                    elif "Last updated at" in timing_text:
                        updated_match = re.search(
                            r"Last updated at\s*(.+)", timing_text
                        )
                        if updated_match:
                            score_entry["lastUpdated"] = updated_match.group(1).strip()

                    scores.append(score_entry)

        except Exception as e:
            print(f"Error parsing {url}: {e}")

        return scores, max_score

    # Get Scoreboards IPs from environment variable
    scoreboard_ips = os.getenv("COMBINEDSCOREBOARDS")
    if not scoreboard_ips:
        scoreboard_ips = os.getenv("FRONTENDHOST")

    if not scoreboard_ips:
        return flask.render_template("combined.html", maximumScore=0, scores=[])

    # Force specific IPs for testing.
    # scoreboard_ips = "10.42.91.100,10.42.169.120"

    # Initialize combined scores and max score
    all_scores = []
    max_score = 0

    # Parse Scoreboards IPs and get scores information
    scoreboard_index = 0
    for scoreboard_ip in scoreboard_ips.split(","):
        current_scoreboard_ip = scoreboard_ip.strip()
        try:
            ipaddress.ip_address(current_scoreboard_ip)

            # Get current URLs from query parameters
            current_scoreboard_url = flask.request.args.get("scoreboard" + str(scoreboard_index), "http://" + current_scoreboard_ip + ":8080/scoreboard")

            # Parse the current scoreboard
            current_scoreboard_scores, current_scoreboard_max_score = parse_scoreboard_html(current_scoreboard_url)
            if scoreboard_index == 0:
                all_scores = current_scoreboard_scores
                max_score = current_scoreboard_max_score
            else:
                all_scores += current_scoreboard_scores
                max_score = max(max_score, current_scoreboard_max_score) if current_scoreboard_max_score else max_score

        except ValueError:
            pass

        scoreboard_index += 1

    # Use the same template as the original scoreboard
    return flask.render_template(
        "combined.html", maximumScore=max_score, scores=all_scores
    )


if __name__ == "__main__":
    app.run(host=os.getenv("FRONTENDHOST"), port=os.getenv("FRONTENDPORT"), debug=True)
