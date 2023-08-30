from st_pages import Page, show_pages

# Specify what pages should be shown in the sidebar, and what their titles and icons
# should be
show_pages(
    [
        Page("src/home_page.py", "Dashboard Emails", "🏠"),
        Page("src/teste.py", "teste")
    ]
)