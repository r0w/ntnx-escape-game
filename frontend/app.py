from dotenv import load_dotenv

from flask import Flask, render_template, request
import json, os, base64

app = Flask(__name__)

# Definition of the global variables
load_dotenv('config.env')

def loadScores():
    """
    Load scores from the scores.json file located in the parent directory.

    Returns:
        dict: A dictionary containing the scores and maximum score.
    """
    parentDir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    scoreDir = os.path.join(parentDir, 'score')
    
    # Intialize the data structure
    data = {"score": [], "maximumScore": {}}
    
    mas_stage_path = os.path.join(scoreDir, 'maxStage.json')
    if os.path.exists(mas_stage_path):
        with open(mas_stage_path) as f:
            data["maximumScore"] = json.load(f)['maximumScore']
    
    # Load all trigram score files
    for filename in os.listdir(scoreDir):
        if filename.endswith('.json') and len(os.path.splitext(filename)[0]) == 3:
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

@app.route('/')
@app.route('/terminal')
def terminal():
    """
    Render the page for in Browser SSH terminal.

    Returns:
        str: Rendered HTML of the terminal page.
    """
    return render_template('terminal.html', hostname=os.getenv('FRONTENDHOST'), username=os.getenv('HOSTSSHUSERNAME'), password=base64.b64encode(os.getenv('HOSTSSHPASSWORD').encode("ascii")).decode('utf-8'))

@app.route('/ssh')
def ssh():
    """
    Render the page for in Browser SSH terminal.

    Returns:
        str: Rendered HTML of the terminal page.
    """
    return render_template('terminal2.html', hostname=os.getenv('FRONTENDHOST'), username=os.getenv('PLAYERSSHUSERNAME'), password=base64.b64encode(os.getenv('PLAYERSSHPASSWORD').encode("ascii")).decode('utf-8'))

@app.route('/scoreboard')
def scoreBoard():
    """
    Render the scoreboard page with scores and maximum score.

    Returns:
        str: Rendered HTML of the scoreboard page.
    """
    data = loadScores()
    return render_template('scoreboard.html', maximumScore=data["maximumScore"], scores=data["score"])

@app.route('/combined')
def combined_scoreboard():
    """
    Combine scoreboards from multiple clusters by parsing their HTML.
    Returns:
        str: Rendered HTML of the combined scoreboard page.
    """
    import requests
    import re
    
    # Get URLs from query parameters
    url1 = request.args.get('c1', 'http://cluster1/scoreboard')
    url2 = request.args.get('c2', 'http://cluster2/scoreboard')
    
    def parse_scoreboard_html(url):
        """Parse HTML scoreboard page to extract scores using regex"""
        scores = []
        max_score = 100
        
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                html = response.text
                
                # Remove newlines to make regex easier
                html = html.replace('\n', ' ').replace('\r', '')
                
                # Extract max score from aria-valuemax
                max_match = re.search(r'aria-valuemax="(\d+)"', html)
                if max_match:
                    max_score = int(max_match.group(1))
                
                # Find all agent blocks - pattern for the complete col div
                pattern = r'<div class="col-[^"]*">\s*<div class="mb-3">\s*<h5>(\d+)\.\s*Agent:\s*([^(]+)\s*\((\d+)%\)</h5>.*?<div class="progress".*?aria-valuenow="(\d+)".*?</div>\s*<div>\s*([^<]+)\s*</div>'
                
                matches = re.finditer(pattern, html, re.DOTALL)
                
                for match in matches:
                    rank = match.group(1)
                    player_name = match.group(2).strip()
                    percentage = int(match.group(3))
                    aria_value = int(match.group(4))
                    timing_text = match.group(5).strip()
                    
                    score_entry = {
                        'player': player_name,
                        'value': aria_value,  # Use aria-valuenow directly
                        'lastUpdated': '',
                        'finishedTime': '',
                        'duration': ''
                    }
                    
                    # Parse timing info
                    if 'Finished at' in timing_text:
                        finished_match = re.search(r'Finished at\s*([^/]+?)\s*/\s*Duration:\s*(.+)', timing_text)
                        if finished_match:
                            score_entry['finishedTime'] = finished_match.group(1).strip()
                            score_entry['duration'] = finished_match.group(2).strip()
                    elif 'Last updated at' in timing_text:
                        updated_match = re.search(r'Last updated at\s*(.+)', timing_text)
                        if updated_match:
                            score_entry['lastUpdated'] = updated_match.group(1).strip()
                    
                    scores.append(score_entry)
                        
        except Exception as e:
            print(f"Error parsing {url}: {e}")
        
        return scores, max_score
    
    # Parse both scoreboards
    scores1, max1 = parse_scoreboard_html(url1)
    scores2, max2 = parse_scoreboard_html(url2)
    
    # Combine all scores
    all_scores = scores1 + scores2
    max_score = max(max1, max2) if (max1 or max2) else 100
    
    # Use the same template as the original scoreboard
    return render_template('scoreboard.html', 
                         maximumScore=max_score, 
                         scores=all_scores)

    maximumScore = 100
    return render_template('scoreboard.html', scores=scores, maximumScore=maximumScore)

if __name__ == '__main__':
    app.run(host=os.getenv('FRONTENDHOST'), port=os.getenv('FRONTENDPORT'), debug=True)
