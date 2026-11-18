"""
HTML rendering.

Catalogue content comes from einthusan. Personal data remains in localStorage
for offline browsing and is merged into the account database when signed in.

Markup follows the class names in style.css. Rails are filled from app.js;
everything server-rendered is static HTML so the page paints without JS.
"""

import html
import re
import urllib.parse

from flask import request

from . import einthusan as E

NAV = [
    ("/", "Home", "home"),
    ("/search", "Search", "search"),
    ("/watchlist", "My List", "list"),
]

LANG_OPTIONS = list(E.LANGS)


def esc(text):
    return html.escape(text or "", quote=True)


def origin():
    """Absolute base for the share card. Taken from the request so the tag is
    right on localhost, on Render and on Vercel without being hard-coded."""
    try:
        return request.host_url.rstrip("/")
    except RuntimeError:
        return ""


# --------------------------------------------------------------------------
# icons
# --------------------------------------------------------------------------

ICON_SEARCH = ('<svg viewBox="0 0 24 24" width="18" height="18" fill="none"'
               ' stroke="currentColor" stroke-width="2" stroke-linecap="round"'
               ' aria-hidden="true"><circle cx="11" cy="11" r="7"/>'
               '<path d="m20 20-3.5-3.5"/></svg>')

ICON_PLAY = ('<svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"'
             ' aria-hidden="true"><path d="M8 5v14l11-7z"/></svg>')

ICON_PLUS = ('<svg viewBox="0 0 24 24" width="18" height="18" fill="none"'
             ' stroke="currentColor" stroke-width="2.2" stroke-linecap="round"'
             ' aria-hidden="true"><path d="M12 5v14M5 12h14"/></svg>')

ICON_CHECK = ('<svg viewBox="0 0 24 24" width="18" height="18" fill="none"'
              ' stroke="currentColor" stroke-width="2.4" stroke-linecap="round"'
              ' stroke-linejoin="round" aria-hidden="true">'
              '<path d="m5 13 4 4L19 7"/></svg>')

ICON_PREV = ('<svg viewBox="0 0 24 24" width="22" height="22" fill="none"'
             ' stroke="currentColor" stroke-width="2.4" stroke-linecap="round"'
             ' stroke-linejoin="round" aria-hidden="true">'
             '<path d="m15 6-6 6 6 6"/></svg>')

ICON_NEXT = ('<svg viewBox="0 0 24 24" width="22" height="22" fill="none"'
             ' stroke="currentColor" stroke-width="2.4" stroke-linecap="round"'
             ' stroke-linejoin="round" aria-hidden="true">'
             '<path d="m9 6 6 6-6 6"/></svg>')

ICON_GEAR = ('<svg viewBox="0 0 24 24" width="19" height="19" fill="none"'
             ' stroke="currentColor" stroke-width="1.8" stroke-linecap="round"'
             ' stroke-linejoin="round" aria-hidden="true">'
             '<path d="M9.6 3.2h4.8l.7 2.1a7.3 7.3 0 0 1 1.7 1l2.1-.6 2.4 4.1-1.5 1.6'
             'a7.4 7.4 0 0 1 0 2l1.5 1.6-2.4 4.1-2.1-.6a7.3 7.3 0 0 1-1.7 1l-.7 2.1H9.6l-.7-2.1'
             'a7.3 7.3 0 0 1-1.7-1l-2.1.6-2.4-4.1 1.5-1.6a7.4 7.4 0 0 1 0-2L2.7 9.8l2.4-4.1 2.1.6'
             'a7.3 7.3 0 0 1 1.7-1z"/><circle cx="12" cy="12.4" r="2.7"/></svg>')

ICON_HOME = ('<svg viewBox="0 0 24 24" width="17" height="17" fill="none"'
             ' stroke="currentColor" stroke-width="2" stroke-linejoin="round"'
             ' aria-hidden="true"><path d="m3 11 9-8 9 8v9a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1z"/>'
             '<path d="M9 21v-6h6v6"/></svg>')
ICON_LIST = ('<svg viewBox="0 0 24 24" width="17" height="17" fill="none"'
             ' stroke="currentColor" stroke-width="2" stroke-linecap="round"'
             ' aria-hidden="true"><path d="M5 5h14M5 12h14M5 19h14"/></svg>')

ICON_LIB = ('<svg viewBox="0 0 24 24" width="17" height="17" fill="none"'
            ' stroke="currentColor" stroke-width="2" stroke-linecap="round"'
            ' stroke-linejoin="round" aria-hidden="true">'
            '<rect x="3" y="4" width="7" height="7" rx="1.5"/>'
            '<rect x="14" y="4" width="7" height="7" rx="1.5"/>'
            '<rect x="3" y="15" width="7" height="7" rx="1.5"/>'
            '<rect x="14" y="15" width="7" height="7" rx="1.5"/></svg>')

NAV_ICONS = {"home": ICON_HOME, "search": ICON_SEARCH, "list": ICON_LIST,
             "lib": ICON_LIB}


# --------------------------------------------------------------------------
# shell
# --------------------------------------------------------------------------


def lang_options(selected):
    return "".join(
        '<option value="%s"%s>%s</option>'
        % (code, " selected" if code == selected else "", esc(label))
        for code, label in LANG_OPTIONS)


def page(title, body, top_lang="tamil"):
    current = title.lower()
    links = "".join(
        '<a class="nav-link%s" href="%s">%s<span>%s</span></a>'
        % (" on" if (href == "/" and current == "home")
           or href.lstrip("/").lower() == current else "",
           href, NAV_ICONS[key], esc(label))
        for href, label, key in NAV)

    # The home page carries the site name; every other page leads with its own
    # name so a tab in a crowded strip still says which page it is.
    shown = ("EinthuFlix &middot; South Asian films and shows"
             if current == "home" else "%s &middot; EinthuFlix" % esc(title))

    return (
        '<!DOCTYPE html>'
        '<html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<meta name="color-scheme" content="dark">'
        '<meta name="theme-color" content="#0a0809">'
        '<script>try{document.documentElement.setAttribute("data-theme",'
        'localStorage.getItem("iml:theme")||"saffron")}catch(e){}</script>'
        '<link rel="preconnect" href="https://fonts.googleapis.com">'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
        'family=Fraunces:ital,opsz,wght@0,9..144,300..700;1,9..144,400..600'
        '&amp;family=IBM+Plex+Mono:wght@400;500'
        '&amp;family=Instrument+Sans:wght@400;500;600&amp;display=swap">'
        '<link rel="icon" href="/static/favicon-32.png" sizes="32x32"'
        ' type="image/png">'
        '<link rel="icon" href="/static/icon-192.png" sizes="192x192"'
        ' type="image/png">'
        '<link rel="apple-touch-icon" href="/static/logo-180.png">'
        '<link rel="manifest" href="/static/manifest.json">'
        '<meta name="application-name" content="EinthuFlix">'
        '<meta property="og:site_name" content="EinthuFlix">'
        '<meta property="og:title" content="%s">'
        '<meta property="og:image" content="%s/static/og.png">'
        '<meta name="twitter:card" content="summary_large_image">'
        '<meta name="description" content="Tamil, Telugu, Malayalam, '
        'Kannada, Hindi and English films and shows.">'
        "<title>%s</title>"
        '<link rel="stylesheet" href="/static/style.css">'
        "</head><body>"
        '<header class="nav" id="bar"><div class="nav-inner">'
        '<a class="brand" href="/" aria-label="EinthuFlix home">'
        '<img class="brand-mark" src="/static/mark.png" alt="" width="32"'
        ' height="28"><span class="brand-word">Einthu<em>Flix</em></span>'
        '<span class="brand-tag">South Asian cinema</span></a>'
        '<nav class="nav-links">%s</nav>'
        '<form class="nav-search" action="/search" method="get" role="search">'
        '<span class="nav-field">%s'
        '<input type="search" name="q" placeholder="Search films"'
        ' autocomplete="off" aria-label="Search films"></span>'
        '<select name="lang" aria-label="Language">%s</select>'
        "</form>"
        '<a class="nav-gear" href="/settings" aria-label="Settings">%s</a>'
        "</div></header>"
        '<main class="page" data-lang="%s">%s</main>'
        '<footer class="foot"><div class="foot-inner">'
        '<a class="foot-link" href="https://github.com/RegorTheDodger/einthuflix"'
        ' target="_blank" rel="noopener noreferrer"'
        ' aria-label="Source on GitHub">'
        '<svg class="foot-icon" viewBox="0 0 16 16" width="16" height="16"'
        ' aria-hidden="true"><path fill="currentColor" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8c0-4.42-3.58-8-8-8z"/></svg>'
        '<span>Source on GitHub</span></a>'
        "</div></footer>"
        '<script src="/static/motion.js"></script>'
        '<script src="/static/app.js?v=2"></script>'
        "</body></html>"
        % (shown, origin(), shown, links, ICON_SEARCH,
           lang_options(top_lang), ICON_GEAR, esc(top_lang), body)
    )


# --------------------------------------------------------------------------
# pieces
# --------------------------------------------------------------------------


def search_field(value="", lang="tamil", action="/search"):
    return (
        '<form class="search-field" action="%s" method="get" role="search">'
        '<span class="sf-input">%s'
        '<input type="search" name="q" value="%s" placeholder="Search films"'
        ' autocomplete="off" aria-label="Film title" required></span>'
        '<select name="lang" aria-label="Language">%s</select>'
        '<button class="btn" type="submit">Search</button>'
        "</form>" % (esc(action), ICON_SEARCH, esc(value), lang_options(lang)))


def watch_href(item):
    """The bare id cannot render a player, so the card passes on what it
    already knows rather than paying for a lookup."""
    return "/watch/%s?%s" % (esc(item["id"]), urllib.parse.urlencode({
        "t": item["title"], "c": item.get("cover") or "",
        "y": item.get("year") or "", "l": item.get("lang") or "",
    }))


def card(item):
    """A card for anything already known to be playable. `href` lets a
    library title point at its own page instead of straight at a player."""
    href = item.get("href") or watch_href(item)
    poster = ('<img loading="lazy" src="%s" alt="">' % esc(item["cover"])
              if item.get("cover") else '<span class="card-none">No artwork</span>')
    meta = " &middot; ".join(esc(b) for b in (item.get("year"), item.get("lang")) if b)

    return (
        '<article class="card" data-id="%s" data-title="%s" data-cover="%s"'
        ' data-url="%s" data-href="%s" data-year="%s" data-lang="%s">'
        '<a class="card-link" href="%s" aria-label="%s">'
        '<span class="card-poster">%s'
        '<span class="card-shade"></span>'
        '<span class="card-play">%s</span>'
        "</span>"
        '<span class="card-text"><b>%s</b>%s</span>'
        "</a>"
        '<button class="card-add" type="button" data-action="toggle"'
        ' aria-label="Add to my list"><span class="add-off">%s</span>'
        '<span class="add-on">%s</span></button>'
        "</article>"
        % (esc(item["id"]), esc(item["title"]), esc(item.get("cover") or ""),
           esc(item["url"]), esc(href), esc(item.get("year", "")),
           esc(item.get("lang", "")), href, esc(item["title"]),
           poster, ICON_PLAY, esc(item["title"]),
           ('<em>%s</em>' % meta) if meta else "",
           ICON_PLUS, ICON_CHECK))


def continue_head_actions():
    """Emptying the shelf at once, behind its own yes/no question."""
    return (
        '<button class="shelf-clear" type="button" data-action="clear-continue"'
        ' hidden>Clear all</button>'
        '<span class="shelf-confirm" data-confirm="continue" hidden>'
        "<span>Are you sure?</span>"
        '<button class="btn tiny" type="button"'
        ' data-action="confirm-clear-continue">Yes</button>'
        '<button class="btn ghost tiny" type="button"'
        ' data-action="cancel-clear-continue">No</button></span>'
    )


def shelf(title, shelf_id, items_html="", empty_text="", note="",
          head_extra=""):
    head = '<h2>%s</h2>' % esc(title)
    if note:
        head += '<p class="shelf-note">%s</p>' % esc(note)
    head += head_extra
    return (
        '<section class="shelf" data-row="%s">'
        '<div class="shelf-head">%s</div>'
        '<div class="rail-wrap">'
        '<div class="rail" data-shelf="%s" tabindex="0" aria-label="%s">%s</div>'
        '<button class="rail-btn prev" data-scroll="-1" tabindex="-1"'
        ' aria-label="Scroll left">%s</button>'
        '<button class="rail-btn next" data-scroll="1" tabindex="-1"'
        ' aria-label="Scroll right">%s</button>'
        "</div>"
        '<p class="empty" data-empty="%s"%s>%s</p>'
        "</section>"
        % (esc(shelf_id), head, esc(shelf_id), esc(title), items_html,
           ICON_PREV, ICON_NEXT, esc(shelf_id),
           "" if empty_text else " hidden", esc(empty_text))
    )


def grid(items_html, empty_text=""):
    return (
        '<div class="grid">%s</div>'
        '<p class="empty"%s>%s</p>'
        % (items_html, "" if empty_text else " hidden", esc(empty_text))
    )


# --------------------------------------------------------------------------
# pages
# --------------------------------------------------------------------------


def billboard_fallback(top_lang="tamil"):
    """Shown when the catalogue has nothing to feature either. app.js swaps the
    hero for the newest saved film as soon as it can read localStorage, so this
    has to look complete on its own for the first paint."""
    return (
        '<section class="bb bb-plain"><div class="bb-inner">'
        '<p class="bb-kicker">EinthuFlix</p>'
        '<h1 class="bb-title">Your next film<br>is one search away.</h1>'
                '<p class="bb-sub">Save anything with the + on a poster and the newest '
        'one shows up here.</p>'
        '<div class="bb-search">%s</div></div></section>'
        % search_field(lang=top_lang)
    )


def billboard_item(item, kicker="Now showing"):
    """The hero, painted from the catalogue rather than from a saved list.

    Mirrors the markup app.js writes into the same host, so the swap from this
    to a personalised film does not shift anything on the page.
    """
    cover = item.get("cover") or ""
    href = watch_href(item)
    chips = "".join('<span class="bb-chip">%s</span>' % esc(bit)
                    for bit in (item.get("year"), item.get("lang")) if bit)

    parts = ['<section class="bb">']
    if cover:
        parts.append('<div class="bb-art" aria-hidden="true">'
                     '<img src="%s" alt=""></div>' % esc(cover))
    parts.append('<div class="bb-scrim" aria-hidden="true"></div>')
    parts.append('<div class="bb-inner">'
                 '<p class="bb-kicker">%s</p>'
                 '<h1 class="bb-title">%s</h1>'
                 % (esc(kicker), esc(item["title"])))
    if chips:
        parts.append('<p class="bb-meta">%s</p>' % chips)
    parts.append('<div class="bb-actions">'
                 '<a class="btn play" href="%s">%sPlay</a>'
                 '<a class="btn ghost" href="%s">More info</a>'
                 "</div></div>" % (esc(href), ICON_PLAY, esc(href)))
    if cover:
        parts.append('<div class="bb-poster" aria-hidden="true">'
                     '<img src="%s" alt=""></div>' % esc(cover))
    parts.append("</section>")
    return "".join(parts)


def home_page(top_lang):
    # A visitor with an empty list still deserves a film, so the hero and the
    # discovery rails come from the catalogue. app.js takes the hero over with
    # the newest saved title the moment there is one.
    try:
        browse = E.browse(top_lang if top_lang in E.LANG_CODES else None)
    except Exception:
        browse = {"featured": [], "shelves": []}

    featured = browse.get("featured") or []
    hero = billboard_item(featured[0]) if featured else billboard_fallback(top_lang)

    rails = []
    for shelf_data in (browse.get("shelves") or [])[:3]:
        items = shelf_data.get("items") or []
        if not items:
            continue
        rails.append(shelf(
            shelf_data.get("title") or "Films",
            "browse-%d" % len(rails),
            items_html="".join(card(one) for one in items[:12])))

    # Saved and half-watched first: the discovery rows are what is on offer,
    # these two are what somebody already chose.
    return ("Home",
            '<div class="bb-host" data-billboard>%s</div>'
            '<div class="rows" data-rows>%s%s%s</div>'
            % (hero,
               shelf("Continue watching", "continue",
                     empty_text="Nothing part-watched yet. Start a film and "
                                "it shows up here.",
                     head_extra=continue_head_actions()),
               shelf("My list", "watchlist",
                     empty_text="Nothing saved yet. Use the + on any poster."),
               "".join(rails),
               ),
            top_lang)


def lang_tabs(query, lang):
    """Picking a language keeps the query, so switching is one click instead
    of retyping."""
    links = []
    for code, label in LANG_OPTIONS:
        qs = urllib.parse.urlencode({"q": query, "lang": code})
        links.append(
            '<a class="lang-tab%s" href="/search?%s">%s</a>'
            % (" on" if code == lang else "", qs, esc(label)))
    return '<div class="lang-tabs">%s</div>' % "".join(links)


def search_hero(title_html, sub, query, lang, extra=""):
    return (
        '<section class="search-hero">%s%s'
        '<form class="search-field sf-center" action="/search" method="get"'
        ' role="search">'
        '<span class="sf-input">%s'
        '<input type="search" name="q" value="%s" placeholder="Search films"'
        ' autocomplete="off" aria-label="Film title">'
        '<button class="sf-clear" type="button" data-action="clear-search"'
        ' aria-label="Clear">&times;</button></span>'
        '<select name="lang" aria-label="Language">%s</select>'
        '<button class="btn" type="submit">Search</button>'
        "</form>%s%s</section>"
        % (title_html, ('<p class="lede">%s</p>' % esc(sub)) if sub else "",
           ICON_SEARCH, esc(query), lang_options(lang), extra,
           lang_tabs(query, lang)))


def search_page(query, lang, items, total_pages, total_count, used_prefix,
                top_lang, suggestions=()):
    if not query:
        return ("Search",
                search_hero(
                    '<p class="eyebrow">Search</p>'
                    '<h1 class="display">Find something to watch</h1>',
                    "Every language at once, or pick one. Titles are indexed "
                    "from their first letter, so start with the first word.",
                    "", lang),
                top_lang)

    label = E.LANG_NAMES.get(lang, lang)

    if not items:
        return ("Search",
                search_hero(
                    '<p class="eyebrow">No match in %s</p>'
                    '<h1 class="display">Nothing for &ldquo;%s&rdquo;</h1>'
                    % (esc(label), esc(query)),
                    "Check the spelling, try just the first word, or switch "
                    "language. Another catalogue may have it.",
                    query, lang),
                top_lang)

    note = ""
    if used_prefix and used_prefix.strip().lower() != query.strip().lower():
        note = ('Nothing matched "%s" exactly, so these start with "%s".'
                % (query, used_prefix))
    elif total_count and total_count > len(items):
        note = ("Showing %d of %d matches." % (len(items), total_count))

    count = "%d result%s" % (len(items), "" if len(items) == 1 else "s")

    return ("Search",
            search_hero(
                '<p class="eyebrow">%s &middot; %s</p>'
                '<h1 class="display search-query">%s</h1>'
                % (esc(label), esc(count), esc(query)),
                note, query, lang)
            + '<section class="results"><div class="grid">%s</div></section>'
            % "".join(card(i) for i in items),
            top_lang)


def watchlist_page(top_lang):
    return ("My List",
            '<section class="page-head">'
            '<p class="eyebrow">Saved</p>'
            '<h1 class="h1">My list</h1>'
            '<p class="lede">Kept in this browser. Clearing site data or '
            "switching device will empty it.</p>"
            '<p class="head-actions">'
            '<button class="btn ghost" type="button" data-action="clear-watchlist">'
            "Clear list</button></p></section>"
            '<div class="grid" data-shelf="watchlist-full"></div>'
            '<p class="empty" data-empty="watchlist-full">Nothing saved yet.</p>',
            top_lang)


def home_rows(top_lang):
    """Every row the home page can show, in its shipped order."""
    rows = [("continue", "Continue watching"), ("watchlist", "My list")]
    try:
        browse = E.browse(top_lang if top_lang in E.LANG_CODES else None)
        shelves = browse.get("shelves") or []
    except Exception:
        shelves = []
    for index in range(3):
        title = ""
        if index < len(shelves):
            title = shelves[index].get("title") or ""
        rows.append(("browse-%d" % index, title or "Films"))
    return rows


def rows_panel(top_lang):
    """Pick the rows and their order; the home page applies it on load."""
    items = "".join(
        '<li class="row-item" data-row-id="%s" data-row-title="%s">'
        '<label class="row-toggle"><input type="checkbox" checked>'
        '<span>%s</span></label>'
        '<span class="row-move">'
        '<button class="btn ghost tiny" type="button" data-move="-1"'
        ' aria-label="Move %s up">&uarr;</button>'
        '<button class="btn ghost tiny" type="button" data-move="1"'
        ' aria-label="Move %s down">&darr;</button></span></li>'
        % (esc(key), esc(name), esc(name), esc(name), esc(name))
        for key, name in home_rows(top_lang))
    return (
        '<section class="panel rows-panel" data-rows-panel>'
        '<h2>Home page rows</h2>'
        '<p class="panel-note">Choose which rows the home page shows and in '
        'which order. Kept in this browser, next to your list.</p>'
        '<ol class="row-list" data-row-list>%s</ol>'
        '<button class="btn ghost tiny" type="button" data-rows-reset>'
        'Reset to default</button></section>' % items)


THEMES = [
    ("saffron", "Saffron", "#f2a33c"),
    ("ember", "Ember", "#e56b3a"),
    ("crimson", "Crimson", "#e0433f"),
    ("rose", "Rose", "#e86a92"),
    ("orchid", "Orchid", "#d267d8"),
    ("violet", "Violet", "#a78bfa"),
    ("indigo", "Indigo", "#7f8cf6"),
    ("azure", "Azure", "#4aa8f0"),
    ("teal", "Teal", "#3fbcae"),
    ("emerald", "Emerald", "#54c288"),
    ("lime", "Lime", "#a3c94f"),
    ("gold", "Gold", "#d9b544"),
    ("sand", "Sand", "#d3bb9c"),
    ("ice", "Ice", "#a8bed6"),
    ("slate", "Slate", "#96a4b4"),
]


def theme_panel():
    """Fifteen accents; the choice is applied in the browser and kept there."""
    swatches = "".join(
        '<button class="swatch" type="button" data-theme-option="%s"'
        ' style="--swatch:%s" aria-label="%s" title="%s"'
        ' aria-pressed="false"><span></span></button>'
        % (key, hexv, name, name)
        for key, name, hexv in THEMES)
    return (
        '<section class="panel theme-panel" data-theme-panel>'
        '<h2>Colour</h2>'
        '<p class="panel-note">The accent the whole site uses. Kept in this '
        'browser.</p>'
        '<div class="swatches" data-theme-list>%s</div></section>' % swatches)


def settings_page(top_lang):
    rows = "".join(
        '<label class="radio"><input type="radio" name="toplang" value="%s"%s>'
        "<span>%s</span></label>"
        % (code, " checked" if code == top_lang else "", esc(name))
        for code, name in LANG_OPTIONS)
    return ("Settings",
            '<section class="page-head">'
            '<p class="eyebrow">Preferences</p>'
            '<h1 class="h1">Settings</h1></section>'
            + theme_panel() +
            '<section class="panel"><h2>Default language</h2>'
            '<p class="panel-note">The language the search box starts on. '
            "You can still switch it per search.</p>"
            '<form class="setlang" action="/settings" method="post">%s'
            '<button class="btn" type="submit">Save</button></form></section>'
            '<section class="panel auth-panel" data-auth-panel><h2>Sync between devices</h2>'
            '<p class="panel-note">Create an account or log in to sync your '
            "list, watch time and resume positions between your devices.</p>"
            '<p class="auth-status" data-auth-status role="status"></p>'
            '<div data-auth-guest>'
            '<form class="auth-form" data-auth-form="login" action="/auth/login" method="post">'
            '<input type="text" name="username" placeholder="Username" '
            'autocomplete="username" required>'
            '<input type="password" name="password" placeholder="Password" '
            'autocomplete="current-password" required>'
            '<button class="btn" type="submit">Log in</button></form>'
            '<form class="auth-form" data-auth-form="register" action="/auth/register" method="post">'
            '<input type="text" name="username" placeholder="New username" '
            'autocomplete="username" required>'
            '<input type="password" name="password" placeholder="New password (8+ characters)" '
            'autocomplete="new-password" required>'
            '<button class="btn ghost" type="submit">Create account</button></form>'
            '</div><div data-auth-user hidden>'
            '<p class="auth-welcome">Signed in as <b data-auth-name></b></p>'
            '<button class="btn ghost" type="button" data-auth-logout>Log out</button>'
            '</div>'
            '<form action="/auth/logout" method="post" hidden>'
            '<button class="btn ghost" type="submit">Log out</button></form>'
            '<p class="panel-note">Your list stays local until you log in; '
            "the browser syncs it after authentication.</p></section>" % rows
            + rows_panel(top_lang) +
            '<section class="panel"><h2>Stored data</h2>'
            '<p class="panel-note">Erase this browser\'s local list, watch time '
            "and resume positions.</p>"
            '<button class="btn ghost" type="button" data-action="clear-all">'
            "Erase everything</button></section>",
            top_lang)


def watch_page(item, top_lang):
    meta = " &middot; ".join(esc(b) for b in (item.get("year"), item.get("lang")) if b)
    media = item.get("url") or ""

    # A signed url can come back empty: the film may be gone, or einthusan may
    # be refusing to sign. An empty player frame is worse than saying so.
    if media:
        stage = ('<div class="player-wrap"><div class="player">'
                 '<video id="player" controls preload="metadata" playsinline>'
                 '<source src="%s" type="video/mp4">'
                 "Your browser cannot play this file."
                 "</video></div></div>" % esc(media))
        open_link = ('<a class="btn ghost" href="%s" target="_blank"'
                     ' rel="noopener noreferrer">Open in new tab</a>'
                     % esc(media))
    else:
        stage = ('<div class="player-wrap"><div class="player is-empty">'
                 '<p class="play-note">einthusan is not handing out a stream for '
                 'this film just now. It may have been taken down, or the site '
                 'may be between signings — try again in a minute.</p>'
                 "</div></div>")
        open_link = ""

    return (item["title"],
            '<article class="watch" data-id="%s" data-title="%s" data-cover="%s"'
            ' data-url="%s" data-year="%s">'
            '<div class="watch-top"><a class="back" href="/">Back to home</a></div>'
            '%s'
            '<div class="watch-meta">'
            "<div><h1>%s</h1>%s</div>"
            '<div class="watch-actions">'
            '<button class="btn ghost watch-add" type="button" data-action="toggle">'
            '<span class="add-off">%s<span>My List</span></span>'
            '<span class="add-on">%s<span>In My List</span></span></button>'
            "%s"
            "</div></div>"
            '<p class="resume" data-role="resume"></p>'
            "</article>"
            % (esc(item["id"]), esc(item["title"]), esc(item.get("cover") or ""),
               esc(media), esc(item.get("year", "")), stage,
               esc(item["title"]),
               ('<p class="watch-sub">%s</p>' % meta) if meta else "",
               ICON_PLUS, ICON_CHECK, open_link),
            top_lang)


def convert_page(raw, movie_id, ok, ctype, error):
    if error:
        return ("Convert",
                '<section class="page-head"><h1 class="h1">Convert</h1>'
                '<p class="lede bad">%s</p>%s</section>'
                % (esc(error), search_field()), "tamil")

    item = {"id": movie_id, "title": "id %s" % movie_id, "year": "", "lang": "",
            "cover": None, "url": E.watch_link(movie_id)}

    if ok is None:
        badge = ""
    elif ok:
        badge = '<p class="lede good">Confirmed live (%s).</p>' % esc(ctype)
    else:
        badge = ('<p class="lede bad">No file at that address on the CDN. The id '
                 "may be wrong, or the film may be gone.</p>")

    return ("Convert",
            '<section class="page-head"><h1 class="h1">Convert a link</h1>'
            '<form class="search-field" action="/convert" method="get">'
            '<span class="sf-input"><input type="text" name="u"'
            ' placeholder="einthusan link or 4-character id" autocomplete="off"'
            ' required></span>'
            '<button class="btn" type="submit">Convert</button></form>%s</section>'
            '<div class="grid">%s</div>'
            % (badge, card(item)), "tamil")
