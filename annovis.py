#!/usr/bin/env python3

import json
import sys

from dataclasses import dataclass
from dataclasses import field
from svgwrite import Drawing
from pathlib import Path
from operator import attrgetter

def extent(obj):
    """Get a (obj.start, obj.end) tuple from an object with start/end offset attributes"""
    try:
        start = attrgetter('start')(obj)
    except AttributeError:
        start = -1
    try:
        end = attrgetter('end')(obj)
    except AttributeError:
        end = -1
    return start, end

def overlaps(*objs):
    """Given any number of objects that have .start and .end attributes, find the offsets that overlap amongst them"""
    return set.intersection(*(set(range(*extent(obj))) for obj in objs))

def find_annotations(line, annotations):
    """Find all annotations whose start/end offsets overlap with the start/end offsets fo the given line"""
    return (a for a in annotations if overlaps(a, line))

@dataclass
class Annotation:
    """dataclass to model textual annotations with a label, and start/end character offsets"""
    label: str
    start: int = -1
    end: int = -1
    y: int = 0

@dataclass
class Line:
    """dataclass to model a line of text that also has an associated tuple of Annotations"""
    text: str
    start : int = -1
    end: int = -1
    annotations: tuple[Annotation] = field(default_factory=tuple)

@dataclass
class Visualization:
    """Class that can visualize character start/end offset annotations referring to text"""
    text: str
    annotations: tuple[Annotation] = field(default_factory=tuple)
    outfile: Path = Path('visualization.svg')
    font_size: int = 1
    padding: int = 12
    
    def __post_init__(self):
        self.lines = tuple(sorted(self.get_lines(), key=extent))
        self.annotations = tuple(sorted(self.annotations, key=extent))
        self.set_annotations_per_line()
        self.offset_annotation_labels()
    
    def get_lines(self):
        """Generate lines in the text with their character start/end offsets"""
        start = 0
        for line in self.text.splitlines(keepends=True):
            end = start + len(line)
            yield Line(text=line, start=start, end=end)
            start = end
    
    def set_annotations_per_line(self):
        """Associate annotations with the lines of text that their character offsets overlap with"""
        for line in self.lines:
            line.annotations = tuple(sorted(find_annotations(line, self.annotations), key=extent))
    
    def offset_annotation_labels(self):
        """Set annotation.y offsets so they don't overlap"""
        for line in self.lines:
            previous, annotations = line.annotations[0], line.annotations[1:]
            for annotation in annotations:
                if any((
                    overlaps(annotation, previous), # overlapping spans
                    #TODO: handle other conditions like long label strings
                )):
                    annotation.y = previous.y + 1
                previous = annotation
    
    def draw(self):
        """Draw the annotations as SVG"""
        drawing = Drawing(self.outfile)
        font_x_pixels = self.font_size * 7.8
        font_y_pixels = self.font_size * 12
        label_y_pixels = font_y_pixels / 2.0
        left_pad = self.padding * self.font_size
        y = 0
        # draw lines
        for line in self.lines:
            max_labels = max(ann.y for ann in line.annotations)
            #print(f'{max_labels=}, {line.text=}')
            label_area_height = label_y_pixels * max_labels
            #print(f'{label_area_height=}')
            y += (font_y_pixels * 2) + label_area_height
            drawing.add(
                drawing.text(
                    text=line.text,
                    insert=(left_pad, y),
                    font_family='monospace',
                    font_size=f'{self.font_size}em'
                )
            )
            # draw annotations
            for annotation in line.annotations:
                #print(annotation)
                x1 = left_pad + (annotation.start - line.start) * font_x_pixels
                x2 = left_pad + (annotation.end - line.start) * font_x_pixels
                y1 = y - font_y_pixels
                rect_height = font_y_pixels + (label_y_pixels * annotation.y)
                # handle multiline annotations
                if annotation.start < line.start:
                    x1 = -3
                    rect_width = x2 + 3
                if annotation.end > line.end:
                    x2 = line.end
                    rect_width = '200%'
                else:
                    rect_width = x2 - x1
                rect_y_offset = -(label_y_pixels * annotation.y) + (label_y_pixels / 2.0) - 2
                drawing.add(
                    drawing.rect(
                        insert=(x1, y1 + rect_y_offset),
                        size=(rect_width, rect_height),
                        fill='none',
                        stroke='red',
                        rx='3px',
                        ry='3px',
                        stroke_width=1
                    )
                )
                label_y_offset = -(annotation.y * label_y_pixels)
                drawing.add(
                    drawing.text(
                        text=(annotation.label if annotation.start >= line.start else f'⋯{annotation.label}'),
                        insert=(x1 if annotation.start >= line.start else x1 + 3, y1 + label_y_offset),
                        font_family='monospace',
                        font_size=f'{self.font_size / 2.0}em',
                        fill='red'
                    )
                )
        return drawing
        
    def save(self):
        self.draw().save()

def main(args):
    """Load input data and save SVG visualization to file"""
    with args.input as infile:
        data = json.load(infile)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    visualization = Visualization(
        text=data['text'],
        annotations=[Annotation(**ann) for ann in data['annotations']],
        outfile=args.output
    )
    print('Writing SVG to:', args.output.as_posix(), file=sys.stderr)
    visualization.save()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description=__doc__
    )
    parser.add_argument(
        'input',
        type=argparse.FileType('r'),
        help='input JSON file with "text" and "annotations"',
    )
    parser.add_argument(
        '-o', '--output',
        type=Path,
        default='annotations.svg',
        help='path to output file where SVG visualization will be written',
    )
    args = parser.parse_args()
    main(args)
