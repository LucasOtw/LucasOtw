name: Update profile art

# Rebuilds the heatmap, the neofetch card and the ASCII portrait from public data.
# Daily cron + on every push to main + manual trigger (Actions tab → Run workflow).
on:
  schedule:
    - cron: "23 5 * * *"   # ~07:23 Paris time
  workflow_dispatch: {}
  push:
    branches: [main]
    paths-ignore: ["*.svg", "data/**"]

permissions:
  contents: write

jobs:
  render:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r scripts/requirements.txt
      - name: Scrape public contribution calendar (no token)
        run: python scripts/fetch_contributions.py
      - name: Render SVGs
        working-directory: scripts
        run: |
          python render_heatmap.py
          python render_card.py
          python make_ascii_portrait.py
      - uses: stefanzweifel/git-auto-commit-action@v5
        with:
          commit_message: "chore: refresh profile art [skip ci]"
          file_pattern: "data/contributions.json *.svg"
