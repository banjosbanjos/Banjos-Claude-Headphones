# Getting every song you want into Headphones

Headphones can only measure audio files you own (ADR-0001). This guide gets you as close as the law allows to "every song I'd ever want", for as little money as possible. It also tells you plainly which songs can't be had, so nothing silently goes missing.

## The short version

1. Pull back everything you've already bought.
2. Run the sourcing helper on your Spotify data. It tells you what you own, what's for sale and the cheapest way to buy it, and what only exists on CD.
3. Grab free downloads through your library card.
4. Buy the rest, cheapest route first.
5. Hunt used CDs for anything not sold as a download.
6. Whatever is left you can still mark by ear while listening on Spotify.

## 1. Pull back what you already own

These cost nothing and often cover more than you'd expect.

- **iTunes Store purchases.** Every song bought on iTunes since 2009 is DRM-free and can be downloaded again from the Purchased section of the Apple Music app (Mac) or the Apple Music or iTunes app (Windows).
- **Amazon MP3 purchases.** Downloadable again from your Amazon Music library under Purchased.
- **Bandcamp purchases.** Your collection page lets you re-download anything you've bought, in any format, including lossless.
- **Old hard drives, backups and CDs** on a shelf somewhere.

Apple Music and Amazon Music Unlimited *subscription* downloads don't count. They're DRM-locked rentals, not files you own.

Put everything in one folder, then `headphones library add` that folder.

## 2. Run the sourcing helper

Ask Spotify for your data on your account page under Account privacy (spotify.com/account/privacy). Ask for the **Extended streaming history**, since play counts are what your profile trusts most. It can take up to 30 days to arrive. The quicker "Account data" export has your saved songs and works too.

Then, in a terminal on your own computer:

```
python3 tools/find_sources.py --spotify-export ~/Downloads/my_spotify_data \
    --library ~/Music --out ~/headphones-sources --musicbrainz
```

No Spotify export yet? Make a text file with one song per line, `Artist - Title` or `Artist - Title - Album`, and use `--list wants.txt` instead.

What it does:

- Ranks songs by how often you actually played them (plays of 30 seconds or more), so the songs that matter most come first.
- Checks your music folder and marks what you already own.
- Looks every song up on the iTunes Store, and for each album works out whether buying the whole album or just the songs you want is cheaper.
- With `--musicbrainz`, checks songs not on iTunes for other store links (often Bandcamp) and for CD or vinyl releases.
- Writes `shopping-list.md` (links and prices, grouped by what to do) and `sources.csv` to the folder you chose.

Useful options: `--limit 300` checks only your top 300 songs, `--min-plays 5` skips songs you rarely play, `--country GB` uses a different iTunes Store.

**Timing.** Apple allows about 20 lookups a minute, so the first run takes a few seconds per album. A library of a few thousand songs can take an hour or two. Stop it any time. The next run picks up where it left off, and reruns are instant.

**What it sends.** Artist, title and album text go to Apple and, with `--musicbrainz`, to MusicBrainz, along with your IP address. Nothing else leaves your computer. It only ever prints summary counts. The full list stays in the files it writes. That's on purpose: Spotify's User Guidelines restrict feeding Spotify data into an AI (SPEC OI-1), so it's best to run this yourself rather than through Claude.

It never buys or downloads anything.

## 3. Free downloads through your library

Many US public libraries offer **Freegal Music** with a library card: DRM-free MP3s you keep forever, usually around 5 songs a week (each library sets its own limit). That's up to about 260 free songs a year. Search Freegal for anything on your "Not found yet" list before paying. Ask your library whether it subscribes.

Bandcamp also has plenty of free and name-your-price releases.

## 4. Buy the rest

- **iTunes Store**: the widest catalog for major-label music, which covers most of your anchor artists. In a test run it had Spoon, XTC, The Smiths, Teenage Fanclub, Ahmad Jamal, Trashcan Sinatras and Heavenly's 2026 album. Usually $1.29 a song.
- **Bandcamp**: best for independent labels, and the artist keeps more of the money. Lossless included. Bandcamp Fridays waive the site's cut.
- **Amazon**: MP3s, sometimes cheaper than iTunes.
- **Qobuz**: lossless and hi-res downloads.

Prefer lossless or high-bitrate files (256 kbps AAC or MP3 and up) when the price is the same. Headphones records whether a file is lossy, and a few metrics (breath, pick sound, air between notes) read best without heavy compression.

Drop new purchases in your music folder and run `headphones library add` again. Rerun the helper now and then to see your list shrink.

## 5. Used CDs for what isn't sold as a download

Some music is only on CD: out-of-print records, catalogs tied up in rights disputes, anything a label never put online. In the test run, Michelle Shocked's "Anchorage" didn't turn up on the US iTunes Store, but MusicBrainz showed CD releases. The helper lists these with a Discogs link for used copies. eBay and local record shops work too.

Ripping a CD you own is legal for personal use in some countries and a grey area in others (in the US it isn't spelled out in law, and the UK withdrew its private copying exception in 2015). Check where you live. Tag rips with the source label `cd_rip`.

Vinyl rips work too, but surface noise can confuse a few metrics (gaps, air between notes, breath). Tag them `vinyl_rip` so the analyzers and the evaluation can tell.

## 6. Songs you can't get

Some songs can't be owned legally anywhere: streaming-only releases and exclusives, live sessions recorded for a platform, out-of-print records with no copies for sale, region-locked catalogs. No legal method closes that gap, and this guide won't pretend otherwise.

Those songs can still take part. Run `headphones station --external <spotify-uri>` while you listen on Spotify, and tap your chills, head-nods and hooks. Headphones keeps those as ear judgments. It just can't measure the audio. If the song is ever sold, buy it and the measurements fill in.

## Keeping it complete

- **New songs.** When something new grabs you, add `Artist - Title` to your want list, or wait for your next Spotify data export, and rerun the helper.
- **Each December**, after Wrapped, request a fresh export and rerun. Your profile already plans a yearly refresh then.
- **Budget.** Free first (what you own, Freegal), then singles, then albums only where the helper says the album is cheaper.
