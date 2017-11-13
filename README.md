# dumbphone directions

Get directions from Google maps and send to your phone. Will export as a single HTML file with images included as base64 encoded PNGs.

## Setup

This project is set up with [pipenv](https://github.com/kennethreitz/pipenv). Maybe overkill but that's the way I like it.

You'll need to set up a `.env` file with the following environment variables set:

```bash
DUMBP_GMAPS_API_KEY=set_this_to_your_key
DUMBP_HOME_ADDRESS="1234 Main St., Somewheresville, AP"
```

## Usage

Run the script:

```bash
pipenv run python directions.py
```

You'll be prompted for everything else.