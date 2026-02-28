# Source Shortlist (Stage 1 Stabilization)

_Last updated: 2026-02-28 18:36 UTC_

Stage 1 executed: approved candidates were promoted into `data/sources.json -> sources[]`, feed health was validated, and pipeline artifacts were regenerated.

## Promotions completed

1. **Rob Quickenden** (`rob-quickenden`) — https://robquickenden.blog/feed
2. **Karl-Johan Spiik (Karlex)** (`karlex`) — https://www.karlex.fi/feed

Both feeds returned HTTP 200 and parsed successfully.

## Candidate queue updates

- Removed from `candidates.add` after promotion:
  - `rob-quickenden`
  - `karlex`
- Existing rejected feeds remain in `candidates.reject` for fallback tracking.

## Remaining pending candidates

- `forwardforever`
- `megan-v-walker`
- `nishant-rana`
- `readyxrm`
- `eliostruyf`
- `sharepains`
- `michelcarlo`

## Feed health summary (post-promotion)

- Queue build completed and produced 24 validated items.
- Hard feed failure still requiring fallback handling:
  - `azure-updates` — XML parse failure (`not well-formed (invalid token): line 5, column 31`)
