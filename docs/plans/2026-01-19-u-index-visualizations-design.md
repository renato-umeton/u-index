# U-Index Visualizations Design

## Purpose

Create interactive visualizations demonstrating the utility of the U-index by comparing synthetic researcher profiles with different career stages and leadership styles.

## Destination

- Primary: GitHub repository (`examples/` folder)
- Secondary: Potential inclusion in manuscript if visualizations prove effective

## Researcher Profiles

Eight synthetic profiles covering multiple dimensions:

### Career Stage

| Name | Years | h | U | Description |
|------|-------|---|---|-------------|
| Dr. Early | 5 | 12 | 10 | 5 years post-PhD, primarily first-author experimental work |
| Dr. Midcareer | 12 | 25 | 18 | Mix of independent and supervised research |
| Dr. Senior | 25 | 45 | 22 | Heavy supervision load, leads large lab |

### Leadership Style

| Name | h | U | Description |
|------|---|---|-------------|
| Dr. Independent | 20 | 18 | Runs small lab, does own experiments |
| Dr. Collaborative | 35 | 8 | Hub in large consortiums, many middle-author papers |
| Dr. Balanced | 28 | 14 | Equal leadership and collaboration contributions |

### Edge Cases

| Name | h | U | Description |
|------|---|---|-------------|
| Dr. Consortium | 40 | 3 | Almost entirely middle-author consortium positions |
| Dr. Solo | 15 | 15 | Single-author theoretician, h equals U |

## Visualizations

### A: Bar Chart Comparison

- Grouped bar chart with all 8 researchers
- Two bars per researcher: h-index (blue) and U-index (orange)
- Ordered by h-index descending
- Hover tooltips with persona descriptions
- Shows that high h does not imply high U

### B: Career Trajectories

- Line chart showing h and U over 25 simulated career years
- 3-4 representative trajectories to avoid clutter:
  - Dr. Independent (lines stay close)
  - Dr. Collaborative (lines diverge dramatically)
  - Dr. Senior (gradual divergence)
- Shaded area between lines to emphasize the gap
- Interactive legend to toggle researchers

## Technical Specification

### File Structure

```
examples/
  u_index_visualizations.py
  output/
    comparison_bar_chart.html
    career_trajectories.html
```

### Dependencies

- plotly (for interactive charts)

### Data Model

```python
{
    "name": str,
    "archetype": str,
    "description": str,
    "h": int,
    "u": int,
    "trajectory": [(year, h, u), ...]
}
```

### Trajectory Simulation

- Start h and U at 0
- Each year: h grows by base rate + collaboration bonus
- Each year: U grows by base rate only
- Different archetypes have different collaboration bonuses
- Small random noise for realism

## Output

- Self-contained HTML files viewable in any browser
- Plotly export button allows PNG download
- Can be embedded in README or linked from documentation
