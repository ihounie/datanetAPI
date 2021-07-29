import argparse
from pathlib import Path
import datanetAPI
path = 'dataset' # to do add argparsing and CLI
Path(path).mkdir(parents=True, exist_ok=True)
reader = datanetAPI.DatanetAPI(path,[],False)