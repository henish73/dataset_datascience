#!/usr/bin/env python3
"""
Clean Economic Analysis Figure Generator
======================================
Generates three key figures for V1→V2→V3 economic analysis:
1. Usage Share Trends Across Economic Index Reports
2. Notable Task Changes (Growing/Declining Tasks)
3. Automation vs Augmentation Evolution

ASSUMPTIONS:
- V1/V2/V3 use same task taxonomy
- GLOBAL geo_id is representative
- Missing values = 0% usage
- Percentages don't need renormalization
"""

import os
import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# Use default matplotlib styling
plt.style.use("default")

# Configuration
FILES = {
    "v1_tasks": "../data/input/task_pct_v1.csv",
    "v2_tasks": "../data/input/task_pct_v2.csv",
    "v3_data": "../data/intermediate/aei_raw_claude_ai_2025-08-04_to_2025-08-11.csv",
    "v1_auto": "../data/input/automation_vs_augmentation_v1.csv",
    "v2_auto": "../data/input/automation_vs_augmentation_v2.csv",
    "onet": "../data/intermediate/onet_task_statements.csv",
    "soc": "../data/intermediate/soc_structure.csv",
}

AUTOMATION_TYPES = ["directive", "feedback_loop"]
AUGMENTATION_TYPES = ["validation", "task_iteration", "learning"]
MIN_THRESHOLD = 1.0
COLORS = {
    "increase": "#2E8B57",
    "decrease": "#CD5C5C",
    "automation": "#FF6B6B",
    "augmentation": "#4ECDC4",
}

# ============================================================================
# DATA LOADING
# ============================================================================


def load_task_data(filepath, version_name):
    """Load and validate task percentage data for any version."""
    if not Path(filepath).exists():
        raise FileNotFoundError(f"Missing {version_name} data: {filepath}")

    df = pd.read_csv(filepath)

    if version_name == "V3":
        # Filter V3 data for global onet tasks
        df = df[
            (df["geo_id"] == "GLOBAL")
            & (df["facet"] == "onet_task")
            & (df["variable"] == "onet_task_pct")
        ].copy()
        df = df.rename(columns={"cluster_name": "task_name", "value": "pct"})

        # Remove "not_classified" from V3 for fair comparison with V1/V2
        # Keep "none" as it represents legitimate unclassifiable tasks across all versions
        not_classified_pct = df[df["task_name"] == "not_classified"]["pct"].sum()
        df = df[df["task_name"] != "not_classified"].copy()

        # Renormalize V3 to 100% after removing not_classified
        if not_classified_pct > 0:
            remaining_total = df["pct"].sum()
            normalization_factor = 100 / remaining_total
            df["pct"] = df["pct"] * normalization_factor
            print(
                f"  → Removed {not_classified_pct:.1f}% not_classified, renormalized by {normalization_factor:.3f}x"
            )

    # Validate structure
    if "task_name" not in df.columns or "pct" not in df.columns:
        raise ValueError(f"{version_name} data missing required columns")

    # Normalize task names and validate totals
    df["task_name"] = df["task_name"].str.lower().str.strip()
    total = df["pct"].sum()

    if not (80 <= total <= 120):
        warnings.warn(
            f"{version_name} percentages sum to {total:.1f}% (expected ~100%)",
            stacklevel=2,
        )

    print(f"✓ {version_name}: {len(df)} tasks, {total:.1f}% coverage")
    return df[["task_name", "pct"]]


def load_automation_data():
    """Load automation/collaboration data for all versions."""
    result = {}

    # V1 and V2 - always renormalize to 100%
    for version in ["v1", "v2"]:
        df = pd.read_csv(FILES[f"{version}_auto"])

        # Always renormalize to 100%
        total = df["pct"].sum()
        normalization_factor = 100 / total
        df["pct"] = df["pct"] * normalization_factor
        print(
            f"  → {version.upper()} automation: renormalized from {total:.1f}% to 100.0%"
        )

        result[version] = df

    # V3 from processed data
    df = pd.read_csv(FILES["v3_data"])
    v3_collab = df[
        (df["geo_id"] == "GLOBAL")
        & (df["facet"] == "collaboration")
        & (df["level"] == 0)
        & (df["variable"] == "collaboration_pct")
    ].copy()
    v3_collab = v3_collab.rename(
        columns={"cluster_name": "interaction_type", "value": "pct"}
    )

    # Remove "not_classified" from V3 collaboration data for fair comparison
    not_classified_pct = v3_collab[v3_collab["interaction_type"] == "not_classified"][
        "pct"
    ].sum()
    v3_collab = v3_collab[v3_collab["interaction_type"] != "not_classified"].copy()

    # Renormalize V3 collaboration to 100% after removing not_classified
    if not_classified_pct > 0:
        remaining_total = v3_collab["pct"].sum()
        normalization_factor = 100 / remaining_total
        v3_collab["pct"] = v3_collab["pct"] * normalization_factor
        print(
            f"  → V3 collaboration: removed {not_classified_pct:.1f}% not_classified, renormalized by {normalization_factor:.3f}x"
        )

    result["v3"] = v3_collab[["interaction_type", "pct"]]

    print(f"✓ Automation data loaded for all versions")
    return result


def load_occupational_mapping():
    """Load O*NET to SOC mapping data."""
    onet_df = pd.read_csv(FILES["onet"])
    soc_df = pd.read_csv(FILES["soc"]).dropna(subset=["Major Group"])

    onet_df["soc_major_group"] = onet_df["O*NET-SOC Code"].str[:2]
    soc_df["soc_major_group"] = soc_df["Major Group"].str[:2]

    merged = onet_df.merge(
        soc_df[["soc_major_group", "SOC or O*NET-SOC 2019 Title"]], on="soc_major_group"
    )
    merged["task_normalized"] = merged["Task"].str.lower().str.strip()

    print(f"✓ Occupational mapping: {merged['soc_major_group'].nunique()} SOC groups")
    return merged


# ============================================================================
# ANALYSIS
# ============================================================================


def analyze_occupational_trends(task_data, onet_soc_data):
    """Analyze occupational category trends across versions."""

    def aggregate_by_occupation(df):
        merged = df.merge(
            onet_soc_data[
                ["task_normalized", "SOC or O*NET-SOC 2019 Title"]
            ].drop_duplicates(),
            left_on="task_name",
            right_on="task_normalized",
            how="left",
        )

        unmapped = merged[merged["SOC or O*NET-SOC 2019 Title"].isna()]
        # Only warn if there are real unmapped tasks (not just "none" and "not_classified")
        real_unmapped = unmapped[
            ~unmapped["task_name"].isin(["none", "not_classified"])
        ]
        if len(real_unmapped) > 0:
            real_unmapped_pct = real_unmapped["pct"].sum()
            warnings.warn(
                f"{real_unmapped_pct:.1f}% of tasks unmapped to occupational categories",
                stacklevel=2,
            )

        return merged.groupby("SOC or O*NET-SOC 2019 Title")["pct"].sum()

    # Aggregate all versions
    comparison_df = pd.DataFrame(
        {
            "v1": aggregate_by_occupation(task_data["v1"]),
            "v2": aggregate_by_occupation(task_data["v2"]),
            "v3": aggregate_by_occupation(task_data["v3"]),
        }
    ).fillna(0)

    # Calculate changes and filter economically significant categories
    comparison_df["v3_v1_diff"] = comparison_df["v3"] - comparison_df["v1"]
    significant = comparison_df[
        (comparison_df[["v1", "v2", "v3"]] >= MIN_THRESHOLD).any(axis=1)
    ]

    print(
        f"✓ Occupational analysis: {len(significant)} economically significant categories"
    )
    return significant.sort_values("v1", ascending=False)


def analyze_task_changes(task_data, onet_soc_data, top_n=12):
    """Identify most notable task changes V1→V3."""
    v1, v3 = task_data["v1"], task_data["v3"]

    # Compare changes
    comparison = (
        v1[["task_name", "pct"]]
        .rename(columns={"pct": "v1_pct"})
        .merge(
            v3[["task_name", "pct"]].rename(columns={"pct": "v3_pct"}),
            on="task_name",
            how="outer",
        )
        .fillna(0)
    )

    comparison["change"] = comparison["v3_pct"] - comparison["v1_pct"]
    comparison["rel_change"] = np.where(
        comparison["v1_pct"] > 0,
        (comparison["v3_pct"] - comparison["v1_pct"]) / comparison["v1_pct"] * 100,
        np.inf,
    )

    # Add SOC context
    with_context = comparison.merge(
        onet_soc_data[
            ["task_normalized", "SOC or O*NET-SOC 2019 Title"]
        ].drop_duplicates(),
        left_on="task_name",
        right_on="task_normalized",
        how="left",
    )

    # Get all tasks with economically significant changes (>= 0.2pp)
    significant_changes = with_context[abs(with_context["change"]) >= 0.2].copy()

    # Create category column with formatted relative percentage change
    def format_rel_change(row):
        if row["v1_pct"] > 0:
            rel_change = (row["v3_pct"] - row["v1_pct"]) / row["v1_pct"] * 100
            return f"{rel_change:+.0f}%"
        else:
            return "new"

    significant_changes["category"] = significant_changes.apply(
        format_rel_change, axis=1
    )

    # Rename column and sort by change descending
    significant_changes = significant_changes.rename(
        columns={"SOC or O*NET-SOC 2019 Title": "soc_group"}
    )
    significant_changes = significant_changes.sort_values("change", ascending=False)

    # Round to 3 decimals
    significant_changes[["v1_pct", "v3_pct", "change"]] = significant_changes[
        ["v1_pct", "v3_pct", "change"]
    ].round(3)

    print(f"✓ Task changes: {len(significant_changes)} notable changes identified")
    return significant_changes


def analyze_automation_trends(automation_data):
    """Analyze automation vs augmentation trends across versions."""
    # Standardize interaction names
    for df in automation_data.values():
        df["interaction_type"] = df["interaction_type"].replace(
            {"task iteration": "task_iteration", "feedback loop": "feedback_loop"}
        )

    results = {}
    for version, data in automation_data.items():
        auto_total = data[data["interaction_type"].isin(AUTOMATION_TYPES)]["pct"].sum()
        aug_total = data[data["interaction_type"].isin(AUGMENTATION_TYPES)]["pct"].sum()

        interaction_dict = dict(zip(data["interaction_type"], data["pct"], strict=True))
        results[version] = {
            "automation_total": auto_total,
            "augmentation_total": aug_total,
            "directive": interaction_dict["directive"],
            "feedback_loop": interaction_dict["feedback_loop"],
            "validation": interaction_dict["validation"],
            "task_iteration": interaction_dict["task_iteration"],
            "learning": interaction_dict["learning"],
        }

    print("✓ Automation trends analysis complete")
    return results


# ============================================================================
# VISUALIZATION
# ============================================================================


def setup_plot_style():
    """Configure consistent plot styling."""
    plt.rcParams.update({"font.size": 12, "axes.titlesize": 16, "axes.labelsize": 14})
    sns.set_context("notebook", font_scale=1.1)


def create_usage_trends_figure(comparison_df):
    """Create Usage Share Trends subplot figure."""
    setup_plot_style()

    # Get top categories
    top_cats = comparison_df[
        (comparison_df[["v1", "v2", "v3"]] >= MIN_THRESHOLD).any(axis=1)
    ].head(8)
    top_cats.index = top_cats.index.str.replace(" Occupations", "")

    fig, axes = plt.subplots(2, 4, figsize=(20, 15))
    axes = axes.flatten()

    line_color = "#FF8E53"
    fill_color = "#DEB887"

    # Simplified date labels (actual periods: Dec 2024-Jan 2025, Feb-Mar 2025, Aug 2025)
    versions, version_labels = [1, 2, 3], ["Jan 2025", "Mar 2025", "Aug 2025"]

    for i, (category, data) in enumerate(top_cats.iterrows()):
        if i >= len(axes):
            break
        ax = axes[i]
        values = [data["v1"], data["v2"], data["v3"]]

        ax.plot(
            versions,
            values,
            "o-",
            color=line_color,
            linewidth=3,
            markersize=8,
            markerfacecolor=line_color,
            markeredgecolor="white",
            markeredgewidth=2,
        )
        ax.fill_between(versions, values, alpha=0.3, color=fill_color)

        # Add value labels
        for x, y in zip(versions, values, strict=True):
            ax.text(
                x,
                y + max(values) * 0.02,
                f"{y:.1f}%",
                ha="center",
                va="bottom",
                fontsize=12,
                fontweight="bold",
            )

        ax.set_title(category, fontsize=14, fontweight="bold", pad=10)
        ax.set_xticks(versions)
        ax.set_xticklabels(version_labels)
        ax.set_ylabel("Percentage", fontsize=12)
        ax.set_ylim(0, max(values) * 1.15)
        ax.grid(True, alpha=0.3)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    fig.suptitle(
        "Usage share trends across economic index reports (V1 to V3)",
        fontsize=18,
        fontweight="bold",
        y=0.98,
    )
    plt.tight_layout()
    plt.subplots_adjust(top=0.88)
    return fig


def create_automation_figure(trends):
    """Create Automation vs Augmentation Evolution figure."""
    setup_plot_style()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    # Simplified date labels (actual periods: Dec 2024-Jan 2025, Feb-Mar 2025, Aug 2025)
    version_labels = ["Jan 2025", "Mar 2025", "Aug 2025"]
    x_pos = [1, 2, 3]

    # Left: Overall trends (no fill)
    auto_vals = [trends[v]["automation_total"] for v in ["v1", "v2", "v3"]]
    aug_vals = [trends[v]["augmentation_total"] for v in ["v1", "v2", "v3"]]

    ax1.plot(
        x_pos,
        auto_vals,
        "o-",
        color=COLORS["automation"],
        linewidth=3,
        markersize=8,
        label="Automation",
        markeredgecolor="white",
        markeredgewidth=2,
    )
    ax1.plot(
        x_pos,
        aug_vals,
        "o-",
        color=COLORS["augmentation"],
        linewidth=3,
        markersize=8,
        label="Augmentation",
        markeredgecolor="white",
        markeredgewidth=2,
    )

    # Value labels with automation above and augmentation below dots
    y_max = max(max(auto_vals), max(aug_vals))
    for i, (auto, aug) in enumerate(zip(auto_vals, aug_vals, strict=True)):
        # Red (automation) always above the dot
        ax1.text(
            x_pos[i],
            auto + 1.2,
            f"{auto:.1f}%",
            ha="center",
            va="bottom",
            fontweight="bold",
            color=COLORS["automation"],
        )
        # Blue (augmentation) always below the dot
        ax1.text(
            x_pos[i],
            aug - 1.5,
            f"{aug:.1f}%",
            ha="center",
            va="top",
            fontweight="bold",
            color=COLORS["augmentation"],
        )

    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(version_labels)
    ax1.set_ylabel("Percentage")
    ax1.set_title("Automation vs augmentation trends")
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.spines[["top", "right"]].set_visible(False)
    ax1.set_ylim(0, y_max * 1.15)

    # Right: Individual interaction types with color-coded groups
    interactions = [
        "directive",
        "feedback_loop",
        "validation",
        "task_iteration",
        "learning",
    ]
    # Automation = red shades, Augmentation = cool shades
    colors_individual = ["#DC143C", "#FF6B6B", "#4682B4", "#5F9EA0", "#4169E1"]

    for interaction, color in zip(interactions, colors_individual, strict=True):
        values = [trends[v][interaction] for v in ["v1", "v2", "v3"]]
        ax2.plot(
            x_pos,
            values,
            "o-",
            color=color,
            linewidth=2.5,
            markersize=6,
            label=interaction.replace("_", " ").title(),
            alpha=0.8,
        )

    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(version_labels)
    ax2.set_ylabel("Percentage")
    ax2.set_title("Individual interaction types")
    ax2.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
    ax2.grid(True, alpha=0.3)
    ax2.spines[["top", "right"]].set_visible(False)

    plt.suptitle(
        "Automation vs augmentation evolution (V1 to V3)",
        fontsize=16,
        fontweight="bold",
    )
    plt.tight_layout()
    return fig


# ============================================================================
# MAIN
# ============================================================================


def main():
    """Generate all three economic analysis figures."""
    print("=" * 80)
    print("ECONOMIC ANALYSIS FIGURE GENERATION")
    print("=" * 80)

    # Use consistent output directory for all economic research scripts
    output_dir = "../data/output/figures"
    os.makedirs(output_dir, exist_ok=True)

    # Load all data
    print("\nLoading data...")
    task_data = {
        "v1": load_task_data(FILES["v1_tasks"], "V1"),
        "v2": load_task_data(FILES["v2_tasks"], "V2"),
        "v3": load_task_data(FILES["v3_data"], "V3"),
    }
    automation_data = load_automation_data()
    onet_soc_data = load_occupational_mapping()

    # Analysis
    print("\nAnalyzing trends...")
    occupational_trends = analyze_occupational_trends(task_data, onet_soc_data)
    task_changes = analyze_task_changes(task_data, onet_soc_data)
    automation_trends = analyze_automation_trends(automation_data)

    # Generate figures
    print("\nGenerating figures...")

    fig1 = create_usage_trends_figure(occupational_trends)
    fig1.savefig(
        f"{output_dir}/main_occupational_categories.png",
        dpi=300,
        bbox_inches="tight",
        facecolor="white",
    )
    print("✓ Saved: main_occupational_categories.png")

    fig3 = create_automation_figure(automation_trends)
    fig3.savefig(
        f"{output_dir}/automation_trends_v1_v2_v3.png",
        dpi=300,
        bbox_inches="tight",
        facecolor="white",
    )
    print("✓ Saved: automation_trends_v1_v2_v3.png")

    print(f"\n✅ All figures generated successfully!")
    return occupational_trends, task_changes, automation_trends


if __name__ == "__main__":
    results = main()
