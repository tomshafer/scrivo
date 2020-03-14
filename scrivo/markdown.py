"""
Custom Markdown extension for YAML metadata parsing.
"""
import logging
import re
from typing import Any, Dict, List

import yaml
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor

logger = logging.getLogger()


class YAMLMetadataExtension(Extension):
    """Parse YAML metadata at the top of a Markdown document"""
    def extendMarkdown(self, md):
        # Register our metadata preprocessor at the lower priority
        md.preprocessors.register(YAMLMetadataPreprocessor(md), 'yaml', 1)


class YAMLMetadataPreprocessor(Preprocessor):
    """Parse YAML metadata at the top of a Markdown document."""
    def run(self, lines: List[str]) -> List[str]:
        """Run the Preprocessor to extract any YAML block.

        Args:
            lines (list[str]): the lines of the input Markdown

        Returns:
            list[str]: the original Markdown minus the YAML content

            NB: This also has side-effects, setting 'self.md.metadata' to the
            extracted YAML content.

        """
        RE_YAML = re.compile(r'^(-|\.){3}$')

        yaml_start, yaml_end = None, None
        for i, line in enumerate(lines):
            if not line.strip():
                continue
            rx = RE_YAML.match(line.strip())
            # We're into text without ever seeing YAML
            if not rx and yaml_start is None:
                break
            # We see a YAML line and we haven't before
            if rx and yaml_start is None:
                yaml_start = i
                continue
            # We see a YAML line and we are tracking the YAML block
            if rx and yaml_start is not None:
                yaml_end = i
                break

        metadata: Dict[str, Any] = {}
        if yaml_start is None and yaml_end is None:
            new_lines = lines
        elif yaml_start is not None and yaml_end is not None:
            new_lines = lines[yaml_end+1:]
            metadata = yaml.safe_load('\n'.join(lines[yaml_start+1:yaml_end]))
        else:
            raise ValueError('did not find the end of the YAML header block')

        # lowercase the keys
        self.md.metadata = {k.lower(): v for k, v in metadata.items()}
        return new_lines
