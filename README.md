# The World in One Picture — Wednesday 18 November 2026

[![make.fun · news-image-20261118](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![rank](https://make.fun/badge/news-image-20261118/Ikball53/news-image-20261118/rank.svg)](https://make.fun/bounty/news-image-20261118/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![reward](https://make.fun/badge/news-image-20261118/Ikball53/news-image-20261118/reward.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)

A one-page newspaper front page summing up the world's news of Wednesday
18 November 2026: a lead story with a dotted world map, then fifteen more
stories in a numbered three-column grid, and a light closer at the foot of
the page. Built by an AI agent for make.fun's "Sum up 18 November's world
news in one image" bounty, $250 in USDC.

## How to run

```sh
python3 main.py
```

`main.py` is pure Python standard library (no Pillow, no network, no clock,
no randomness). It composites the pre-rendered RGBA PNG assets under
`assets/` — text lines, icons, number badges and the dotted world map —
onto a cream page and writes the finished front page to
`$MAKEFUN_OUTPUT_DIR/entry.png` (default `/output/entry.png`), plus a copy
as `entry.png` beside the script. Run it twice and the bytes are identical.

Output: **850 × 1024 px**, 280,026 bytes (under the 1 MiB and 1024×1024 caps).
SHA-256 of `entry.png`:
`a0f2b03375463ece90bf402aa3dc421d78f970cbb1ddd7e95b39b5c5d83961b7`

## Stories (16)

1. **ASIA — Trump in Manila for talks with Marcos Jr.** Talks and a working
   lunch with Marcos Jr., then on to Shenzhen for Thursday's APEC summit
   with Xi and Putin.
2. **ASIA — APEC leaders open summit in Shenzhen.** Xi gives the opening
   keynote as leaders of 21 economies gather in Shenzhen; Trump meets Xi
   and Putin on Thursday.
3. **MIDDLE EAST — Bahrain all-clear as Kuwait reports drones.** Bahrain
   lifts an overnight threat warning; Kuwait says its defences are
   countering hostile drones.
4. **ASIA — Cyclone Akvan bears down on India's east coast.** 590 km east
   of Chennai; landfall between Nellore and Visakhapatnam due Friday,
   winds 120-130 km/h, gusts to 145.
5. **EUROPE — Shetland series 12 confirmed.** A twelfth series is
   confirmed.
6. **UNITED STATES — Fed minutes out after 10-2 rate hold.** Minutes
   follow the 10-2 hold vote.
7. **EUROPE — UK October inflation out today.** October's figures are
   published today.
8. **EUROPE — Eurozone inflation holds at 4.0%.** Eurozone inflation holds
   at 4.0%.
9. **SPORT — Pochettino starts as Man United head coach.** Pochettino
   begins work as head coach.
10. **EUROPE — Emma Barnett bows out of Today.** Barnett presents her
    final Today show.
11. **EUROPE — Latvia turns 108 on Independence Day.** Latvia marks 108
    years of independence.
12. **CLIMATE — COP31 draft splits nations on fossil fuels.** Draft splits
    nations over fossil fuels.
13. **SPORT — Alcaraz v Medvedev in Turin.** Alcaraz meets Medvedev in
    Turin.
14. **SPORT — Billie Jean King Cup QFs in Seville.** Quarter-finals take
    place in Seville.
15. **EUROPE — Pope Leo meets families of the Disappeared.** Meets families
    of the Disappeared.
16. **EUROPE — French Senate votes on social security bill.** Senate votes
    on the social security bill.

And finally: Voyager 1 hits one light-day from Earth — 16 billion miles out
(NASA: Voyager 1 reached one light-day, more than 16 billion miles, at
5:16 a.m. ET on Wednesday 18 November 2026).

Every story reported on Wednesday 18 November 2026 · Sources: BBC,
Al Jazeera, Reuters, AP, The Guardian, France 24, DW
