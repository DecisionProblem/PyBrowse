import sys
from PySide6.QtCore import QUrl, QSize
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QToolBar,
    QLineEdit, QPushButton, QWidget, QVBoxLayout
)
from PySide6.QtWebEngineWidgets import QWebEngineView

# --- Configuration ---
DEFAULT_URL = "https://www.google.com"
HOME_URL = "https://www.google.com"
# ---------------------

class BrowserTab(QWebEngineView):
    """
    A custom QWebEngineView to represent a single browser tab.
    Handles navigation logic for the address bar and window title updates.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent

    def createWindow(self, type):
        """Handle new windows (e.g., links with target="_blank") by opening a new tab."""
        if type == QWebEngineView.WebBrowserWindow:
            new_tab = BrowserTab(self.parent_window)
            self.parent_window.add_new_tab(new_tab, QUrl(DEFAULT_URL))
            return new_tab
        return super().createWindow(type)

class MainWindow(QMainWindow):
    """
    The main browser window, handling the toolbar and tab management.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Python Browser")
        self.setMinimumSize(QSize(1000, 600))

        # 1. Tab Widget Setup
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.update_ui_on_tab_change)
        self.setCentralWidget(self.tabs)

        # 2. Navigation Toolbar Setup
        nav_toolbar = QToolBar("Navigation")
        nav_toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(nav_toolbar)

        # --- Navigation Buttons ---
        back_btn = QPushButton("⬅️")
        back_btn.setStatusTip("Back to previous page")
        back_btn.clicked.connect(lambda: self.tabs.currentWidget().back())
        nav_toolbar.addWidget(back_btn)

        forward_btn = QPushButton("➡️")
        forward_btn.setStatusTip("Forward to next page")
        forward_btn.clicked.connect(lambda: self.tabs.currentWidget().forward())
        nav_toolbar.addWidget(forward_btn)

        reload_btn = QPushButton("🔄")
        reload_btn.setStatusTip("Reload page")
        reload_btn.clicked.connect(lambda: self.tabs.currentWidget().reload())
        nav_toolbar.addWidget(reload_btn)

        home_btn = QPushButton("🏠")
        home_btn.setStatusTip("Go to Home (Google)")
        home_btn.clicked.connect(self.navigate_home)
        nav_toolbar.addWidget(home_btn)

        # --- Address Bar ---
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        nav_toolbar.addWidget(self.url_bar)

        # --- New Tab Button ---
        new_tab_btn = QPushButton("➕ New Tab")
        new_tab_btn.setStatusTip("Open a new tab")
        new_tab_btn.clicked.connect(lambda: self.add_new_tab(BrowserTab(self)))
        nav_toolbar.addWidget(new_tab_btn)

        # 3. Add Initial Tab
        self.add_new_tab(BrowserTab(self), QUrl(DEFAULT_URL))

    def add_new_tab(self, browser: BrowserTab, url: QUrl = None, label: str = "New Tab"):
        """Adds a new tab to the QTabWidget."""
        if url is None:
            url = QUrl(DEFAULT_URL)

        browser.setUrl(url)
        
        # Connect signals for status and title updates
        browser.urlChanged.connect(lambda q, browser=browser: self.update_url_bar(q, browser))
        browser.titleChanged.connect(lambda title, browser=browser: self.update_tab_title(title, browser))

        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)

    def close_tab(self, index):
        """Closes the tab at the given index."""
        if self.tabs.count() < 2:
            # Prevent closing the last tab
            return

        widget = self.tabs.widget(index)
        widget.deleteLater()
        self.tabs.removeTab(index)

    def update_tab_title(self, title: str, browser: BrowserTab):
        """Updates the tab title when the page title changes."""
        index = self.tabs.indexOf(browser)
        if index != -1:
            self.tabs.setTabText(index, title)
            # Also update the main window title for the current tab
            if browser == self.tabs.currentWidget():
                self.setWindowTitle(f"Python Browser - {title}")

    def navigate_to_url(self):
        """Loads the URL typed in the address bar."""
        q = QUrl(self.url_bar.text())
        if q.scheme() == "":
            # Default to HTTPS, or use Google search if not a valid URL
            url_text = self.url_bar.text()
            if "." in url_text:
                q.setUrl("https://" + url_text)
            else:
                q.setUrl(f"https://www.google.com/search?q={url_text}")

        self.tabs.currentWidget().setUrl(q)

    def update_url_bar(self, q: QUrl, browser: BrowserTab = None):
        """Updates the address bar to show the current page's URL."""
        if browser != self.tabs.currentWidget():
            return
        
        self.url_bar.setText(q.toString())
        self.url_bar.setCursorPosition(0)

    def navigate_home(self):
        """Loads the home page (Google) in the current tab."""
        self.tabs.currentWidget().setUrl(QUrl(HOME_URL))

    def update_ui_on_tab_change(self, index):
        """Updates the address bar and window title when a different tab is selected."""
        if index != -1:
            current_browser = self.tabs.widget(index)
            self.update_url_bar(current_browser.url(), current_browser)
            self.update_tab_title(current_browser.title(), current_browser)


if __name__ == '__main__':
    # Ensure QtWebEngine is loaded before creating the app
    try:
        from PySide6.QtWebEngineWidgets import QWebEngineView
    except ImportError:
        print("FATAL ERROR: QWebEngineWidgets module not found.")
        print("Please ensure you have PySide6 installed correctly, often:")
        print("pip install PySide6")
        sys.exit(1)

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
