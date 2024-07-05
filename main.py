import magic
import subprocess

from pathlib import Path

from ulauncher.api import Extension, Result
from ulauncher.api.shared.action.RunScriptAction import RunScriptAction
from ulauncher.modes.file_browser.get_icon_from_path import get_icon_from_path


ICON='utilities-terminal'


class Launchpad(Extension):
    def __init__(self):
        super().__init__()
        self.scripts = []

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
            matches = [i for i in self.scripts if query in i.name.lower()]

        if not matches:
            return [Result(icon=ICON,
                           name='No matches found',
                           description='Try to change the search pattern',
                           on_enter=True)]

        items = []
        for i in matches[:25]:
            path = str(i)
            items.append(Result(icon=get_icon_from_path(path),
                                name=i.name,
                                description=magic.detect_from_filename(path).mime_type,
                                compact=self.preferences['compact'],
                                highlightable=self.preferences['highlight'],
                                on_enter=RunScriptAction(path)))
        return items


if __name__ == '__main__':
    Launchpad().run()
