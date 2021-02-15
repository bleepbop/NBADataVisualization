# NBADataVisualization

A simple Dash app that can be used to visualize NBA statistics of the users choice. Simply select a team and parameters for the X and Y axes.
Each datapoint will have a color associated with a player on the selected team. 
The size of the datapoint corresponds to the team's win percentage for the games in which the selected player has logged minutes.

There are two ways to run the app. First, navigate to the project directory.
Then enter the following commands:

  With Python3:

  `pip install -r requirements.txt`

  `python3 src/dash_graphs.py`
  
  With Docker:

  `docker build -t nba_viz .`

  `docker run -dp 8000:8000 nba_viz`

Navigate to 0.0.0.0:8000, and you should see an instance of the project up and running.
