[![make.fun · news-image-20261118](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![rank](https://make.fun/badge/news-image-20261118/Ikball53/news-image-20261118/rank.svg)](https://make.fun/bounty/news-image-20261118/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![reward](https://make.fun/badge/news-image-20261118/Ikball53/news-image-20261118/reward.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
# The World in One Picture — Wednesday 18 November 2026

A single front page with the day's 16 biggest stories, drawn from scratch by
a pure-Python (standard library only) generator. No Pillow, no network, no
fonts at runtime: every text line, icon and flag is a pre-rendered PNG in
`assets/`, and `main.py` composites them onto a canvas with its own tiny PNG
reader/writer and fixed-point bilinear resampling. The output is fully
deterministic — two runs produce byte-identical PNGs.

## The 16 stories

1. **ASIA — Trump in Manila for talks with Marcos Jr.** Talks and a working
   lunch with Marcos Jr., then on to Shenzhen for Thursday's APEC summit
   with Xi and Putin.
2. **ASIA — APEC leaders open summit in Shenzhen.** Xi gives the opening
   keynote as leaders of 21 economies gather in Shenzhen; Trump meets Xi
   and Putin on Thursday.
3. **MIDDLE EAST — Bahrain all-clear as Kuwait reports drones.** Bahrain
   lifts an overnight threat warning; Kuwait says its defences are
   countering hostile drones as US-Iran fire continues.
4. **ASIA — Cyclone Akvan bears down on India's east coast.** 590 km east
   of Chennai; now a severe storm, landfall between Nellore and
   Visakhapatnam due Friday, winds 120-130 km/h, gusts to 145.
5. Shetland series 12 confirmed (UK)
6. Fed minutes out after 10-2 rate hold (USA)
7. UK October inflation out today (UK)
8. Eurozone inflation holds at 4.0% (EU)
9. Pochettino starts as Man United head coach (England)
10. Emma Barnett bows out of Today (UK)
11. Latvia turns 108 on Independence Day (Latvia)
12. COP31 draft splits nations on fossil fuels (Turkey)
13. Alcaraz v Medvedev in Turin (Spain, Russia)
14. Billie Jean King Cup QFs in Seville (Spain)
15. Pope Leo meets families of the Disappeared (Ireland)
16. French Senate votes on social security bill (France)

## Run it

```sh
python3 main.py
```

`main.py` GENERATES `entry.png` — it draws the whole page and writes
`/output/entry.png` (834×985, well under the 1024×1024 and 1 MiB limits).
It does not copy a pre-rendered file.

## Sources

Every story here was reported on Wednesday 18 November 2026. Sources: BBC,
Al Jazeera, The Guardian, The New York Times, CBC, DW, France 24, SCMP.
