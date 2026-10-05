"""Find a legal place to get every song you want, cheapest first.

Reads a want list (your Spotify data export, or a plain text list), checks
what you already own, looks each song up on the iTunes Store and
optionally MusicBrainz, and writes a shopping list that says, per album,
whether buying the album or single tracks is cheaper. Songs that are not
sold digitally are checked for CD or vinyl releases. Anything left gets
search links for other stores and is marked as ear-only for now.

It never buys or downloads anything. See docs/sourcing-guide.md.

Usage:
    python3 tools/find_sources.py --spotify-export ~/Downloads/my_spotify_data \
        --library ~/Music --out ~/headphones-sources
    python3 tools/find_sources.py --list wants.txt --out ~/headphones-sources

A want list file has one song per line as "Artist - Title" or
"Artist - Title - Album". Lines starting with # are ignored.

Network: sends artist, title and album text to itunes.apple.com and, with
--musicbrainz, to musicbrainz.org, along with your IP address. Nothing
else leaves the machine. Results are cached, so a stopped run resumes.

Only the summary is printed. The full list is written to files in --out,
so the details stay on your machine unless you open them somewhere else.
Needs Python 3.10 or later and nothing else. If the optional `mutagen`
package is installed, --library reads tags. Otherwise it uses file names.
"""

from __future__ import annotations

import argparse
import csv
import difflib
import json
import pathlib
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from dataclasses import dataclass, field

USER_AGENT = "HeadphonesFindSources/0.1 ( https://github.com/banjosbanjos/Banjos-Claude-Headphones )"
ITUNES_GAP_S = 3.2  # Apple documents roughly 20 calls per minute.
MUSICBRAINZ_GAP_S = 1.1  # MusicBrainz asks for at most one call per second.
AUDIO_SUFFIXES = {".flac", ".mp3", ".m4a", ".aac", ".ogg", ".opus", ".wav", ".aif", ".aiff", ".alac"}
MIN_PLAY_MS = 30_000
MATCH = 0.86

# ---------------------------------------------------------------- matching


def norm(text: str) -> str:
    """Lowercase, strip accents, edition notes, featured artists and punctuation."""
    text = unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode()
    text = text.lower()
    text = re.sub(r"\s[-–]\s.*(remaster|version|edit|mix|mono|stereo|live|demo|single).*$", "", text)
    text = re.sub(r"[\(\[][^\)\]]*(remaster|version|edition|deluxe|bonus|mono|stereo|feat|with )[^\)\]]*[\)\]]", "", text)
    text = re.sub(r"\b(feat|ft|featuring)\b.*$", "", text)
    text = re.sub(r"^the\s+", "", text)
    text = text.replace("&", "and")
    text = re.sub(r"[^a-z0-9 ]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def similar(a: str, b: str) -> float:
    a, b = norm(a), norm(b)
    if not a or not b:
        return 0.0
    if a == b:
        return 1.0
    return difflib.SequenceMatcher(None, a, b).ratio()


def wants_variant(title: str) -> bool:
    return bool(re.search(r"\b(live|remix|mix|demo|acoustic|edit)\b", title, re.I))


# ---------------------------------------------------------------- data


@dataclass
class Want:
    artist: str
    title: str
    album: str = ""
    plays: int = 0
    status: str = "unknown"  # owned, itunes, musicbrainz_store, physical_only, not_found
    route: str = ""
    price: float | None = None
    link: str = ""
    note: str = ""

    @property
    def key(self) -> str:
        return f"{norm(self.artist)}|{norm(self.title)}"


@dataclass
class AlbumPlan:
    artist: str
    album: str
    album_price: float | None
    album_link: str
    wanted: list[Want] = field(default_factory=list)


# ---------------------------------------------------------------- inputs


def read_spotify_export(folder: pathlib.Path) -> list[Want]:
    """Plays from extended history outrank saves, so plays set the order."""
    wants: dict[str, Want] = {}

    for path in sorted(folder.rglob("Streaming_History_Audio_*.json")):
        for row in json.loads(path.read_text(encoding="utf-8")):
            title = row.get("master_metadata_track_name")
            artist = row.get("master_metadata_album_artist_name")
            if not title or not artist:
                continue  # podcasts, audiobooks, videos
            w = Want(artist, title, row.get("master_metadata_album_album_name") or "")
            w = wants.setdefault(w.key, w)
            if (row.get("ms_played") or 0) >= MIN_PLAY_MS:
                w.plays += 1

    library = next(folder.rglob("YourLibrary.json"), None)
    if library:
        for row in json.loads(library.read_text(encoding="utf-8")).get("tracks", []):
            if row.get("artist") and row.get("track"):
                w = Want(row["artist"], row["track"], row.get("album") or "")
                wants.setdefault(w.key, w)

    if not wants:
        sys.exit(f"No Streaming_History_Audio_*.json or YourLibrary.json found under {folder}")
    return sorted(wants.values(), key=lambda w: -w.plays)


def read_list(path: pathlib.Path) -> list[Want]:
    wants: dict[str, Want] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in re.split(r"\s+[-–]\s+", line)]
        if len(parts) < 2:
            print(f"skipped (need 'Artist - Title'): {line}", file=sys.stderr)
            continue
        w = Want(parts[0], parts[1], parts[2] if len(parts) > 2 else "")
        wants.setdefault(w.key, w)
    return list(wants.values())


def scan_library(root: pathlib.Path) -> list[tuple[str, str]]:
    """Return (artist, title) pairs for owned files."""
    try:
        import mutagen  # type: ignore
    except ImportError:
        mutagen = None
        print("mutagen not installed: matching owned files by file name only", file=sys.stderr)

    owned = []
    for path in root.rglob("*"):
        if path.suffix.lower() not in AUDIO_SUFFIXES or not path.is_file():
            continue
        artist = title = ""
        if mutagen:
            try:
                tags = mutagen.File(path, easy=True) or {}
                artist = (tags.get("artist") or tags.get("albumartist") or [""])[0]
                title = (tags.get("title") or [""])[0]
            except Exception:
                pass
        if not title:
            stem = re.sub(r"^\d+[\s._-]+", "", path.stem)
            bits = re.split(r"\s+-\s+", stem)
            title = bits[-1]
            artist = artist or (bits[0] if len(bits) > 1 else path.parent.parent.name)
        owned.append((artist, title))
    return owned


# ---------------------------------------------------------------- network


class Fetcher:
    def __init__(self, cache_path: pathlib.Path):
        self.cache_path = cache_path
        self.cache = json.loads(cache_path.read_text()) if cache_path.exists() else {}
        self.last = {"itunes": 0.0, "musicbrainz": 0.0}
        self.calls = 0

    def get(self, service: str, url: str):
        if url in self.cache:
            return self.cache[url]
        gap = ITUNES_GAP_S if service == "itunes" else MUSICBRAINZ_GAP_S
        for attempt in range(5):
            wait = self.last[service] + gap - time.monotonic()
            if wait > 0:
                time.sleep(wait)
            self.last[service] = time.monotonic()
            try:
                req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
                with urllib.request.urlopen(req, timeout=30) as resp:
                    data = json.load(resp)
                self.calls += 1
                self.cache[url] = data
                if self.calls % 20 == 0:
                    self.save()
                return data
            except urllib.error.HTTPError as err:
                if err.code in (403, 429, 503):
                    time.sleep(gap * 2 ** (attempt + 1))
                    continue
                if err.code == 404:
                    self.cache[url] = None
                    return None
                raise
            except (urllib.error.URLError, TimeoutError):
                time.sleep(gap * 2 ** (attempt + 1))
        print(f"giving up on {service} after retries", file=sys.stderr)
        return None

    def save(self):
        self.cache_path.write_text(json.dumps(self.cache))


def itunes_url(path: str, **params) -> str:
    return f"https://itunes.apple.com/{path}?" + urllib.parse.urlencode(params)


def find_itunes_album(f: Fetcher, artist: str, album: str, country: str):
    data = f.get("itunes", itunes_url("search", term=f"{artist} {album}", entity="album", limit=10, country=country))
    best, best_score = None, 0.0
    for r in (data or {}).get("results", []):
        score = min(similar(artist, r.get("artistName", "")), similar(album, r.get("collectionName", "")))
        if score > best_score:
            best, best_score = r, score
    return best if best_score >= MATCH else None


def itunes_album_tracks(f: Fetcher, collection_id: int, country: str) -> list[dict]:
    data = f.get("itunes", itunes_url("lookup", id=collection_id, entity="song", country=country))
    return [r for r in (data or {}).get("results", []) if r.get("wrapperType") == "track"]


def find_itunes_song(f: Fetcher, w: Want, country: str):
    data = f.get("itunes", itunes_url("search", term=f"{w.artist} {w.title}", entity="song", limit=15, country=country))
    best, best_score = None, 0.0
    for r in (data or {}).get("results", []):
        if not wants_variant(w.title) and wants_variant(r.get("trackName", "")):
            continue
        score = min(similar(w.artist, r.get("artistName", "")), similar(w.title, r.get("trackName", "")))
        if score > best_score:
            best, best_score = r, score
    return best if best_score >= MATCH else None


def musicbrainz_check(f: Fetcher, w: Want) -> tuple[list[str], list[str]]:
    """Return (store links, physical formats) for the song's releases."""
    base = "https://musicbrainz.org/ws/2/"
    q = f'recording:"{w.title}" AND artist:"{w.artist}"'
    data = f.get("musicbrainz", base + "recording?" + urllib.parse.urlencode({"query": q, "fmt": "json", "limit": 5}))
    releases = []
    for rec in (data or {}).get("recordings", []):
        if similar(w.title, rec.get("title", "")) >= MATCH:
            releases += [r["id"] for r in rec.get("releases", [])[:6]]
    links, formats = set(), set()
    for rid in releases[:6]:
        rel = f.get("musicbrainz", f"{base}release/{rid}?inc=url-rels+media&fmt=json")
        for r in (rel or {}).get("relations", []):
            if r.get("type") in ("purchase for download", "download for free"):
                links.add(r["url"]["resource"])
        for m in (rel or {}).get("media", []):
            fmt = (m.get("format") or "").lower()
            if "cd" in fmt:
                formats.add("CD")
            elif "vinyl" in fmt or '"' in fmt:
                formats.add("vinyl")
            elif "cassette" in fmt:
                formats.add("cassette")
    return sorted(links), sorted(formats)


def search_links(w: Want) -> str:
    q = urllib.parse.quote_plus(f"{w.artist} {w.title}")
    qa = urllib.parse.quote_plus(f"{w.artist} {w.album or w.title}")
    return (
        f"[Bandcamp](https://bandcamp.com/search?q={q}) · "
        f"[Amazon](https://www.amazon.com/s?k={q}&i=digital-music) · "
        f"[Qobuz](https://www.qobuz.com/us-en/search?q={q}) · "
        f"[Discogs CDs](https://www.discogs.com/search/?q={qa}&type=release&format_exact=CD)"
    )


# ---------------------------------------------------------------- planning


def plan(wants: list[Want], f: Fetcher, country: str, use_mb: bool) -> list[AlbumPlan]:
    by_album: dict[tuple[str, str], list[Want]] = defaultdict(list)
    for w in wants:
        if w.status == "unknown":
            by_album[(norm(w.artist), norm(w.album))].append(w)

    plans: dict[int, AlbumPlan] = {}  # keyed by iTunes collectionId so no album is counted twice

    def add(w: Want, hit: dict):
        cid = hit.get("collectionId")
        if cid not in plans:
            plans[cid] = AlbumPlan(w.artist, hit.get("collectionName", w.album),
                                   hit.get("collectionPrice"), hit.get("collectionViewUrl", ""))
        plans[cid].wanted.append(w)

    total = len(by_album)
    for i, group in enumerate(by_album.values(), 1):
        print(f"\r  albums checked {i}/{total}", end="", file=sys.stderr, flush=True)
        artist, album = group[0].artist, group[0].album
        album_hit = find_itunes_album(f, artist, album, country) if album else None
        tracks = itunes_album_tracks(f, album_hit["collectionId"], country) if album_hit else []
        for w in group:
            hit = next((t for t in tracks if similar(w.title, t.get("trackName", "")) >= MATCH), None)
            hit = hit or find_itunes_song(f, w, country)
            if hit:
                w.status = "itunes"
                price = hit.get("trackPrice")
                w.price = price if isinstance(price, (int, float)) and price > 0 else None
                w.link = hit.get("trackViewUrl", "")
                w.album = hit.get("collectionName", w.album)
                if w.price is None:
                    w.note = "album only"
                add(w, hit)
            elif use_mb:
                links, formats = musicbrainz_check(f, w)
                if links:
                    w.status, w.link = "musicbrainz_store", links[0]
                    w.note = "store link from MusicBrainz"
                elif formats:
                    w.status = "physical_only"
                    w.note = "Released on " + ", ".join(formats) + ". Not found for sale digitally."
                else:
                    w.status = "not_found"
            else:
                w.status = "not_found"
    print(file=sys.stderr)

    for ap in plans.values():
        prices = [w.price for w in ap.wanted]
        singles_total = sum(prices) if all(p is not None for p in prices) else None
        album_cheaper = ap.album_price is not None and ap.album_price > 0 and (
            singles_total is None or ap.album_price <= singles_total)
        for w in ap.wanted:
            w.route = "buy album" if album_cheaper else ("buy single" if w.price is not None else "check store")
            if w.route == "check store":
                w.note = "album only, but no album price listed"
    return list(plans.values())


# ---------------------------------------------------------------- output


def write_outputs(out: pathlib.Path, wants: list[Want], plans: list[AlbumPlan]) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    with (out / "sources.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["artist", "title", "album", "plays", "status", "route", "price", "link", "note"])
        for w in wants:
            writer.writerow([w.artist, w.title, w.album, w.plays, w.status, w.route, w.price or "", w.link, w.note])

    albums = [ap for ap in plans if ap.wanted and ap.wanted[0].route == "buy album"]
    singles = [w for ap in plans for w in ap.wanted if w.route == "buy single"]
    album_cost = sum(ap.album_price or 0 for ap in albums)
    single_cost = sum(w.price or 0 for w in singles)
    by = defaultdict(list)
    for w in wants:
        by[w.status].append(w)

    lines = [
        "# Where to get your songs",
        "",
        "Generated by `tools/find_sources.py`. Prices are iTunes Store prices at the time of the run and can change.",
        "",
        "| | Songs |",
        "|---|---|",
        f"| Already own | {len(by['owned'])} |",
        f"| On the iTunes Store | {len(by['itunes'])} |",
        f"| Store link found on MusicBrainz | {len(by['musicbrainz_store'])} |",
        f"| CD or vinyl only | {len(by['physical_only'])} |",
        f"| Not found yet | {len(by['not_found'])} |",
        "",
        f"Estimated iTunes cost: **${album_cost + single_cost:,.2f}** "
        f"({len(albums)} albums for ${album_cost:,.2f}, {len(singles)} singles for ${single_cost:,.2f}). "
        "Check Bandcamp and Qobuz before buying from independent labels, since the artist often gets a bigger share there.",
        "",
        "## Buy these albums",
        "",
        "Buying the album is the same price or cheaper than the wanted tracks one by one.",
        "",
    ]
    for ap in sorted(albums, key=lambda a: -len(a.wanted)):
        names = ", ".join(w.title for w in ap.wanted)
        lines.append(f"- [{ap.artist} - {ap.album}]({ap.album_link}) ${ap.album_price:.2f}: {len(ap.wanted)} wanted ({names})")
    lines += ["", "## Buy these singles", ""]
    for w in sorted(singles, key=lambda w: -w.plays):
        lines.append(f"- [{w.artist} - {w.title}]({w.link}) ${w.price:.2f}")
    check = [w for ap in plans for w in ap.wanted if w.route == "check store"]
    if check:
        lines += ["", "## On iTunes, but check the price", ""]
        for w in check:
            lines.append(f"- [{w.artist} - {w.title}]({w.link}): {w.note}")
    lines += ["", "## Store links from MusicBrainz", ""]
    for w in by["musicbrainz_store"]:
        lines.append(f"- {w.artist} - {w.title}: <{w.link}>")
    lines += ["", "## CD or vinyl only", "", "Look for used copies. Rip where your country's law allows it.", ""]
    for w in by["physical_only"]:
        lines.append(f"- {w.artist} - {w.title}: {w.note} {search_links(w)}")
    lines += [
        "",
        "## Not found yet",
        "",
        "Try these searches, and your library's Freegal service. If nothing turns up, the song stays ear-only "
        "for now: mark it with `headphones station --external` while you listen on Spotify.",
        "",
    ]
    for w in sorted(by["not_found"], key=lambda w: -w.plays):
        lines.append(f"- {w.artist} - {w.title}: {search_links(w)}")
    lines += ["", "## Already own", ""]
    for w in by["owned"]:
        lines.append(f"- {w.artist} - {w.title}")
    (out / "shopping-list.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    return {k: len(v) for k, v in by.items()} | {"estimated_cost": round(album_cost + single_cost, 2)}


# ---------------------------------------------------------------- main


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--spotify-export", type=pathlib.Path, help="folder with your Spotify data export")
    src.add_argument("--list", type=pathlib.Path, help="text file, one 'Artist - Title' per line")
    ap.add_argument("--library", type=pathlib.Path, action="append", default=[], help="folder of music you own (repeatable)")
    ap.add_argument("--out", type=pathlib.Path, required=True, help="folder for shopping-list.md, sources.csv and the cache")
    ap.add_argument("--country", default="US", help="iTunes Store country code (default US)")
    ap.add_argument("--limit", type=int, default=0, help="only check the top N songs (by plays when known)")
    ap.add_argument("--min-plays", type=int, default=0, help="skip songs with fewer plays than this")
    ap.add_argument("--musicbrainz", action="store_true", help="also check MusicBrainz for store links and CD or vinyl releases (slow)")
    args = ap.parse_args()

    wants = read_spotify_export(args.spotify_export) if args.spotify_export else read_list(args.list)
    if args.min_plays:
        wants = [w for w in wants if w.plays >= args.min_plays]
    if args.limit:
        wants = wants[: args.limit]

    owned = [pair for root in args.library for pair in scan_library(root)]
    owned_keys = {f"{norm(a)}|{norm(t)}" for a, t in owned}
    for w in wants:
        if w.key in owned_keys or any(
            similar(w.title, t) >= MATCH and similar(w.artist, a) >= MATCH for a, t in owned if norm(t)[:3] == norm(w.title)[:3]
        ):
            w.status = "owned"

    args.out.mkdir(parents=True, exist_ok=True)
    fetcher = Fetcher(args.out / "cache.json")
    print(f"Checking {sum(w.status == 'unknown' for w in wants)} songs. "
          f"About {ITUNES_GAP_S * 2:.0f} s per album on the first run, instant on reruns.", file=sys.stderr)
    try:
        plans = plan(wants, fetcher, args.country, args.musicbrainz)
    finally:
        fetcher.save()
    summary = write_outputs(args.out, wants, plans)

    print("\nSummary")
    for label, key in [("already own", "owned"), ("on iTunes", "itunes"), ("store link via MusicBrainz", "musicbrainz_store"),
                       ("CD or vinyl only", "physical_only"), ("not found yet", "not_found")]:
        print(f"  {label:28} {summary.get(key, 0)}")
    print(f"  estimated iTunes cost        ${summary['estimated_cost']:,.2f}")
    print(f"\nFull list: {args.out / 'shopping-list.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
