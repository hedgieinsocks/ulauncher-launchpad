import magic
import re
import subprocess

from pathlib import Path

from ulauncher.api import Extension, Result
from ulauncher.api.shared.action.RunScriptAction import RunScriptAction
from ulauncher.utils.fuzzy_search import get_score
from ulauncher.utils.get_icon_path import get_icon_path
from ulauncher.modes.file_browser.get_icon_from_path import get_icon_from_path


ICON='utilities-terminal'


class Launchpad(Extension):
    def __init__(self):
        super().__init__()
        self.scripts = []

    def get_metadata(self, item):
        metadata = {'icon': None, 'description': None}
        pattern_icon = r'#\s*icon:\s*(.*)'
        pattern_description = r'#\s*description:\s*(.*)'
        path = str(item)

        with item.open('r') as file:
            for line in file.readlines()[:10]:
                match_icon = re.search(pattern_icon, line, re.IGNORECASE)
                if match_icon:
                    icon = match_icon.group(1).strip()
                    if not icon.startswith("/"):
                        metadata['icon'] = get_icon_path(icon) or ICON
                    else:
                        metadata['icon'] = icon
                match_description = re.search(pattern_description, line, re.IGNORECASE)
                if match_description:
                    metadata['description'] = match_description.group(1).strip()

        if not metadata['icon']:
            metadata['icon'] = get_icon_from_path(path)
        if not metadata['description']:
            metadata['description'] = magic.detect_from_filename(path).mime_type

        return metadata

    def on_input(self, input_text, trigger_id):
        query = input_text.lower().strip()

        if not query:
            if not self.preferences['scripts_dir']:
                return [Result(icon=ICON,
                               name='The scripts directory is not configured',
                               description='Set the scripts directory in the extension settings',
                               on_enter=True)]

            scripts_dir = Path(self.preferences['scripts_dir']).expanduser()
            if not scripts_dir.is_dir():
                return [Result(icon=ICON,
                               name='The configured scripts directory does not exist',
                               description='Double-check the scripts directory in the extension settings',
                               on_enter=True)]

            self.scripts = [f for f in scripts_dir.iterdir() if f.is_file()]
            if not self.scripts:
                return [Result(icon=ICON,
                               name='No scripts found',
                               description='Place the scripts into the scripts directory',
                               on_enter=True)]

            matches = self.scripts
        else:
            if trigger_id == 'fuzzy':
                fuzzy_scores = sorted(self.scripts, key=lambda fn: get_score(query, fn.name.lower()), reverse=True)
                matches = list(filter(lambda fn: get_score(query, fn.name.lower()) > self.preferences['threshold'], fuzzy_scores))
            else:
                matches = [i for i in self.scripts if query in i.name.lower()]

        if not matches:
            return [Result(icon=ICON,
                           name='No matches found',
                           description='Try to change the search pattern',
                           on_enter=True)]

        items = []
        for i in matches[:25]:
            metadata = self.get_metadata(i)
            items.append(Result(icon=metadata['icon'],
                                name=i.name,
                                description=metadata['description'],
                                compact=self.preferences['compact'],
                                highlightable=self.preferences['highlight'],
                                on_enter=RunScriptAction(str(i))))
        return items


if __name__ == '__main__':
    Launchpad().run()
