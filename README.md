# annovis
Visualize offset-based annotations of text spans as SVG.

# Setup Python Virtual Environment

```zsh
$ python3 -m venv annovis
...
$ source annovis/bin/activate
(annovis) $ pip3 install -r requirements
...
```

# Visualize Annotations from JSON

Let's take the provided `data.json` as an example:

```zsh
$ cat data.json 
{
  "text" :"Jane Doe is a software engineer.\nShe works at Acme.\n‍🧙‍♀️✨ emojis!\nPortsmouth, NH",
  "annotations": [
      {"start": 0, "end": 63, "label": "*"},
      {"start": 0, "end": 8, "label": "PERSON"},
      {"start": 14, "end": 31, "label": "OCCUPATION"},
      {"start": 31, "end": 34, "label": "MULTILINE"},
      {"start": 31, "end": 36, "label": "MULTILINE"},
      {"start": 33, "end": 36, "label": "PERSON"},
      {"start": 46, "end": 50, "label": "ORGANIZATION"},
      {"start": 52, "end": 56, "label": "EMOJIS"},
      {"start": 52, "end": 54, "label": "EMOJI"},
      {"start": 54, "end": 56, "label": "EMOJI"},
      {"start": 67, "end": 77, "label": "CITY"},
      {"start": 77, "end": 81, "label": "STATE"},
      {"start": 67, "end": 81, "label": "LOCATION"}
  ]
}
```

We can visualize this as SVG as follows:

```zsh
$ ./annovis.py -h
usage: annovis.py [-h] [-o OUTPUT] input

positional arguments:
  input                 input JSON file with "text" and "annotations"

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        path to output file where SVG visualization will be
                        written (default: annotations.svg)
$ ./annovis.py data.json
Writing SVG to: annotations.svg
```

![annotation.svg](annotations.svg "Annotations as SVG")

# TODO
* Fix the vertical padding within the label area
* Find a better way to visualize annotations that span multiple lines?
* Soft line wrapping?
* Allow for visualizing more complex annotations, such as relationships