"""djLint function to call cssbeautifier."""
from functools import partial

import cssbeautifier
import regex as re
from jsbeautifier.javascript.options import BeautifierOptions

from ..settings import Config


def format_css(html: str, config: Config) -> str:
    """Format css inside <style> tags."""

    def launch_formatter(config: Config, match: re.Match) -> str:
        """Add break after if not in ignored block."""
        if not match.group(3).strip():
            return match.group()

        indent = len(match.group(1)) * " "

        # because of the param options for js-beautifier we cannot pass
        # in a fixed space leading.
        # so, call formatter twice, once with a fake indent.
        # check which lines changed (these are the formattable lines)
        # and add the leading space to them.

        config.css_config["indent_level"] = 1
        opts = BeautifierOptions(config.css_config)
        beautified_lines = cssbeautifier.beautify(match.group(3), opts).splitlines()

        config.js_config["indent_level"] = 2
        opts = BeautifierOptions(config.js_config)
        beautified_lines_test = cssbeautifier.beautify(
            match.group(3), opts
        ).splitlines()

        beautified = ""
        for line, test in zip(beautified_lines, beautified_lines_test):
            beautified += "\n"
            if line == test:
                beautified += line
                continue
            beautified += indent + line

        return match.group(1) + match.group(2) + beautified + "\n" + indent

    func = partial(launch_formatter, config)

    return re.sub(
        re.compile(
            r"([ ]*?)(<(?:style)\b(?:\"[^\"]*\"|'[^']*'|{[^}]*}|[^'\">{}])*>)(.*?)(?=</style>)",
            re.IGNORECASE | re.DOTALL,
        ),
        func,
        html,
    )
