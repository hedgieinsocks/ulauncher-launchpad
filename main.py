import magic
import subprocess

from pathlib import Path

from ulauncher.api import Extension, Result
from ulauncher.api.shared.action.RunScriptAction import RunScriptAction
from ulauncher.modes.file_browser.get_icon_from_path import get_icon_from_path


ICON='utilities-terminal'


class Launchpad(Extension):

    def on_input(self, input_text, trigger_id):

        scripts_dir = Path(self.preferences['scripts_dir'] or '~').expanduser().resolve()
        if not scripts_dir.is_dir():
            return [Result(icon=ICON,
                           name='The provided directory does not exist',
                           description=f'Ensure that {scripts_dir} directory exists',
                           on_enter=True)]

        scripts = [f for f in scripts_dir.iterdir() if f.is_file()]
        if not scripts:
            return [Result(icon=ICON,
                           name='No scripts found',
                           description=f'Place the scripts into {scripts_dir}',
                           on_enter=True)]

        if not input_text:
            matches = scripts
        else:
            matches = [i for i in scripts if input_text.lower() in i.name.lower()]

        if not matches:
            return [Result(icon=ICON,
                           name='No matches found',
                           description='Try to change the search request',
                           on_enter=True)]

        items = []
        for i in matches[:25]:
            path = str(i)
            items.append(Result(icon=get_icon_from_path(path),
                                name=i.name,
                                description=magic.detect_from_filename(path).mime_type,
                                on_enter=RunScriptAction(path)))
        return items


if __name__ == '__main__':
    Launchpad().run()
