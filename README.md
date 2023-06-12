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
| `S=half \| spicy` | a declaration of [spiciness] (default half) |
| `<P1> <P2> <P3> <P4>` | a list of player names (no hashes, asterisks, leading hyphens, or leading digits) |
| `<R1> <R2> <R3> <R4>` | a declaration of [game results] |
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

Base points are converted by a [multiplier] to a [portion].

### Maximum faan

Declared via `M=<faan>`.

In the event of a [false-win (詐糊)], the player at fault pays out the maximum
self-drawn (自摸) win amount to each other player.
This is to discourage collusion and deliberate false-winning.

### Responsibility

Declared via `R=half | full`.

| Responsibility | Cantonese name |
| - | - |
| `half` | 半銃 |
| `full` | 全銃 |

Determines whether a [discarding (打出)] player bears the payment of the two blameless players.

### Spiciness

Declared via `S=half | spicy`.

Determines whether the exponential rise in multiplier (with respect to number of faan)
is slowed to half-pace (with arithmetic-mean interpolation) when the number of faan exceeds 4.

#### Multiplier

| Number of faan | Multiplier for half-spicy increase<br>(半辣上) | Multiplier for spicy-spicy increase<br>(辣辣上) |
| - | - | - |
| 0 | 1 | 1 |
| 1 | 2 | 2 |
| 2 | 4 | 4 |
| 3 | 8 | 8 |
| 4 | 16 | 16 |
| 5 | 24 | 32 |
| 6 | 32 | 64 |
| 7 | 48 | 128 |
| 8 | 64 | 256 |
| 9 | 96 | 512 |
| 10 | 128 | 1024 |
| 11 | 192 | 2048 |
| 12 | 256 | 4096 |
| 13 | 384 | 8192 |

#### Portion

The multiplier is what converts [base points] to a portion:

$$ \text{Portion} = \text{Base Points} \times \text{Multiplier}. $$

### Player names

Declared via `<P1> <P2> <P3> <P4>`.

Each name must not have hashes, asterisks, leading hyphens, or leading digits.

### Game results

Declared via `<R1> <R2> <R3> <R4>`.

| `<Ri>` | Meaning |
| - | - |
| `<digits>` | winner's number of faan |
| `-` | blameless player |
| `d` | [discarding (打出)] player |
| `g` | [guaranteeing (包自摸)] player |
| `f` | [false-winning (詐糊)] player |

Examples:

#### Draw (摸和)

```
A B C D
- - - -  # draw between A, B, C, D
```

Scores do not change (although the game count is incremented).

#### False-win (詐糊)

```
A B C D
- - - f  # D has a false-win
```

The player at fault pays out the maximum
self-drawn (自摸) win amount to each other player:
- Blameless players (A, B, C) each gain 3 [portions] at [maximum faan]
- Player at fault (D) loses 9 [portions] at [maximum faan]

#### Self-drawn win (自摸)

```
A B C D
8 - - -  # A has a self-drawn win (8 faan)
```

The blameless players each pay the winner one portion:
- Winner (A) gains 3 [portions] at the winning number of faan
- Blameless players (B, C, D) each lose 1 [portion] at the winning number of faan

#### Discarding (打出)

```
A B C D
8 - - d  # A wins (8 faan) from a discard by D
```

Under half [responsibility] (半銃):
- Winner (A) gains 2 [portions] at the winning number of faan
- Blameless players (B, C) each lose a 1/2 [portion] at the winning number of faan
- Player at fault (D) loses 1 [portion] at the winning number of faan

Under full [responsibility] (全銃):
- Winner (A) gains 2 [portions] at the winning number of faan
- Player at fault (D) loses 2 [portions] at the winning number of faan

#### Guaranteeing (包自摸)

```
A B C D
8 - - g  # A wins (8 faan) by self-draw guaranteed by D
```

The player at fault bears all the losses of a self-drawn win:
- Winner (A) gains 3 [portions] at the winning number of faan
- Player at fault (D) loses 3 [portions] at the winning number of faan

The envisaged situation here is that D has supplied enough favourable tiles
for A to have revealed melds indicating significant chance of a high-scoring win
(e.g. 12 same-suited tiles, 2 out of 3 dragon triplets, etc.).
Should such high-scoring win eventuate through self-drawing by A,
then D ought to bear losses on behalf of B and C.


## Output data

| Column | Explanation |
| - | - |
| `name` | player name; bottom row `*` is the aggregate of all players |
| `game_count` | total number of games played |
| `win_count` | total number of games won |
| `win_fraction` | `win_count` divided by `game_count` |
| `net_score` | cumulative zero-sum score |
| `net_score_per_game` | `net_score` divided by `game_count` |


[LICENSE]: LICENSE
[base points]: #base-points
[maximum faan]: #maximum-faan
[responsibility]: #responsibility
[spiciness]: #spiciness
[portion]: #portion
[portions]: #portion
[player names]: #player-names
[game results]: #game-results
[false-win (詐糊)]: #false-win-詐糊
[false-winning (詐糊)]: #false-win-詐糊
[discarding (打出)]: #discarding-打出
[guaranteeing (包自摸)]: #guaranteeing-包自摸
