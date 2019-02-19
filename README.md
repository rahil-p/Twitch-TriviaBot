# Twitch-TriviaBot
a Twitch bot for overlaying custom trivia questions on a stream, capturing viewer responses in live chat, and tracking participants' scores

***DOCUMENTATION IN PROGRESS***

## Setup

### 1) Listing questions, answers, and values in /questions

In ***questions.csv***, use the outline:

* Column A: question id (e.g. q3)
* Column B: question text (e.g. *Which Spanish painter created the set of etchings "Los Caprichos", which included "The Sleep of Reason Produces Monsters," in the late 18th century?*)
* Column C and following: the set of options for each respective question

In ***answers.csv***, use the outline:
* Column A: question id
* Column B and following: correct option/s (integer such that Column C in *questions.csv* corresponds to option *1*, Column D in *questions.csv* corresponds to option *2*, and so forth)

In ***values.csv***
* Column A: question id
* Column B: value assigned to the question (numbers based on some value system)

### 2) Configuration for capturing Twitch chat

In OBS, link two separate browser sources to http://localhost:5000/display and http://localhost:5000/results.  These sources will display poll questions and results, respectively.

### 3) Launching the programs

In two separate terminal windows, run:
```
python overlay.py
```
and
```
python triviabot.py
```


## Usage

### Launch
In a terminal window, run:
```
python overlay.py
```

In a separate terminal window, run:
```
python triviabot.py
```

