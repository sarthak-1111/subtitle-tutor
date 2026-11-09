# Stand-in run: notfound

Title not in the library: must stop without offering another title.

Model `gpt-oss:120b` served by Ollama on a PC, not the NAS. The experts, the approval prompt and the user are emulated by `testbed/emulator.py`. Date 2026-11-09.

## user

````text
Make a French lesson from Casablanca. I speak English.
````

## assistant

````text

[tool call] delegate --target media-agent --instruction 'Search the NAS video library for movies and TV series whose title matches Casablanca. Read only: do not start playback and do not change anything. For every match return the exact title, the year, whether it is a movie or a series, the media ID, and the real file path of the video file. If there are no results, return an empty list and say so. Do not return similar or unrelated titles as matches.'
````

## expert

````text
{"status": "completed", "data": {"items": [], "note": "no results"}}
````

## assistant

````text
I could not find a title matching **Casablanca** in the NAS media library.  

END OF TASK
````

