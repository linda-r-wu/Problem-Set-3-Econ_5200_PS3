[README.md](https://github.com/user-attachments/files/34406327/README.md)
# Auditing a Staggered Training Programme

## Objective
I checked whether an agency’s difference-in-differences estimate supported its claim that a training programme worked.

## What I did
- Reproduced the Card and Krueger result of about +2.75 full-time-equivalent employees using a two-by-two comparison and a regression.
- Simulated 40 counties across eight boards over twelve years, with staggered adoption, growing treatment effects and shared board shocks.
- Decomposed TWFE and found that already-treated controls carried 37.0% of its weight.
- Estimated cohort-period effects using only never-treated or not-yet-treated controls and plotted an event study.
- Compared default, county-clustered and board-clustered standard errors.
- Used a null-imposed wild cluster bootstrap with all 256 board sign combinations.
- Put the functions in `src/did_toolkit.py` and reviewed AI feedback on my identification argument.

## Key findings
In my latest run, TWFE estimated 2.41 even though the true treatment effects ranged from 3 to 38. Its p-value rose from 0.0117 with default inference to 0.5332 with board clustering; the wild bootstrap gave 0.9688. The agency’s significance claim did not hold up, but that does not establish that the programme had no effect. I recommended keeping funding for now while asking for a better evaluation before a longer-term commitment.
