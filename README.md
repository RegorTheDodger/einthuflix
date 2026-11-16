<p align="center"><img src="static/logo.webp" alt="EinthuFlix — the best of South Asian cinema" width="300"></p>

# EinthuFlix

South Asian cinema, streaming in the browser: Tamil, Telugu, Malayalam, Kannada,
Hindi, Bengali, Marathi and Punjabi films in one library, with search, a player,
My List, continue watching and accounts that keep those shelves in step across
devices.

## How the site works

**The catalogue.** EinthuFlix is built on einthusan's listings, one A–Z index
per language. The home page reads the browse pages for the chosen language (or
all eight at once) and turns them into a featured film, Most Watched, Staff
Picks and Recently Added.

**Search.** einthusan has no full-text API, so a search is a prefix walk over a
language's index. If nothing matches the whole phrase, the last word is
shortened and near matches are accepted, so a typo near the end of a title still
finds the film. The language tabs keep the query when you switch, and a watch
link pasted into the box is treated as "convert this" instead of a search.

**Watching.** Each watch page resolves a signed mp4 for that page view. The
signature is issued by einthusan and expires six hours after the page was
built, so it is never stored and never reused: opening the page again signs a
fresh one. A film that has been taken down has no player element to sign, and
the page says so instead of showing an empty frame.

**My List.** The + on any poster saves the film locally, instantly, with no
account needed. Removing one writes a timestamped tombstone so a stale device
cannot bring it back.

**Continue watching.** The player writes a resume position, and the shelf shows
what is part-watched, most recent first. A title earns a card after ten seconds
of real playback; a jump longer than six seconds counts as a seek, not
watching; the position is saved at most every four seconds; and at 95% the film
counts as finished and leaves the shelf. For a show the resume point is per
episode, while My List holds the show.

**Convert.** A link from einthusan — or just its four-character id — becomes a
playable page, with an optional check that the signed file really exists at the
CDN before you press play.

## How sync works

Everything works signed out. The browser owns the list, the resume points and
the watch time, which is why the site is instant and survives a dropped
connection.

An account adds a second copy. When you sign in, the device posts its whole
state and the server returns the **merge** of the two — never a replacement.
Merging is what makes a phone and a laptop safe on one account: a film added on
one is not erased by an older copy from the other.

- **My List** — newest add per title wins; a removal is a tombstone that
  outvotes older adds and expires after 180 days.
- **Continue watching** — newest position wins; once a title is marked started
  it stays started, whichever device said so first.
- **Watch time** — the newer record supplies the metadata, but play time keeps
  the larger tally and "finished" stays true once true.
- **Titles and covers** — merged field by field, so a known title or cover is
  never replaced by a blank.
- **Finishing or clearing** a title drops the resume point rather than sending a
  device backwards.

Passwords are stored as PBKDF2-HMAC-SHA256 hashes with a per-user salt, and a
session is a random token whose hash — not the token — is kept. Attempts are
throttled per address. Total synced state is capped, so a broken client cannot
post a gigabyte of junk.

## EinthuFlix vs RogFlix

The two sites are deliberately separate products; neither links to the other,
and they share no catalogue and no account database.

| | **EinthuFlix** | **RogFlix** |
| --- | --- | --- |
| Library | South Asian cinema only — eight Indian languages | Everything the big streaming services carry, across 35 services |
| Where titles come from | einthusan's language indexes | Streaming Catalogs (Stremio) rows, metadata from Cinemeta |
| Playback | einthusan's signed mp4 in a native player | VidSpark embed by IMDb id |
| Browsing | Language tabs, Most Watched, Staff Picks, Recently Added | One row per service, plus popular films and shows on search |
| Search | Prefix search inside one language | Full-library search by title |
| Best for | Finding a Tamil, Telugu, Malayalam, Kannada, Hindi, Bengali, Marathi or Punjabi film | Finding a specific film or show from Netflix, Prime Video, JioHotstar, Disney+, HBO Max, Zee5 and the rest |

RogFlix is the broader shelf; EinthuFlix is the deeper one. Both run the same
player behaviour, the same My List and continue watching, and the same
merge-on-sync accounts described above.
