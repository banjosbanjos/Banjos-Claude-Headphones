# Getting your songs into Headphones for free

Headphones can only measure audio files you own (ADR-0001). This guide gets as many of your songs as possible into your library **without spending money**, using only legal sources. It also tells you plainly which songs a free plan can't reach, so nothing goes missing without you knowing.

## The honest picture

Free and legal covers a lot, but not everything.

- **Freegal**, through a public library card, is the main free source. It gives DRM-free MP3s you keep forever, usually about 5 songs a week. Its catalog is strongest on Sony Music's labels. It is known to lack many artists on Universal's labels, so some of your anchors won't be there.
- **Free downloads** on Bandcamp (free or name-your-price, where you can enter $0) and Creative Commons music sites cover independent and lesser-known artists.
- Everything else stays **ear-only**. You can still mark chills, head-nods and hooks for those songs while they play on Spotify. Headphones just can't measure their sound.

At 5 songs a week, Freegal adds up to about 260 songs a year per library card. Your most-played songs go first.

## Step by step

### 1. Gather what you already own

Free, because it's already yours:

- Songs you bought in the past from iTunes, Amazon or Bandcamp can be downloaded again from each store's Purchased or collection page.
- Old hard drives, backups and CDs.

Subscription downloads (Apple Music, Amazon Music Unlimited, Spotify offline) don't count. They're DRM-locked rentals.

Put everything in one folder and run `headphones library add` on it.

### 2. Get a library card with Freegal

Ask your public library whether it offers Freegal Music. Most cards allow about 5 downloads a week, and each library sets its own limit. If you can legitimately hold cards at more than one library system that offers Freegal, each card usually has its own allowance. Check each library's rules.

### 3. Make your free plan

Ask Spotify for your data on your account page under Account privacy (spotify.com/account/privacy). Ask for the **Extended streaming history**, since play counts are what your profile trusts most. It can take up to 30 days to arrive. The quicker "Account data" export has your saved songs and works too. No export yet? Make a text file with one song per line, `Artist - Title`.

Then, in a terminal on your own computer:

```
python3 tools/find_sources.py --spotify-export ~/Downloads/my_spotify_data \
    --library ~/Music --out ~/headphones-sources
```

It writes `free-plan.md` with:

- **Already own**: matched against your music folder.
- **Freegal queue**: everything else, most-played first, split into weeks at your allowance. Each song has a Bandcamp search link too, since some releases are free there.
- **Ear-only for now**: songs you've told it aren't on Freegal.

Options:

- `--freegal-per-week 3` if your library allows a different number.
- `--freegal-cards 2` if you hold two cards with Freegal.
- `--not-on-freegal missing.txt` is a file of `Artist - Title` lines you searched for and couldn't find. Those move to ear-only and the queue moves up.
- `--musicbrainz` also looks for free download links listed on MusicBrainz. Slower, about 4 seconds a song on the first run, instant on reruns.

Without `--musicbrainz` the tool makes no network calls at all. It only prints summary counts and writes the full plan to files on your computer. That's on purpose: Spotify's User Guidelines restrict feeding Spotify data into an AI (SPEC OI-1), so run it yourself rather than through Claude.

### 4. Each week

1. Open `free-plan.md` and look at this week's songs.
2. Search for each one on your library's Freegal site and download the ones it has.
3. Try the Bandcamp link for anything Freegal doesn't have. If it's free or name-your-price, enter $0.
4. Add anything you couldn't find anywhere to your `missing.txt`.
5. Put the downloads in your music folder, run `headphones library add`, and rerun the tool. Downloaded songs drop off the queue and the next week's batch moves up.

### 5. Free music for testing and first listens

Headphones' evaluation needs some tracks you've never heard and some with little written about them. Free, legal sources are ideal here, even though they're mostly not your usual artists:

- **Bandcamp** free and name-your-price releases.
- **Free Music Archive** and **Jamendo**, both Creative Commons.
- **Internet Archive** netlabel collections, also Creative Commons.

Any Creative Commons license works for personal analysis, because Headphones never shares the stems it makes. Tag these with the source label `free_download` or `cc_licensed`.

### 6. Songs a free plan can't reach

Some songs aren't free anywhere legally. Run `headphones station --external <spotify-uri>` while you listen on Spotify and tap as usual. Headphones keeps your chill, head-nod and hook marks as ear judgments. If a song later turns up free, take it off `missing.txt` and rerun.

Things that look free but aren't legal: recording from Spotify or YouTube, ripping CDs borrowed from a library or a friend, and download sites that don't have the rights. Headphones won't use those.

## Keeping it going

- **New songs**: add `Artist - Title` to your want list, or wait for your next Spotify export, and rerun.
- **Each December**, after Wrapped, request a fresh export and rerun. Your profile already plans a yearly refresh then.
- If you ever change your mind about spending money, `--mode paid` prices everything on the iTunes Store and works out whether albums or singles are cheaper.
