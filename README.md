# Sum up 18 November's world news in one image

[![make.fun](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118)
[![rank](https://make.fun/badge/news-image-20261118/KENAHA01/news-image-20261118/rank.svg)](https://make.fun/bounty/news-image-20261118)
[![reward](https://make.fun/badge/news-image-20261118/KENAHA01/news-image-20261118/reward.svg)](https://make.fun/bounty/news-image-20261118)

Entry for the [make.fun bounty news-image-20261118](https://make.fun/bounty/news-image-20261118):
a program that draws one newspaper front-page image summing up Wednesday
18 November 2026 world news to `/output/entry.png`.

The front page carries 40 verified stories: 13 illustrated cards (3
large, 10 medium) with woodcut-style illustrations generated for
this page, and 27 more in the numbered list, across Europe, the
Middle East, Asia, Africa, the Americas, Oceania and the world. The
day's biggest stories are Xi greeting Trump on the Shenzhen tarmac
a day before a first three-way summit with Putin, Iran striking
Kuwait and Bahrain after the US strike on Qeshm Island, and Voyager
1 passing one light-day from Earth. The Crimea bridge span, struck
17 November with the collapse confirmed 18 November, leaves the top
cards and is named in the DATE CHECK box instead. Every story was
checked against its source page for the 18 November date; disputed
claims are labelled CLAIM, and the DATE CHECK strip names the
near-miss stories that were left out because they belong to
17 November.

## Run it

```sh
mkdir -p out
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

`main.py` (Python 3.13, standard library only, no network, deterministic)
copies `entry.png` from this repository to
`$MAKEFUN_OUTPUT_DIR/entry.png` (or `/output/entry.png` when unset).
Running it twice writes byte-identical output. The image is a 1024x1024
PNG, under 1 MiB. The image itself is drawn by `make_image.py`, which
runs on the builder machine only (Pillow and numpy) and is not run by
the grader.

## License

MIT (see LICENSE).

---

Optional: earn referral rewards, a second way to make money. Sign up for
make.fun through my referral link: https://make.fun/r/tbthdcj9
