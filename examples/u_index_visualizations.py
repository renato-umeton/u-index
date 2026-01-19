"""
U-Index Visualizations

Interactive visualizations demonstrating how the U-index differentiates
researchers with similar h-indices but different leadership profiles.

Usage:
    python examples/u_index_visualizations.py

Output:
    examples/output/comparison_bar_chart.html
    examples/output/career_trajectories.html
"""

import random
from pathlib import Path

import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def hex_to_rgba(hex_color: str, alpha: float) -> str:
    """Convert hex color to rgba string."""
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return f"rgba({r}, {g}, {b}, {alpha})"


# Researcher profiles with synthetic data
RESEARCHERS = [
    {
        "name": "Dr. Early",
        "archetype": "Career Stage",
        "description": "5 years post-PhD, primarily first-author experimental work",
        "h": 12,
        "u": 10,
        "years": 5,
        "h_base_rate": 2.4,
        "collab_bonus": 0.4,
    },
    {
        "name": "Dr. Midcareer",
        "archetype": "Career Stage",
        "description": "12 years in, mix of independent and supervised research",
        "h": 25,
        "u": 18,
        "years": 12,
        "h_base_rate": 1.5,
        "collab_bonus": 0.58,
    },
    {
        "name": "Dr. Senior",
        "archetype": "Career Stage",
        "description": "25 years experience, leads large lab with heavy supervision",
        "h": 45,
        "u": 22,
        "years": 25,
        "h_base_rate": 0.88,
        "collab_bonus": 0.92,
    },
    {
        "name": "Dr. Independent",
        "archetype": "Leadership Style",
        "description": "Runs small lab, still does own experiments",
        "h": 20,
        "u": 18,
        "years": 15,
        "h_base_rate": 1.2,
        "collab_bonus": 0.13,
    },
    {
        "name": "Dr. Collaborative",
        "archetype": "Leadership Style",
        "description": "Hub in large consortiums, many middle-author papers",
        "h": 35,
        "u": 8,
        "years": 15,
        "h_base_rate": 0.53,
        "collab_bonus": 1.8,
    },
    {
        "name": "Dr. Balanced",
        "archetype": "Leadership Style",
        "description": "Equal leadership and collaboration contributions",
        "h": 28,
        "u": 14,
        "years": 15,
        "h_base_rate": 0.93,
        "collab_bonus": 0.93,
    },
    {
        "name": "Dr. Consortium",
        "archetype": "Edge Case",
        "description": "Almost entirely middle-author consortium positions",
        "h": 40,
        "u": 3,
        "years": 20,
        "h_base_rate": 0.15,
        "collab_bonus": 1.85,
    },
    {
        "name": "Dr. Solo",
        "archetype": "Edge Case",
        "description": "Single-author theoretician, all papers are first/last",
        "h": 15,
        "u": 15,
        "years": 20,
        "h_base_rate": 0.75,
        "collab_bonus": 0.0,
    },
]


def generate_trajectory(researcher: dict, seed: int = 42) -> list[tuple[int, int, int]]:
    """
    Generate a career trajectory showing h and U values over time.

    Returns list of (year, h, u) tuples.
    """
    random.seed(seed + hash(researcher["name"]))

    trajectory = [(0, 0, 0)]
    h_cumulative = 0.0
    u_cumulative = 0.0

    h_base = researcher["h_base_rate"]
    collab = researcher["collab_bonus"]

    for year in range(1, researcher["years"] + 1):
        noise_h = random.uniform(-0.2, 0.3)
        noise_u = random.uniform(-0.15, 0.25)

        h_cumulative += h_base + collab + noise_h
        u_cumulative += h_base + noise_u

        # Ensure monotonic growth
        h_cumulative = max(h_cumulative, trajectory[-1][1])
        u_cumulative = max(u_cumulative, trajectory[-1][2])

        # U can never exceed h (mathematical property)
        u_cumulative = min(u_cumulative, h_cumulative)

        trajectory.append((year, int(h_cumulative), int(u_cumulative)))

    final_h = researcher["h"]
    final_u = researcher["u"]
    scale_h = final_h / max(trajectory[-1][1], 1)
    scale_u = final_u / max(trajectory[-1][2], 1)

    scaled = [(0, 0, 0)]
    for year, h, u in trajectory[1:]:
        scaled_h = int(h * scale_h)
        scaled_u = int(u * scale_u)
        # Ensure U <= h after scaling
        scaled_u = min(scaled_u, scaled_h)
        scaled.append((year, scaled_h, scaled_u))

    scaled[-1] = (researcher["years"], final_h, final_u)

    return scaled


def create_comparison_chart() -> go.Figure:
    """Create grouped bar chart comparing h and U across all researchers."""

    sorted_researchers = sorted(RESEARCHERS, key=lambda r: r["h"], reverse=True)

    names = [r["name"] for r in sorted_researchers]
    h_values = [r["h"] for r in sorted_researchers]
    u_values = [r["u"] for r in sorted_researchers]
    descriptions = [r["description"] for r in sorted_researchers]
    archetypes = [r["archetype"] for r in sorted_researchers]

    ratios = [f"U/h = {u/h:.0%}" for h, u in zip(h_values, u_values)]
    collab_values = [h - u for h, u in zip(h_values, u_values)]

    fig = go.Figure()

    # U-index: solid blue at bottom (leadership impact)
    fig.add_trace(go.Bar(
        name="U-index (leadership)",
        x=names,
        y=u_values,
        marker_color="rgba(0, 115, 200, 1)",
        customdata=list(zip(descriptions, archetypes, ratios)),
        hovertemplate=(
            "<b>%{x}</b><br>"
            "U-index: %{y}<br>"
            "%{customdata[2]}<br><br>"
            "<i>%{customdata[0]}</i><br>"
            "Category: %{customdata[1]}"
            "<extra></extra>"
        ),
    ))

    # (h - U): semi-transparent gray on top (collaboration contribution)
    fig.add_trace(go.Bar(
        name="Collaboration contribution",
        x=names,
        y=collab_values,
        marker_color="rgba(107, 114, 128, 0.5)",
        customdata=list(zip(h_values, collab_values)),
        hovertemplate=(
            "<b>%{x}</b><br>"
            "h-index: %{customdata[0]}<br>"
            "Collaboration contribution: %{y}"
            "<extra></extra>"
        ),
    ))

    fig.update_layout(
        title={
            "text": "H-index vs U-index Across Researcher Profiles",
            "subtitle": {
                "text": "Blue = leadership impact (U-index). Gray = additional impact from collaboration.",
            },
        },
        xaxis_title="Researcher",
        yaxis_title="Index Value",
        barmode="stack",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        template="plotly_white",
        hoverlabel=dict(align="left"),
    )

    for i, (name, ratio) in enumerate(zip(names, ratios)):
        fig.add_annotation(
            x=name,
            y=h_values[i] + 2,
            text=ratio,
            showarrow=False,
            font=dict(size=10, color="#666"),
        )

    return fig


def create_trajectory_chart() -> go.Figure:
    """Create line chart showing career trajectories for selected researchers."""

    selected = ["Dr. Independent", "Dr. Collaborative", "Dr. Senior", "Dr. Solo"]

    colors = {
        "Dr. Independent": "#ef4444",
        "Dr. Collaborative": "#22c55e",
        "Dr. Senior": "#3b82f6",
        "Dr. Solo": "#a855f7",
    }

    fig = go.Figure()

    # Add legend key for line styles
    fig.add_trace(go.Scatter(
        x=[None],
        y=[None],
        mode="lines",
        name="U-index (solid)",
        line=dict(color="#666", width=2),
        legendgroup="legend_key",
    ))
    fig.add_trace(go.Scatter(
        x=[None],
        y=[None],
        mode="lines",
        name="h-index (dashed)",
        line=dict(color="#666", width=2, dash="dash"),
        legendgroup="legend_key",
    ))

    for researcher in RESEARCHERS:
        if researcher["name"] not in selected:
            continue

        name = researcher["name"]
        color = colors[name]
        trajectory = generate_trajectory(researcher)

        years = [t[0] for t in trajectory]
        h_vals = [t[1] for t in trajectory]
        u_vals = [t[2] for t in trajectory]

        fig.add_trace(go.Scatter(
            x=years,
            y=u_vals,
            mode="lines",
            name=name,
            line=dict(color=color, width=2),
            legendgroup=name,
            hovertemplate=f"<b>{name}</b><br>Year %{{x}}<br>U-index: %{{y}}<extra></extra>",
        ))

        fig.add_trace(go.Scatter(
            x=years,
            y=h_vals,
            mode="lines",
            name=f"{name} h",
            line=dict(color=color, width=2, dash="dash"),
            legendgroup=name,
            showlegend=False,
            hovertemplate=f"<b>{name}</b><br>Year %{{x}}<br>h-index: %{{y}}<extra></extra>",
        ))

        # Fill under U-index line (lower bound)
        fig.add_trace(go.Scatter(
            x=years,
            y=u_vals,
            mode="none",
            fill="tozeroy",
            fillcolor=hex_to_rgba(color, 0.3),
            showlegend=False,
            legendgroup=name,
            hoverinfo="skip",
        ))

        # Fill between h and U (collaboration gap)
        fig.add_trace(go.Scatter(
            x=years + years[::-1],
            y=h_vals + u_vals[::-1],
            mode="none",
            fill="toself",
            fillcolor=hex_to_rgba(color, 0.1),
            showlegend=False,
            legendgroup=name,
            hoverinfo="skip",
        ))

    fig.update_layout(
        title={
            "text": "Career Trajectories: How H-index and U-index Diverge Over Time",
            "subtitle": {
                "text": "Solid fill = U-index (lower bound). Light fill = collaboration gap. Click legend to toggle.",
            },
        },
        xaxis_title="Career Year",
        yaxis_title="Index Value",
        template="plotly_white",
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.15,
            xanchor="left",
            x=0,
            groupclick="togglegroup",
        ),
        hovermode="x unified",
        margin=dict(b=100),
    )

    return fig


def create_trajectory_grid() -> go.Figure:
    """Create 2x2 grid showing each researcher's trajectory in separate panes."""

    selected = ["Dr. Independent", "Dr. Collaborative", "Dr. Senior", "Dr. Solo"]

    colors = {
        "Dr. Independent": "#ef4444",
        "Dr. Collaborative": "#22c55e",
        "Dr. Senior": "#3b82f6",
        "Dr. Solo": "#a855f7",
    }

    fig = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=selected,
        horizontal_spacing=0.1,
        vertical_spacing=0.15,
    )

    positions = [(1, 1), (1, 2), (2, 1), (2, 2)]

    for i, name in enumerate(selected):
        researcher = next(r for r in RESEARCHERS if r["name"] == name)
        color = colors[name]
        row, col = positions[i]
        trajectory = generate_trajectory(researcher)

        years = [t[0] for t in trajectory]
        h_vals = [t[1] for t in trajectory]
        u_vals = [t[2] for t in trajectory]

        # U-index line (solid)
        fig.add_trace(go.Scatter(
            x=years,
            y=u_vals,
            mode="lines",
            name="U-index",
            line=dict(color=color, width=2),
            legendgroup="u",
            showlegend=(i == 0),
            hovertemplate=f"Year %{{x}}<br>U-index: %{{y}}<extra></extra>",
        ), row=row, col=col)

        # h-index line (dashed)
        fig.add_trace(go.Scatter(
            x=years,
            y=h_vals,
            mode="lines",
            name="h-index",
            line=dict(color=color, width=2, dash="dash"),
            legendgroup="h",
            showlegend=(i == 0),
            hovertemplate=f"Year %{{x}}<br>h-index: %{{y}}<extra></extra>",
        ), row=row, col=col)

        # Fill under U-index (lower bound)
        fig.add_trace(go.Scatter(
            x=years,
            y=u_vals,
            mode="none",
            fill="tozeroy",
            fillcolor=hex_to_rgba(color, 0.3),
            showlegend=False,
            hoverinfo="skip",
        ), row=row, col=col)

        # Fill between h and U (collaboration gap)
        fig.add_trace(go.Scatter(
            x=years + years[::-1],
            y=h_vals + u_vals[::-1],
            mode="none",
            fill="toself",
            fillcolor=hex_to_rgba(color, 0.1),
            showlegend=False,
            hoverinfo="skip",
        ), row=row, col=col)

    fig.update_layout(
        title={
            "text": "Career Trajectories by Researcher Profile",
            "subtitle": {
                "text": "Solid = U-index (lower bound), Dashed = h-index. Shaded area shows collaboration gap.",
            },
        },
        template="plotly_white",
        height=700,
        showlegend=False,
    )

    fig.update_xaxes(title_text="Career Year")
    fig.update_yaxes(title_text="Index Value")

    return fig


def create_scatter_plot() -> go.Figure:
    """Create scatter plot showing h vs U for all researchers."""

    fig = go.Figure()

    # Add diagonal line (U = h)
    max_val = max(r["h"] for r in RESEARCHERS) + 5
    fig.add_trace(go.Scatter(
        x=[0, max_val],
        y=[0, max_val],
        mode="lines",
        name="U = h (perfect leadership)",
        line=dict(color="#999", width=1, dash="dash"),
        hoverinfo="skip",
    ))

    # Color by archetype
    archetype_colors = {
        "Career Stage": "#3b82f6",
        "Leadership Style": "#22c55e",
        "Edge Case": "#f97316",
    }

    # Add researchers as points
    for archetype in ["Career Stage", "Leadership Style", "Edge Case"]:
        researchers = [r for r in RESEARCHERS if r["archetype"] == archetype]
        fig.add_trace(go.Scatter(
            x=[r["h"] for r in researchers],
            y=[r["u"] for r in researchers],
            mode="markers+text",
            name=archetype,
            marker=dict(
                size=12,
                color=archetype_colors[archetype],
            ),
            text=[r["name"].replace("Dr. ", "") for r in researchers],
            textposition="top center",
            textfont=dict(size=10),
            customdata=[r["description"] for r in researchers],
            hovertemplate=(
                "<b>%{text}</b><br>"
                "h-index: %{x}<br>"
                "U-index: %{y}<br>"
                "U/h: %{customdata}<br>"
                "<extra></extra>"
            ),
        ))

    fig.update_layout(
        title={
            "text": "H-index vs U-index: Leadership Impact Profile",
            "subtitle": {
                "text": "Distance below diagonal = impact from collaborative (non-leadership) contributions",
            },
        },
        xaxis_title="h-index (total impact)",
        yaxis_title="U-index (leadership impact)",
        template="plotly_white",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
        ),
        xaxis=dict(range=[0, max_val], constrain="domain"),
        yaxis=dict(range=[0, max_val], scaleanchor="x", scaleratio=1),
    )

    return fig


def create_scatter_manuscript() -> plt.Figure:
    """Create publication-quality scatter plot for manuscript."""

    fig, ax = plt.subplots(figsize=(5, 5), dpi=300)

    # Add diagonal line (U = h)
    max_val = max(r["h"] for r in RESEARCHERS) + 5
    ax.plot([0, max_val], [0, max_val], color="#999", linewidth=1, linestyle="--",
            label="U = h", zorder=1)

    # Fill above diagonal to show "impossible zone" (U cannot exceed h)
    ax.fill_between([0, max_val], [0, max_val], [max_val, max_val], alpha=0.05, color="#999")

    # Color and marker by archetype
    archetype_styles = {
        "Career Stage": {"color": "#3b82f6", "marker": "o"},
        "Leadership Style": {"color": "#22c55e", "marker": "s"},
        "Edge Case": {"color": "#f97316", "marker": "^"},
    }

    # Plot researchers
    for archetype, style in archetype_styles.items():
        researchers = [r for r in RESEARCHERS if r["archetype"] == archetype]
        h_vals = [r["h"] for r in researchers]
        u_vals = [r["u"] for r in researchers]
        ax.scatter(h_vals, u_vals, c=style["color"], marker=style["marker"],
                   s=80, label=archetype, zorder=3, edgecolors="white", linewidths=0.5)

        # Add labels
        for r in researchers:
            label = r["name"].replace("Dr. ", "")
            ha = "center"
            if label == "Independent":
                ha = "right"
            elif label in ("Midcareer", "Balanced"):
                ha = "left"
            ax.annotate(label, (r["h"], r["u"]), textcoords="offset points",
                        xytext=(0, 8), ha=ha, fontsize=8)

    ax.set_xlabel("h-index (total impact)", fontsize=10)
    ax.set_ylabel("U-index (leadership impact)", fontsize=10)
    ax.set_xlim(0, max_val)
    ax.set_ylim(0, max_val)
    ax.set_aspect("equal")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(fontsize=8, loc="upper left", frameon=False)
    ax.tick_params(labelsize=9)

    # Add annotation explaining the diagonal
    ax.annotate("U = h\n(all papers are\nfirst/last authored)",
                xy=(max_val - 3, max_val - 3), fontsize=7, color="#666", ha="right",
                style="italic")

    plt.tight_layout()
    return fig


def create_bar_chart_manuscript() -> plt.Figure:
    """Create publication-quality stacked bar chart for README."""

    sorted_researchers = sorted(RESEARCHERS, key=lambda r: r["h"], reverse=True)

    names = [r["name"].replace("Dr. ", "") for r in sorted_researchers]
    h_values = [r["h"] for r in sorted_researchers]
    u_values = [r["u"] for r in sorted_researchers]
    collab_values = [h - u for h, u in zip(h_values, u_values)]
    ratios = [f"{u/h:.0%}" for h, u in zip(h_values, u_values)]

    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)

    x = range(len(names))

    # U-index bars (bottom)
    ax.bar(x, u_values, color="#0073c8", label="U-index (leadership)")

    # Collaboration bars (top)
    ax.bar(x, collab_values, bottom=u_values, color="#6b7280", alpha=0.5,
           label="Collaboration contribution")

    # Add ratio labels
    for i, (h, ratio) in enumerate(zip(h_values, ratios)):
        ax.annotate(f"U/h={ratio}", (i, h + 1), ha="center", fontsize=8, color="#666")

    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=45, ha="right")
    ax.set_xlabel("Researcher", fontsize=10)
    ax.set_ylabel("Index Value", fontsize=10)
    ax.set_title("H-index Decomposition: Leadership vs Collaboration", fontsize=12, fontweight="bold")
    ax.legend(loc="upper right", frameon=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()
    return fig


def create_manuscript_figure() -> plt.Figure:
    """Create publication-quality figure for manuscript."""

    # Grouped by archetype: Career Stage + Solo (row 1), Leadership Style + Consortium (row 2)
    selected = [
        "Dr. Early", "Dr. Midcareer", "Dr. Senior", "Dr. Solo",
        "Dr. Independent", "Dr. Balanced", "Dr. Collaborative", "Dr. Consortium"
    ]

    colors = {
        "Dr. Solo": "#a855f7",
        "Dr. Independent": "#ef4444",
        "Dr. Early": "#3b82f6",
        "Dr. Midcareer": "#0ea5e9",
        "Dr. Balanced": "#22c55e",
        "Dr. Senior": "#14b8a6",
        "Dr. Collaborative": "#f97316",
        "Dr. Consortium": "#ec4899",
    }

    fig, axes = plt.subplots(2, 4, figsize=(14, 6), dpi=300)
    axes = axes.flatten()

    for i, name in enumerate(selected):
        ax = axes[i]
        researcher = next(r for r in RESEARCHERS if r["name"] == name)
        color = colors[name]
        trajectory = generate_trajectory(researcher)

        years = [t[0] for t in trajectory]
        h_vals = [t[1] for t in trajectory]
        u_vals = [t[2] for t in trajectory]

        # Fill under U-index (lower bound)
        ax.fill_between(years, 0, u_vals, alpha=0.3, color=color, linewidth=0)

        # Fill between h and U (collaboration gap)
        ax.fill_between(years, u_vals, h_vals, alpha=0.1, color=color, linewidth=0)

        # U-index line (solid)
        ax.plot(years, u_vals, color=color, linewidth=2, label="U-index")

        # h-index line (dashed)
        ax.plot(years, h_vals, color=color, linewidth=2, linestyle="--", label="h-index")

        ax.set_title(name, fontsize=11, fontweight="bold")
        ax.set_xlabel("Career Year", fontsize=9)
        ax.set_ylabel("Index Value", fontsize=9)
        ax.tick_params(labelsize=8)
        ax.set_xlim(0, None)
        ax.set_ylim(0, None)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        # Add legend only to first subplot
        if i == 0:
            ax.legend(fontsize=8, loc="upper left", frameon=False)

    fig.suptitle(
        "Career Trajectories: H-index vs U-index Divergence",
        fontsize=12,
        fontweight="bold",
        y=0.98,
    )

    plt.tight_layout()
    return fig


def main():
    """Generate all visualizations."""
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)

    print("Generating comparison bar chart...")
    bar_chart = create_comparison_chart()
    bar_chart.write_html(output_dir / "comparison_bar_chart.html")
    print(f"  Saved to {output_dir / 'comparison_bar_chart.html'}")

    print("Generating career trajectories chart...")
    trajectory_chart = create_trajectory_chart()
    trajectory_chart.write_html(output_dir / "career_trajectories.html")
    print(f"  Saved to {output_dir / 'career_trajectories.html'}")

    print("Generating career trajectories grid...")
    trajectory_grid = create_trajectory_grid()
    trajectory_grid.write_html(output_dir / "career_trajectories_grid.html")
    print(f"  Saved to {output_dir / 'career_trajectories_grid.html'}")

    print("Generating scatter plot...")
    scatter = create_scatter_plot()
    scatter.write_html(output_dir / "scatter_h_vs_u.html")
    print(f"  Saved to {output_dir / 'scatter_h_vs_u.html'}")

    print("Generating scatter plot manuscript figure...")
    scatter_fig = create_scatter_manuscript()
    scatter_fig.savefig(
        output_dir / "figure_scatter.pdf",
        bbox_inches="tight",
        pad_inches=0.02,
        facecolor="white",
    )
    scatter_fig.savefig(
        output_dir / "figure_scatter.png",
        bbox_inches="tight",
        pad_inches=0.02,
        facecolor="white",
        dpi=300,
    )
    plt.close(scatter_fig)
    print(f"  Saved to {output_dir / 'figure_scatter.pdf'}")
    print(f"  Saved to {output_dir / 'figure_scatter.png'}")

    print("Generating bar chart manuscript figure...")
    bar_fig = create_bar_chart_manuscript()
    bar_fig.savefig(
        output_dir / "figure_bar_chart.png",
        bbox_inches="tight",
        pad_inches=0.02,
        facecolor="white",
        dpi=300,
    )
    plt.close(bar_fig)
    print(f"  Saved to {output_dir / 'figure_bar_chart.png'}")

    print("Generating manuscript figure...")
    manuscript_fig = create_manuscript_figure()
    manuscript_fig.savefig(
        output_dir / "figure_trajectories.pdf",
        bbox_inches="tight",
        facecolor="white",
    )
    manuscript_fig.savefig(
        output_dir / "figure_trajectories.png",
        bbox_inches="tight",
        facecolor="white",
        dpi=300,
    )
    plt.close(manuscript_fig)
    print(f"  Saved to {output_dir / 'figure_trajectories.pdf'}")
    print(f"  Saved to {output_dir / 'figure_trajectories.png'}")

    print("Done!")


if __name__ == "__main__":
    main()
