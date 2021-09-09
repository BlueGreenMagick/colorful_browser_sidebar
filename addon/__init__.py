from typing import Any, Callable

from aqt import gui_hooks
from aqt.qt import *
from aqt.browser import SidebarTreeView, SidebarItem
from aqt.theme import ColoredIcon

from .ankiaddonconfig import ConfigManager

conf = ConfigManager()


def conf_key(item: SidebarItem) -> str:
    return f"colors.{item.item_type.name}.{item.full_name}"


def new_sidebar_item_init(old: Callable) -> Callable:
    def func(self: SidebarItem, *args: Any, **kwargs: Any) -> None:
        old(self, *args, **kwargs)
        if not self.icon:
            return
        if color := conf.get(conf_key(self)):
            if isinstance(self.icon, ColoredIcon):
                path = self.icon.path
            else:
                path = self.icon
            self.icon = ColoredIcon(path, (color, color))

    return func


def add_color(sidebar: SidebarTreeView, item: SidebarItem) -> None:
    colorstr = conf.get(conf_key(item), "#FFFFFF")
    old_color = QColor()
    old_color.setNamedColor(colorstr)
    new_color = QColorDialog.getColor(old_color, parent=sidebar)
    if new_color.isValid():
        conf.set(conf_key(item), new_color.name(QColor.HexRgb))
        conf.save()
    sidebar.refresh()


def remove_color(sidebar: SidebarTreeView, item: SidebarItem) -> None:
    conf.pop(conf_key(item))
    conf.save()
    sidebar.refresh()


def add_sidebar_context_menu(
    sidebar: SidebarTreeView, menu: QMenu, item: SidebarItem, index: QModelIndex
) -> None:
    menu.addSeparator()
    if conf.get(conf_key(item)):
        menu.addAction("Remove Color", lambda: remove_color(sidebar, item))
    menu.addAction("Set Color", lambda: add_color(sidebar, item))


def main() -> None:
    SidebarItem.__init__ = new_sidebar_item_init(SidebarItem.__init__)  # type: ignore
    gui_hooks.browser_sidebar_will_show_context_menu.append(add_sidebar_context_menu)


main()
