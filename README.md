# Robatim
pronounced *row-bay-tum*

Robatim is a pseudo-random music generator based on the conventions of the common practice period.

## Requirements

* Requests

## Installation

```
git clone https://github.com/Sanseer/Robatim.git
```
```
pip install -r requirements.txt
```

## Usage examples

Generate randomly with either a major or minor scale
```
python main.py
```

Generate randomly with a major scale
```
pythom main.py -m major
```

Generate randomly within the key of G# minor
```
python main.py -t G# -m aeolian
```

