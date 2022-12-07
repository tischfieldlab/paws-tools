"""Module contains utility functions."""

import click


def click_monkey_patch_option_show_defaults():
    """Monkey patch click.core.Option to turn on showing default values."""
    orig_init = click.core.Option.__init__

    def new_init(self, *args, **kwargs):
        """This version of click.core.Option.__init__ will set show default values to True."""
        orig_init(self, *args, **kwargs)
        self.show_default = True

    # end new_init()
    click.core.Option.__init__ = new_init  # type: ignore
