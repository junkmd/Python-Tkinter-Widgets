"""Entries with validator."""

import tkinter as tk
from numbers import Number
from unicodedata import east_asian_width


class Validation(object):
    """Container for the properties of a validation."""
    def __init__(self, widget, **kw):
        self.__widget = widget
        self.__kw = kw

    @property
    def type_of_action(self):
        """Type of action.
        0: deletion,
        1: insertion,
        -1: focus in, focus out, or a change to the textvariable."""
        return int(self.__kw['d'])

    @property
    def index(self):
        """Index of the beginning of the insertion or deletion.
        -1: focus in, focus out, or a change to the textvariable."""
        return int(self.__kw['i'])

    @property
    def text_if_allowed(self):
        """The text in the entry will have if the change is allowed.
        """
        return self.__kw['P']

    @property
    def text_before_change(self):
        """The text in the entry before the change.
        """
        return self.__kw['s']

    @property
    def text_what_changed(self):
        """The text in the entry being inserted or deleted.
        """
        return self.__kw['S']

    @property
    def type_of_validation(self):
        """The value of the entry's validate option.
        """
        return self.__kw['v']

    @property
    def reason_for_callback(self):
        """The reason for this callback.
        Returns 'focusin', 'focusout', 'key', or 'forced'."""
        return self.__kw['V']

    @property
    def widget(self):
        """The entry widget.
        """
        return self.__widget

    def __repr__(self):
        members = [m for m in dir(self) if m[0] != '_']
        items = []
        for m in members:
            val = getattr(self, m)
            if isinstance(val, Number):
                items.append('%s=%s' % (m, val))
            elif isinstance(val, str):
                items.append('%s=\'%s\'' % (m, val))
            else:
                items.append('%s=%s' % (m, val.__repr__()))
        return '<validation %s>' % " ".join(items)


class BaseEntryWithValidator(tk.Entry):
    """Internal class for tkinter Entry with valiator."""
    def __init__(self, master, **kw):
        """Construct an entry widget with validator."""
        tk.Entry.__init__(self, master)
        vcmd = (
            self.register(self.__vcmd_callback),
            '%d', '%i', '%P', '%s', '%S', '%v', '%V'
        )
        #
        # '%d'	Type of action.:
        #       0: deletion,
        #       1: insertion,
        #       -1: focus in, focus out, or a change to the textvariable.
        #
        # '%i'	Index of the beginning of the insertion or deletion.
        #       -1: focus in, focus out, or a change to the textvariable.
        #
        # '%P'	The text in the entry will have if the change is allowed.
        #
        # '%s'	The text in the entry before the change.
        #
        # '%S'	The text in the entry being inserted or deleted.
        #
        # '%v'	The current value of the widget's validate option.
        #
        # '%V'	The reason for this callback.
        #       'focusin', 'focusout', 'key', or 'forced'.
        #       'forced' means the textvariable was changed.
        #
        # '%W'	The name of the widget.
        #
        tk.Entry.configure(self, validate='all', vcmd=vcmd)
        tk.Entry.configure(self, **kw)

    def __vcmd_callback(self, d, i, P, s, S, v, V):
        """Internal function.
        Callback function of native Entry's 'validatecommand' option."""
        validation = Validation(self, d=d, i=i, P=P, s=s, S=S, v=v, V=V)
        return self.validate(validation)

    def validate(self, validation):
        """Validating the changing text in the entry.
        """
        return True


def japanese_width_count(chr):
    """
    Returns int value.
    1 for chr is halfwidth(hankaku).
    2 for chr is fullwidth(zenkaku)
    """
    if east_asian_width(chr) in 'FWA':
        return 2
    else:
        return 1


def sum_of_japanese_width_count(chrs):
    """Returns sum of Japanese width count of chrs.
    """
    res = 0
    for c in chrs:
        res += japanese_width_count(c)
    return res


class Entry_LimitedJapaneseDataLength(BaseEntryWithValidator):
    """tkinter Entry widget for Japanese."""
    def __init__(self, master, length=None, **kw):
        # not implemented:
        #   length option.
        self.__len = length
        BaseEntryWithValidator.__init__(self, master, **kw)

    def validate(self, validation):
        if self.__len is None:
            return True
        after = validation.text_if_allowed
        # not implemented:
        #   if the action was paste.
        #   invalid event handling.
        if sum_of_japanese_width_count(after) > self.__len:
            return False
        else:
            return True


Entry_LtdJpnDataLen = Entry_LimitedJapaneseDataLength


if __name__ == "__main__":
    root = tk.Tk()
    ent = Entry_LtdJpnDataLen(root, length=10)
    ent.pack()

    root.mainloop()
