# mahjong-scorer

A Python scorer for Mahjong (HK rules).

Licensed under MIT No Attribution (MIT-0), see [LICENSE].


## Usage

```bash
$ path/to/mahjong.py [-h] [-v] scores.txt

Score some games of Mahjong (HK rules).

positional arguments:
  scores.txt     name of scores file; output written to `{scores.txt}.tsv`

options:
  -h, --help     show this help message and exit
  -v, --version  show program's version number and exit
```


## Scores file syntax

The scorer reads a plain-text file of Big Two scores.
Each line must have one of the following forms:

| Form | Meaning |
| - | - |
| `<yyyy>-<mm>-<dd>` | a date |
| `B=<base>` | a declaration of [base points] (default 1) |
| `M=<faan>` | a declaration of [maximum faan] (default 13) |
| `R=half \| full` | a declaration of [responsibility] (default full) |
| `S=half \| spicy` | a declaration of spiciness (default half) |
| `<P1> <P2> <P3> <P4>` | a list of player names (no hashes, asterisks, leading hyphens, or leading digits) |
| `<R1> <R2> <R3> <R4>` | a declaration of game results |
| `# <comment>` | a comment, also allowed at the end of the forms above |

For details, see the linked explanations.


## Detailed explanations

### Base points

Declared via `B=<base>`.

For a 0-faan or chicken win (雞糊) under half responsibility (半銃):
- The two blameless players each pay `<base>/2` to the winner.
- The discarding (打出) player pays `<base>` to the winner.

| `<base>` | Cantonese name | English translation | Blameless payment | Discarding payment |
| - | - | - | - | - |
| 0.5 | 二五雞 | two & five chicken | 0.25 | 0.5 |
| 1 | 五一 | fives & ones | 0.5 | 1 |
| 2 | 一二蚊 | one & two bucks | 1 | 2 |

### Maximum faan

Declared via `M=<faan>`.

In the event of a false-win (詐糊), the player at fault pays out the maximum
self-drawn (自摸) win amount to each other player.
This is to discourage collusion and deliberate false-winning.

### Responsibility

Declared via `R=half | full`.

| Responsibility | Cantonese name |
| - | - |
| `half` | 半銃 |
| `full` | 全銃 |

Determines whether a discarding (打出) player bears the payment of the two blameless players.


[LICENSE]: LICENSE
[base points]: #base-points
[maximum faan]: #maximum-faan
[responsibility]: #responsibility
