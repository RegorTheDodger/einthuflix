<p align="center"><img src="static/logo.webp" alt="EinthuFlix — the best of South Asian cinema" width="280"></p>

<h1 align="center">EinthuFlix</h1>

<p align="center">
  <a href="https://einthuflix.vercel.app"><img alt="Live site" src="https://img.shields.io/badge/live-einthuflix.vercel.app-a20e1a?style=flat-square"></a>
  <img alt="Python" src="https://img.shields.io/badge/python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white">
  <img alt="Flask" src="https://img.shields.io/badge/flask-3.1-000000?style=flat-square&logo=flask&logoColor=white">
  <img alt="PostgreSQL" src="https://img.shields.io/badge/sync-postgresql-4169E1?style=flat-square&logo=postgresql&logoColor=white">
</p>

EinthuFlix is South Asian cinema in the browser: Tamil, Telugu, Malayalam,
Kannada, Hindi, Bengali, Marathi and Punjabi films from einthusan, with search,
a native player, My List, continue watching and accounts that keep those shelves
in step across devices.

The app is Flask with server-rendered HTML, a small vanilla-JavaScript layer for
the list, the player and the shelves, and Postgres (or SQLite locally) for
accounts. No build step and no client-side framework.

> ### Start with the hosted site
>
> **<https://einthuflix.vercel.app>** is the project, ready to use — no install,
> no database, no environment variables. The install steps below are for running
> it locally when you want to change the code.

## Table of contents

- [What it does](#what-it-does)
- [How the site works](#how-the-site-works)
- [How sync works](#how-sync-works)
- [Project structure](#project-structure)
- [Every file explained](#every-file-explained)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Roadmap and known issues](#roadmap-and-known-issues)
- [Contributing](#contributing)
- [Authors](#authors)
- [License](#license)

## What it does

- **Eight languages, one library.** Tamil, Telugu, Malayalam, Kannada, Hindi,
  Bengali, Marathi and Punjabi, each with its own A–Z index.
- **Search that forgives typos.** einthusan has no search API, so the app walks
  the language's index and shortens the last word when nothing matches.
- **A native player.** No third-party frame: the film plays in the page's own
  `<video>`, with the site's resume behaviour on top.
- **My List and continue watching** that work signed out and keep working on a
  phone and a laptop once you sign in.

## How the site works

**The catalogue.** EinthuFlix is built on einthusan's listings, one A–Z index per
language. The home page reads the browse pages for the chosen language (or all
eight at once) and turns them into a carousel of ten films, one per row at a
time, followed by Most Watched, Staff Picks and Recently Added.

**Search.** einthusan has no full-text API, so a search is a prefix walk over a
language's index. If nothing matches the whole phrase, the last word is shortened
and near matches are accepted, so a typo near the end of a title still finds the
film. The language tabs keep the query when you switch, and a watch link pasted
into the box is treated as "convert this" instead of a search.

**Watching.** Each watch page resolves a signed mp4 for that page view. The
signature is issued by einthusan and expires six hours after the page was built,
so it is never stored and never reused: opening the page again signs a fresh one.
A film that has been taken down has no player element to sign, and the page says
so instead of showing an empty frame.

**Home rows.** Continue watching and My list open the home page; the discovery
rows for the chosen language follow. Settings → Home page rows chooses which rows
appear and in what order, kept in the browser beside your list. The carousel at
the top opens on your own pick — the newest film on My list, or the last one you
played — and the catalogue films follow, drawn from those rows and dropping the
ones that are switched off. With no pick and every discovery row hidden it gives
way to the search banner.

**Carousel speed.** Each film holds for ten seconds with a countdown along the
bottom edge, and a dot per film to jump straight to one. Settings → Carousel
speed changes the hold (one to six hundred seconds) and the countdown follows.

**My List.** The + on any poster saves the film locally, instantly, with no
account needed. Removing one writes a timestamped tombstone so a stale device
cannot bring it back.

**Continue watching.** The player writes a resume position, and the shelf shows
what is part-watched, most recent first. A title earns a card after ten seconds
of real playback; a jump longer than six seconds counts as a seek, not watching;
the position is saved at most every four seconds; and in the player's last
minute and a half the film counts as finished and leaves the shelf (a share of
the reported duration would misfire on streams that claim a shorter runtime).

**Convert.** A link from einthusan — or just its four-character id — becomes a
playable page, with an optional check that the signed file really exists at the
CDN before you press play.

## How sync works

Everything works signed out. The browser owns the list, the resume points and the
watch time, which is why the site is instant and survives a dropped connection.

An account adds a second copy. When you sign in, the device posts its whole state
and the server returns the **merge** of the two — never a replacement. Merging is
what makes a phone and a laptop safe on one account: a film added on one is not
erased by an older copy from the other.

- **My List** — newest add per title wins; a removal is a tombstone that outvotes
  older adds and expires after 180 days.
- **Continue watching** — newest position wins; once a title is marked started it
  stays started, whichever device said so first.
- **Watch time** — the newer record supplies the metadata, but play time keeps
  the larger tally. "Finished" belongs to the later record, so a film watched
  again (a newer resume point) stops counting as finished.
- **Titles and covers** — merged field by field, so a known title or cover is
  never replaced by a blank.
- **Finishing or clearing** a title drops the resume point rather than sending a
  device backwards.
- **Theme and home rows** — one preference stamp, newest change wins, because an
  accent is a single choice and an order is a whole arrangement rather than
  something to merge item by item.

Passwords are stored as PBKDF2-HMAC-SHA256 hashes with a per-user salt, and a
session is a random token whose hash — not the token — is kept. Attempts are
throttled per address. Total synced state is capped, so a broken client cannot
post a gigabyte of junk.

## Project structure

```text
einthuflix/
├── app.py                  local development server
├── api/
│   └── index.py            Vercel serverless entry point
├── lib/
│   ├── __init__.py         marks lib/ as a package
│   ├── webapp.py           Flask app: routes, auth, sync, convert
│   ├── views.py            all HTML rendering
│   ├── einthusan.py        einthusan client: browse, search, signed media
│   ├── accounts.py         users, sessions, signup modes
│   ├── sync.py             merge rules for the personal state
│   ├── db.py               Postgres/SQLite connection + schema
│   └── ai.py               optional Groq helper (dormant)
├── static/
│   ├── app.js              list, resume, player, rails, row settings
│   ├── motion.js           scroll reveal and small page animations
│   ├── style.css           every style in the site
│   ├── manifest.json       PWA metadata
│   ├── logo.webp           full logo (README and social previews)
│   ├── mark.png            the nav mark / emblem crop
│   ├── icon-192.png        PWA icon
│   ├── icon-512.png        PWA icon, large
│   ├── logo-180.png        apple-touch-icon
│   ├── favicon-32.png      browser tab icon
│   └── og.png             1200×630 social card
├── requirements.txt        Flask and pg8000, pinned
├── vercel.json             Vercel function settings
├── .vercelignore           files Vercel must not upload
├── .gitignore              files git must not track
└── README.md               this file
```

## Every file explained

**`app.py`** — the local dev server. Builds the Flask app, warms the einthusan
connection pool in a background thread, and runs on `127.0.0.1` at the port you
pass (`python app.py 8090`), bound to `0.0.0.0` so a phone on the same Wi-Fi can
reach it. Vercel never runs this file.

**`api/index.py`** — the Vercel entry point. It puts the project root on
`sys.path` and exposes `app = create_app()`, which is the WSGI callable Vercel
expects. Keeping it separate from `app.py` is what lets one application run in
both places.

**`lib/__init__.py`** — empty; it marks `lib` as a package so both entry points
can import from it.

**`lib/webapp.py`** — the Flask application and its routes: `/`, `/search`,
`/watch/<id>`, `/watchlist`, `/settings` (GET and POST for the default language),
the `/auth/*` endpoints, `/api/sync` (GET and POST), `/api/sync/clear`,
`/convert?u=`, the old `/library` redirects, and `/healthz`. It parses request
arguments, resolves what is being watched, calls accounts and sync, and hands a
body to `views`.

**`lib/views.py`** — every piece of HTML: the page shell (head, nav, footer), the
home page with its rows, search with language tabs, the watch page and its
player, My List, settings, and convert, plus the shared pieces (`shelf()`,
`card()`, language tabs, the hero fallback, escaping). Nothing here touches the
network; it renders what it is given.

**`lib/einthusan.py`** — all network access to einthusan, and the only file that
knows its HTML. It fetches browse pages per language, parses the A–Z indexes,
runs the prefix search (with the typo fallback), reads the watch page for the
signed mp4, parses pasted links and ids, and keeps gzipped responses in a
10-minute cache plus a two-hour media cache that refreshes before the signature
expires. Both entry points share it, and it can be tested alone.

**`lib/accounts.py`** — users and sessions: PBKDF2-HMAC-SHA256 password hashing
with a per-user salt, session tokens (only their SHA-256 is stored), the signup
modes (`first`, `open`, `closed`), throttling by address, and the state read and
write used by sync.

**`lib/sync.py`** — the merge rules. Given the state two devices posted, it
returns one: newest list add wins, tombstones beat older adds, newest resume
position wins, started stays started, watch time keeps the larger tally, metadata
is merged field by field, and the payload is capped.

**`lib/db.py`** — storage. Uses Postgres when a URL is in the environment and
SQLite at `.data/einthuflix.db` otherwise, opens connections, provides the small
query wrapper used everywhere, and creates the tables on first use. The only file
that knows a database dialect.

**`lib/ai.py`** — an optional Groq helper (spelling suggestions for an empty
search). It fails quietly and is not imported by any page today; the site is
complete without it. Set `GROQ_API_KEY` if you wire it up.

**`static/app.js`** — the browser side: localStorage for My List, resume points
and watch time, painting those shelves, the `<video>` wiring (resume, watch time,
finished), rail scrolling, search-box behaviour, the account/sync calls, and the
home-row order stored by settings.

**`static/motion.js`** — presentation only: reveal-on-scroll and the small
transitions, kept out of `app.js` so the data layer stays readable. Every page
works if it fails to load.

**`static/style.css`** — the whole design system in one file: tokens (colour,
type, spacing, radii), layout, nav, hero, shelves and cards, watch page and
player, settings panels, the home-row list, responsive rules, and reduced-motion
handling.

**`static/manifest.json`** — the web app manifest: name, colours and the 192 and
512 icons, so the site can be installed to a home screen.

**`static/logo.webp`** — the full logo with the wordmark, used by this README and
as the brand image in previews.

**`static/mark.png`** — the square emblem crop used as the 32 px nav badge; the
wordmark inside the full logo is unreadable at that size.

**`static/icon-192.png`, `static/icon-512.png`** — PWA icons referenced by the
manifest.

**`static/logo-180.png`** — the apple-touch-icon for iOS home screens.

**`static/favicon-32.png`** — the tab icon.

**`static/og.png`** — the 1200×630 social card (`og:image`), the logo on the
brand red.

**`requirements.txt`** — the two runtime dependencies, pinned: Flask 3.1.0 and
pg8000 1.31.6 (a pure-Python Postgres driver, so nothing compiles).

**`vercel.json`** — deployment settings: raises the Python function's
`maxDuration` to 30 seconds. Routing is left to Vercel, which already sends every
path to `api/index.py` and serves `static/` directly.

**`.vercelignore`** — keeps `.env`, `.venv`, `__pycache__`, `.data` and
`.DS_Store` out of a deployment.

**`.gitignore`** — keeps `.vercel`, `.data/`, caches, `.env` files and
`.DS_Store` out of the repository.

**`README.md`** — this document.

## Installation

> Reminder: for normal use, just open **<https://einthuflix.vercel.app>**.
> Install locally only to run or change the code.

**Requirements**

- Python 3.10 or newer
- pip and a terminal
- Optional: PostgreSQL 13+ for account sync across machines. Without it the app
  writes to a local SQLite file, which covers everything except signing in from
  more than one device.

**Steps**

```bash
git clone https://github.com/RegorTheDodger/einthuflix.git
cd einthuflix

python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

There is no build step: the only dependencies are Flask and the Postgres driver.

## Usage

```bash
python app.py 8090
```

```text
EinthuFlix
  http://127.0.0.1:8090
  http://<mac-ip>:8090
```

Open <http://127.0.0.1:8090>. The first visit needs no account: browse, search
and playback work signed out, and My List starts in the browser.

**Create the first account.** Go to `/settings` and register. With the default
`first` signup mode the first account is the owner and later registrations are
refused; `EINTHUFLIX_ALLOW_SIGNUP=open` opens it up (see
[Configuration](#configuration)).

**Useful routes**

```text
/search?q=vikram&lang=tamil    search one language (no lang = all)
/watch/<id>?t=120              a film, starting at 2:00
/watchlist                     My List
/convert?u=<einthusan link>    turn a link or 4-character id into a page
/settings                      account, default language, home rows, stored data
/healthz                       JSON: database dialect and app state
```

- Press the + on any poster to add it to My List.
- Watch ten seconds and the film appears under Continue watching.
- In `/settings`, **Default language** sets what search starts on, and
  **Home page rows** untick or reorders the home shelves, and **Carousel speed**
  sets how long each film in the hero holds.
- **Colour** in `/settings` picks one of fifteen palettes for the whole site —
  the accent, and the room it sits in (inks, paper, hairlines, scrims) are all
  mixed from it — kept in the browser.
- Sign in and the next visit merges this browser's list with the account's.

## Configuration

Every setting is an environment variable; all are optional for local use.

| Variable | Default | Purpose |
| --- | --- | --- |
| `EINTHUFLIX_DATABASE_URL` | local SQLite `.data/einthuflix.db` | Postgres URL for accounts and sync. `DATABASE_URL` and `POSTGRES_URL` are accepted too |
| `EINTHUFLIX_DB_PATH` | `.data/einthuflix.db` | Where the SQLite file lives when no Postgres URL is set |
| `EINTHUFLIX_ALLOW_SIGNUP` | `first` | `first` (owner only), `open` (anyone), `closed` (no registrations) |
| `GROQ_API_KEY` | unset | Optional; only used by `lib/ai.py`, which no page imports today |

Example with a local Postgres:

```bash
export EINTHUFLIX_DATABASE_URL="postgresql://user:pass@localhost:5432/einthuflix"
python app.py 8090
```

The tables are created on first use; there is no migration step.

## Roadmap and known issues

**Known issues**

- einthusan is read as HTML, so a change to its markup can break browse, search
  or the watch page until the parser in `lib/einthusan.py` is updated.
- Signed media links last six hours; the app re-signs on each page view, but a
  single viewing past expiry needs a reload.
- A film einthusan has removed has no player element to sign, and the page says
  so rather than showing an empty frame.
- Search is a prefix walk over a language's index, not full-text.
- Home row layout is per browser; it is not part of the synced account state.
- `lib/ai.py` is present but not wired into the search page.

**Roadmap**

- Wire the spelling suggestions from `lib/ai.py` into an empty search.
- Row layout synced with the account.
- Keyboard shortcuts for the player and the rails.

## Contributing

Bug reports and feature requests are welcome in
[Issues](https://github.com/RegorTheDodger/einthuflix/issues). For a pull
request, keep it small and in the shape of the existing code: HTML in
`lib/views.py`, network access in `lib/einthusan.py`, behaviour in
`static/app.js`, no new framework and no build step. Please run the app locally
and say which page you changed.

## Authors

Built and maintained by [RegorTheDodger](https://github.com/RegorTheDodger).

- Bug reports: [GitHub Issues](https://github.com/RegorTheDodger/einthuflix/issues)
- Source: [github.com/RegorTheDodger/einthuflix](https://github.com/RegorTheDodger/einthuflix)

## License

No open-source license has been applied to this repository yet: all rights are
reserved by the author, and the code may not be redistributed or reused without
permission. If you want others to be able to use it, add a `LICENSE` file (MIT
and Apache-2.0 are the usual choices) and replace this section with its name and
a link to that file.
