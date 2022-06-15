from PySide6.QtWidgets import (
    QStyleOptionTab,
    QStylePainter,
    QStyleFactory,
    QApplication,
    QTabWidget,
    QTabBar,
    QWidget,
    QStyle,  
)

from PySide6.QtCore import (
    QPoint,
    QSize,
    QRect
)

class VTabBar(QTabBar):
    """
    QTabBar subclass for vertical tabs.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def tabSizeHint(self, index: int) -> QSize:
        sizeHint = super().tabSizeHint(index)
        sizeHint.transpose()

        return sizeHint

    def paintEvent(self, event) -> None:
        painter = QStylePainter(self)
        optTab = QStyleOptionTab()

        for i in range(self.count()): 
            self.initStyleOption(optTab, i)
            painter.drawControl(QStyle.CE_TabBarTabShape, optTab)
            painter.save()

            s = optTab.rect.size()
            s.transpose()
            r = QRect(QPoint(), s)
            r.moveCenter(optTab.rect.center())
            optTab.rect = r

            c = self.tabRect(i).center()
            painter.translate(c)
            painter.rotate(90)
            painter.translate(-c)
            painter.drawControl(QStyle.CE_TabBarTabLabel, optTab)
            painter.restore()
