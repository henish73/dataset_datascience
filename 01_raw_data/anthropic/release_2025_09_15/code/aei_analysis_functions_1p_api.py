# AEI 1P API Analysis Functions
# This module contains the core analysis functions for the AEI report API chapter

from pathlib import Path
from textwrap import wrap

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import statsmodels.api as sm
from plotly.subplots import make_subplots

# Define the tier colors
CUSTOM_COLORS_LIST = ["#E6DBD0", "#E5C5AB", "#E4AF86", "#E39961", "#D97757"]

# Define the color cycle for charts
COLOR_CYCLE = [
    "#D97757",
    "#656565",
    "#40668C",
    "#E39961",
    "#E4AF86",
    "#C65A3F",
    "#8778AB",
    "#E5C5AB",
    "#B04F35",
]


def setup_plot_style():
    """Configure matplotlib for publication-quality figures."""
    plt.style.use("default")
    plt.rcParams.update(
        {
            "figure.dpi": 100,
            "savefig.dpi": 300,
            "font.size": 10,
            "axes.labelsize": 11,
            "axes.titlesize": 12,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "legend.fontsize": 9,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "savefig.facecolor": "white",
            "axes.edgecolor": "#333333",
            "axes.linewidth": 0.8,
            "axes.grid": True,
            "grid.alpha": 0.3,
            "grid.linestyle": "-",
            "grid.linewidth": 0.5,
            "axes.axisbelow": True,
            "text.usetex": False,
            "mathtext.default": "regular",
            "axes.titlecolor": "#B86046",
            "figure.titlesize": 16,
        }
    )


# Initialize style
setup_plot_style()


def load_preprocessed_data(input_file):
    """
    Load preprocessed API data from CSV or Parquet file.

    Args:
        input_file: Path to preprocessed data file

    Returns:
        DataFrame with preprocessed API data
    """
    input_path = Path(input_file)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    df = pd.read_csv(input_path)
    return df


def create_top_requests_bar_chart(df, output_dir):
    """
    Create bar chart showing top 15 request categories (level 2) by count share.

    Args:
        df: Preprocessed data DataFrame
        output_dir: Directory to save the figure
    """
    # Get request data at level 2 (global only) using percentages
    request_data = df[
        (df["facet"] == "request")
        & (df["geo_id"] == "GLOBAL")
        & (df["level"] == 2)
        & (df["variable"] == "request_pct")
    ].copy()

    # Filter out not_classified (but don't renormalize)
    request_data = request_data[request_data["cluster_name"] != "not_classified"]

    # Use the percentage values directly (already calculated in preprocessing)
    request_data["request_pct"] = request_data["value"]

    # Get top 15 requests by percentage share
    top_requests = request_data.nlargest(15, "request_pct").sort_values(
        "request_pct", ascending=True
    )

    # Create figure
    fig, ax = plt.subplots(figsize=(14, 10))

    # Create horizontal bar chart with tier color gradient
    y_pos = np.arange(len(top_requests))

    # Use tier colors based on ranking (top categories get darker colors)
    colors = []
    for i in range(len(top_requests)):
        # Map position to tier color (top bars = darker, bottom bars = lighter)
        # Since bars are sorted ascending, higher index = higher value = darker color
        rank_position = i / (len(top_requests) - 1)
        tier_index = int(rank_position * (len(CUSTOM_COLORS_LIST) - 1))
        colors.append(CUSTOM_COLORS_LIST[tier_index])

    ax.barh(
        y_pos,
        top_requests["request_pct"],
        color=colors,
        alpha=0.9,
        edgecolor="#333333",
        linewidth=0.5,
    )

    # Add value labels on bars
    for i, (idx, row) in enumerate(top_requests.iterrows()):
        ax.text(
            row["request_pct"] + 0.1,
            i,
            f"{row['request_pct']:.1f}%",
            va="center",
            fontsize=11,
            fontweight="bold",
        )

    # Clean up request names for y-axis labels
    labels = []
    for name in top_requests["cluster_name"]:
        # Truncate long names and add line breaks
        if len(name) > 60:
            # Find good break point around middle
            mid = len(name) // 2
            break_point = name.find(" ", mid)
            if break_point == -1:  # No space found, just break at middle
                break_point = mid
            clean_name = name[:break_point] + "\n" + name[break_point:].strip()
        else:
            clean_name = name
        labels.append(clean_name)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=10)

    # Formatting
    ax.set_xlabel("Percentage of total request count", fontsize=14)
    ax.set_title(
        "Top use cases among 1P API transcripts by usage share \n (broad grouping, bottom-up classification)",
        fontsize=14,
        fontweight="bold",
        pad=20,
    )

    # Add grid
    ax.grid(True, alpha=0.3, axis="x")
    ax.set_axisbelow(True)

    # Remove top and right spines
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Increase tick label font size
    ax.tick_params(axis="x", which="major", labelsize=12)

    plt.tight_layout()

    # Save plot
    output_path = Path(output_dir) / "top_requests_level2_bar_chart.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.show()
    return str(output_path)


def load_onet_mappings():
    """
    Load ONET task statements and SOC structure for occupational category mapping.

    Returns:
        Tuple of (task_statements_df, soc_structure_df)
    """
    # Load from local files
    task_path = Path("../data/intermediate/onet_task_statements.csv")
    soc_path = Path("../data/intermediate/soc_structure.csv")

    # Load CSV files directly
    task_statements = pd.read_csv(task_path)
    soc_structure = pd.read_csv(soc_path)

    return task_statements, soc_structure


def map_to_occupational_categories(df, task_statements, soc_structure):
    """
    Map ONET task data to major occupational categories.

    Args:
        df: Preprocessed data DataFrame
        task_statements: ONET task statements DataFrame
        soc_structure: SOC structure DataFrame

    Returns:
        DataFrame with occupational category mappings
    """
    # Filter for ONET task data
    onet_data = df[df["facet"] == "onet_task"].copy()

    # Handle not_classified and none tasks first
    not_classified_mask = onet_data["cluster_name"].isin(["not_classified", "none"])
    not_classified_data = onet_data[not_classified_mask].copy()
    not_classified_data["soc_major"] = "99"
    not_classified_data["occupational_category"] = "Not Classified"

    # Process regular tasks
    regular_data = onet_data[~not_classified_mask].copy()

    # Standardize task descriptions for matching
    # Create standardized task mapping from ONET statements
    task_statements["task_standardized"] = (
        task_statements["Task"].str.strip().str.lower()
    )
    regular_data["cluster_name_standardized"] = (
        regular_data["cluster_name"].str.strip().str.lower()
    )

    # Create mapping from standardized task to major groups (allowing multiple)
    task_to_major_groups = {}
    for _, row in task_statements.iterrows():
        if pd.notna(row["Task"]) and pd.notna(row["soc_major_group"]):
            std_task = row["task_standardized"]
            major_group = str(int(row["soc_major_group"]))
            if std_task not in task_to_major_groups:
                task_to_major_groups[std_task] = []
            if major_group not in task_to_major_groups[std_task]:
                task_to_major_groups[std_task].append(major_group)

    # Expand rows for tasks that belong to multiple groups
    expanded_rows = []
    for _, row in regular_data.iterrows():
        std_task = row["cluster_name_standardized"]
        if std_task in task_to_major_groups:
            groups = task_to_major_groups[std_task]
            # Assign full value to each group (creates duplicates)
            for group in groups:
                new_row = row.copy()
                new_row["soc_major"] = group
                new_row["value"] = row["value"]  # Keep full value for each group
                expanded_rows.append(new_row)

    # Create new dataframe from expanded rows
    if expanded_rows:
        regular_data = pd.DataFrame(expanded_rows)
    else:
        regular_data["soc_major"] = None

    # Get major occupational groups from SOC structure
    # Filter for rows where 'Major Group' is not null (these are the major groups)
    major_groups = soc_structure[soc_structure["Major Group"].notna()].copy()

    # Extract major group code and title
    major_groups["soc_major"] = major_groups["Major Group"].astype(str).str[:2]
    major_groups["title"] = major_groups["SOC or O*NET-SOC 2019 Title"]

    # Create a clean mapping from major group code to title
    major_group_mapping = (
        major_groups[["soc_major", "title"]]
        .drop_duplicates()
        .set_index("soc_major")["title"]
        .to_dict()
    )

    # Map major group codes to titles for regular data
    regular_data["occupational_category"] = regular_data["soc_major"].map(
        major_group_mapping
    )

    # Keep only successfully mapped regular data
    regular_mapped = regular_data[regular_data["occupational_category"].notna()].copy()

    # Combine regular mapped data with not_classified data
    onet_mapped = pd.concat([regular_mapped, not_classified_data], ignore_index=True)

    # Renormalize percentages to sum to 100 since we may have created duplicates
    total = onet_mapped["value"].sum()

    onet_mapped["value"] = (onet_mapped["value"] / total) * 100

    return onet_mapped


def create_platform_occupational_comparison(api_df, cai_df, output_dir):
    """
    Create horizontal bar chart comparing occupational categories between Claude.ai and 1P API.

    Args:
        api_df: API preprocessed data DataFrame
        cai_df: Claude.ai preprocessed data DataFrame
        output_dir: Directory to save the figure
    """
    # Load ONET mappings for occupational categories
    task_statements, soc_structure = load_onet_mappings()

    # Process both datasets to get occupational categories
    def get_occupational_data(df, platform_name):
        # Get ONET task percentage data (global level only)
        onet_data = df[
            (df["facet"] == "onet_task")
            & (df["geo_id"] == "GLOBAL")
            & (df["variable"] == "onet_task_pct")
        ].copy()

        # Map to occupational categories using existing function
        onet_mapped = map_to_occupational_categories(
            onet_data, task_statements, soc_structure
        )

        # Sum percentages by occupational category
        category_percentages = (
            onet_mapped.groupby("occupational_category")["value"].sum().reset_index()
        )

        # Exclude "Not Classified" category from visualization
        category_percentages = category_percentages[
            category_percentages["occupational_category"] != "Not Classified"
        ]

        category_percentages.columns = ["category", f"{platform_name.lower()}_pct"]

        return category_percentages

    # Get data for both platforms
    api_categories = get_occupational_data(api_df, "API")
    claude_categories = get_occupational_data(cai_df, "Claude")

    # Merge the datasets
    category_comparison = pd.merge(
        claude_categories, api_categories, on="category", how="outer"
    ).fillna(0)

    # Filter to substantial categories (>0.5% in either platform)
    category_comparison = category_comparison[
        (category_comparison["claude_pct"] > 0.5)
        | (category_comparison["api_pct"] > 0.5)
    ].copy()

    # Calculate difference and total
    category_comparison["difference"] = (
        category_comparison["api_pct"] - category_comparison["claude_pct"]
    )
    category_comparison["total_pct"] = (
        category_comparison["claude_pct"] + category_comparison["api_pct"]
    )

    # Get top 8 categories by total usage
    top_categories = category_comparison.nlargest(8, "total_pct").sort_values(
        "total_pct", ascending=True
    )

    # Create figure
    fig, ax = plt.subplots(figsize=(12, 8))

    y_pos = np.arange(len(top_categories))
    bar_height = 0.35

    # Create side-by-side bars
    ax.barh(
        y_pos - bar_height / 2,
        top_categories["claude_pct"],
        bar_height,
        label="Claude.ai",
        color=COLOR_CYCLE[2],
        alpha=0.8,
    )
    ax.barh(
        y_pos + bar_height / 2,
        top_categories["api_pct"],
        bar_height,
        label="1P API",
        color=COLOR_CYCLE[0],
        alpha=0.8,
    )

    # Add value labels with difference percentages
    for i, (idx, row) in enumerate(top_categories.iterrows()):
        # Claude.ai label
        if row["claude_pct"] > 0.1:
            ax.text(
                row["claude_pct"] + 0.2,
                i - bar_height / 2,
                f"{row['claude_pct']:.0f}%",
                va="center",
                fontsize=9,
            )

        # 1P API label with difference
        if row["api_pct"] > 0.1:
            ax.text(
                row["api_pct"] + 0.2,
                i + bar_height / 2,
                f"{row['api_pct']:.0f}%",
                va="center",
                fontsize=9,
                color=COLOR_CYCLE[0] if row["difference"] > 0 else COLOR_CYCLE[2],
            )

    # Clean up category labels
    labels = []
    for cat in top_categories["category"]:
        # Remove "Occupations" suffix and wrap long names
        clean_cat = cat.replace(" Occupations", "").replace(", and ", " & ")
        wrapped = "\n".join(wrap(clean_cat, 40))
        labels.append(wrapped)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=10)

    ax.set_xlabel("Percentage of usage", fontsize=12)
    ax.set_title(
        "Usage shares across top occupational categories: Claude.ai vs 1P API",
        fontsize=14,
        fontweight="bold",
        pad=20,
    )
    ax.legend(loc="lower right", fontsize=11)
    ax.grid(True, alpha=0.3, axis="x")
    ax.set_axisbelow(True)

    # Remove top and right spines
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()

    # Save plot
    output_path = Path(output_dir) / "platform_occupational_comparison.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.show()
    return str(output_path)


def create_platform_lorenz_curves(api_df, cai_df, output_dir):
    """
    Create Lorenz curves showing task usage concentration by platform.

    Args:
        api_df: API preprocessed data DataFrame
        cai_df: Claude.ai preprocessed data DataFrame
        output_dir: Directory to save the figure
    """

    def gini_coefficient(values):
        """Calculate Gini coefficient for a series of values."""
        sorted_values = np.sort(values)
        n = len(sorted_values)
        cumulative = np.cumsum(sorted_values)
        gini = (2 * np.sum(np.arange(1, n + 1) * sorted_values)) / (
            n * cumulative[-1]
        ) - (n + 1) / n
        return gini

    def get_task_usage_data(df, platform_name):
        # Get ONET task percentage data (global level only)
        onet_data = df[
            (df["facet"] == "onet_task")
            & (df["geo_id"] == "GLOBAL")
            & (df["variable"] == "onet_task_pct")
        ].copy()

        # Filter out none and not_classified
        onet_data = onet_data[
            ~onet_data["cluster_name"].isin(["none", "not_classified"])
        ]

        # Use the percentage values directly
        onet_data["percentage"] = onet_data["value"]

        return onet_data[["cluster_name", "percentage"]].copy()

    api_tasks = get_task_usage_data(api_df, "1P API")
    claude_tasks = get_task_usage_data(cai_df, "Claude.ai")

    # Sort by percentage for each platform
    api_tasks = api_tasks.sort_values("percentage")
    claude_tasks = claude_tasks.sort_values("percentage")

    # Calculate cumulative percentages of usage
    api_cumulative = np.cumsum(api_tasks["percentage"])
    claude_cumulative = np.cumsum(claude_tasks["percentage"])

    # Calculate cumulative percentage of tasks
    api_task_cumulative = np.arange(1, len(api_tasks) + 1) / len(api_tasks) * 100
    claude_task_cumulative = (
        np.arange(1, len(claude_tasks) + 1) / len(claude_tasks) * 100
    )

    # Interpolate to ensure curves reach 100%
    # Add final points to reach (100, 100)
    api_cumulative = np.append(api_cumulative, 100)
    claude_cumulative = np.append(claude_cumulative, 100)
    api_task_cumulative = np.append(api_task_cumulative, 100)
    claude_task_cumulative = np.append(claude_task_cumulative, 100)

    # Calculate Gini coefficients
    api_gini = gini_coefficient(api_tasks["percentage"].values)
    claude_gini = gini_coefficient(claude_tasks["percentage"].values)

    # Create panel figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

    # LEFT PANEL: Lorenz Curves
    # Plot Lorenz curves
    ax1.plot(
        api_task_cumulative,
        api_cumulative,
        color=COLOR_CYCLE[1],
        linewidth=2.5,
        label=f"1P API (Gini = {api_gini:.3f})",
    )

    ax1.plot(
        claude_task_cumulative,
        claude_cumulative,
        color=COLOR_CYCLE[0],
        linewidth=2.5,
        label=f"Claude.ai (Gini = {claude_gini:.3f})",
    )

    # Add perfect equality line (diagonal)
    ax1.plot(
        [0, 100],
        [0, 100],
        "k--",
        linewidth=1.5,
        alpha=0.7,
        label="Perfect Equality",
    )

    # Calculate 80th percentile values
    api_80th_usage = np.interp(80, api_task_cumulative, api_cumulative)
    claude_80th_usage = np.interp(80, claude_task_cumulative, claude_cumulative)

    # Add markers at 80th percentile
    ax1.scatter(
        80,
        api_80th_usage,
        alpha=0.5,
        s=100,
        color=COLOR_CYCLE[1],
        edgecolors="white",
        linewidth=1,
        zorder=5,
    )
    ax1.scatter(
        80,
        claude_80th_usage,
        alpha=0.5,
        s=100,
        color=COLOR_CYCLE[0],
        edgecolors="white",
        linewidth=1,
        zorder=5,
    )

    # Add annotations
    ax1.text(
        82,
        api_80th_usage - 2,
        f"{api_80th_usage:.1f}% of usage",
        ha="left",
        va="center",
        fontsize=10,
        color=COLOR_CYCLE[1],
    )

    ax1.text(
        78.5,
        claude_80th_usage + 1,
        f"{claude_80th_usage:.1f}% of usage",
        ha="right",
        va="center",
        fontsize=10,
        color=COLOR_CYCLE[0],
    )

    # Add text box
    ax1.text(
        0.05,
        0.95,
        f"The bottom 80% of tasks account for:\n• 1P API: {api_80th_usage:.1f}% of usage\n• Claude.ai: {claude_80th_usage:.1f}% of usage",
        transform=ax1.transAxes,
        va="top",
        ha="left",
        bbox=dict(
            boxstyle="round,pad=0.3",
            facecolor="white",
            alpha=0.8,
            edgecolor="black",
            linewidth=1,
        ),
        fontsize=10,
    )

    # Styling for Lorenz curves
    ax1.set_xlabel("Cumulative percentage of tasks", fontsize=12)
    ax1.set_ylabel("Cumulative percentage of usage", fontsize=12)
    ax1.set_title("Lorenz curves", fontsize=14, fontweight="bold", pad=20)
    ax1.set_xlim(0, 100)
    ax1.set_ylim(0, 100)
    ax1.grid(True, alpha=0.3, linestyle="--")
    ax1.set_axisbelow(True)
    ax1.legend(loc=(0.05, 0.65), fontsize=11, frameon=True, facecolor="white")
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)

    # RIGHT PANEL: Zipf's Law Analysis
    min_share = 0.1

    # Filter for minimum share
    api_filtered = api_tasks[api_tasks["percentage"] > min_share]["percentage"].copy()
    claude_filtered = claude_tasks[claude_tasks["percentage"] > min_share][
        "percentage"
    ].copy()

    # Calculate ranks and log transforms
    ln_rank_api = np.log(api_filtered.rank(ascending=False))
    ln_share_api = np.log(api_filtered)

    ln_rank_claude = np.log(claude_filtered.rank(ascending=False))
    ln_share_claude = np.log(claude_filtered)

    # Fit regressions
    api_model = sm.OLS(ln_rank_api, sm.add_constant(ln_share_api)).fit()
    api_slope = api_model.params.iloc[1]
    api_intercept = api_model.params.iloc[0]

    claude_model = sm.OLS(ln_rank_claude, sm.add_constant(ln_share_claude)).fit()
    claude_slope = claude_model.params.iloc[1]
    claude_intercept = claude_model.params.iloc[0]

    # Plot scatter points
    ax2.scatter(
        ln_share_api,
        ln_rank_api,
        alpha=0.5,
        s=100,
        color=COLOR_CYCLE[1],
        label=f"1P API: y = {api_slope:.2f}x + {api_intercept:.2f}",
    )

    ax2.scatter(
        ln_share_claude,
        ln_rank_claude,
        alpha=0.5,
        s=100,
        color=COLOR_CYCLE[0],
        label=f"Claude.ai: y = {claude_slope:.2f}x + {claude_intercept:.2f}",
    )

    # Add Zipf's law reference line (slope = -1)
    x_range = np.linspace(
        min(ln_share_api.min(), ln_share_claude.min()),
        max(ln_share_api.max(), ln_share_claude.max()),
        100,
    )
    avg_intercept = (api_intercept + claude_intercept) / 2
    y_line = -1 * x_range + avg_intercept

    ax2.plot(
        x_range,
        y_line,
        color="black",
        linestyle="--",
        linewidth=2,
        label=f"Zipf's Law: y = -1.00x + {avg_intercept:.2f}",
        zorder=0,
    )

    # Styling for Zipf's law plot
    ax2.set_xlabel("ln(Share of usage)", fontsize=12)
    ax2.set_ylabel("ln(Rank by usage)", fontsize=12)
    ax2.set_title(
        "Task rank versus usage share", fontsize=14, fontweight="bold", pad=20
    )
    ax2.grid(True, alpha=0.3, linestyle="--")
    ax2.set_axisbelow(True)
    ax2.legend(fontsize=11)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)

    # Overall title
    fig.suptitle(
        "Lorenz curves and power law analysis across tasks: 1P API vs Claude.ai",
        fontsize=16,
        fontweight="bold",
        y=0.95,
        color="#B86046",
    )

    plt.tight_layout()
    plt.subplots_adjust(top=0.85)  # More room for suptitle

    # Save plot
    output_path = Path(output_dir) / "platform_lorenz_zipf_panel.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.show()
    return str(output_path)


def create_collaboration_alluvial(api_df, cai_df, output_dir):
    """
    Create alluvial diagram showing collaboration pattern flows between platforms.

    Args:
        api_df: API preprocessed data DataFrame
        cai_df: Claude.ai preprocessed data DataFrame
        output_dir: Directory to save the figure
    """

    def get_collaboration_data(df, platform_name):
        # Get collaboration facet data (global level only)
        collab_data = df[
            (df["facet"] == "collaboration")
            & (df["geo_id"] == "GLOBAL")
            & (df["variable"] == "collaboration_pct")
        ].copy()

        # Use cluster_name directly as the collaboration pattern
        collab_data["pattern"] = collab_data["cluster_name"]

        # Filter out not_classified
        collab_data = collab_data[collab_data["pattern"] != "not_classified"]

        # Use the percentage values directly
        result = collab_data[["pattern", "value"]].copy()
        result.columns = ["pattern", "percentage"]
        result["platform"] = platform_name

        return result

    api_collab = get_collaboration_data(api_df, "1P API")
    claude_collab = get_collaboration_data(cai_df, "Claude.ai")

    # Combine collaboration data
    collab_df = pd.concat([claude_collab, api_collab], ignore_index=True)

    # Define categories
    augmentation_types = ["learning", "task iteration", "validation"]
    automation_types = ["directive", "feedback loop"]

    # Colors matching the original
    pattern_colors = {
        "validation": "#2c3e67",
        "task iteration": "#4f76c7",
        "learning": "#79a7e0",
        "feedback loop": "#614980",
        "directive": "#8e6bb1",
    }

    # Extract flows
    flows_claude = {}
    flows_api = {}

    for pattern in augmentation_types + automation_types:
        claude_mask = (collab_df["pattern"] == pattern) & (
            collab_df["platform"] == "Claude.ai"
        )
        if claude_mask.any():
            flows_claude[pattern] = collab_df.loc[claude_mask, "percentage"].values[0]

        api_mask = (collab_df["pattern"] == pattern) & (
            collab_df["platform"] == "1P API"
        )
        if api_mask.any():
            flows_api[pattern] = collab_df.loc[api_mask, "percentage"].values[0]

    # Create figure with subplots
    fig = make_subplots(
        rows=2,
        cols=1,
        row_heights=[0.5, 0.5],
        vertical_spacing=0.15,
        subplot_titles=("<b>Augmentation Patterns</b>", "<b>Automation Patterns</b>"),
    )

    # Update subplot title colors and font
    for annotation in fig.layout.annotations:
        annotation.update(font=dict(color="#B86046", size=14, family="Styrene B LC"))

    def create_alluvial_traces(patterns, row):
        """Create traces for alluvial diagram"""
        # Sort by size on Claude.ai side
        patterns_sorted = sorted(
            [p for p in patterns if p in flows_claude],
            key=lambda p: flows_claude.get(p, 0),
            reverse=True,
        )

        # Calculate total heights first to determine centering
        total_claude = sum(
            flows_claude.get(p, 0) for p in patterns if p in flows_claude
        )
        total_api = sum(flows_api.get(p, 0) for p in patterns if p in flows_api)
        gap_count = max(
            len([p for p in patterns if p in flows_claude and flows_claude[p] > 0]) - 1,
            0,
        )
        gap_count_api = max(
            len([p for p in patterns if p in flows_api and flows_api[p] > 0]) - 1, 0
        )

        total_height_claude = total_claude + (gap_count * 2)
        total_height_api = total_api + (gap_count_api * 2)

        # Calculate offset to center the smaller side
        offset_claude = 0
        offset_api = 0
        if total_height_claude < total_height_api:
            offset_claude = (total_height_api - total_height_claude) / 2
        else:
            offset_api = (total_height_claude - total_height_api) / 2

        # Calculate positions for Claude.ai (left side)
        y_pos_claude = offset_claude
        claude_positions = {}
        for pattern in patterns_sorted:
            if pattern in flows_claude and flows_claude[pattern] > 0:
                height = flows_claude[pattern]
                claude_positions[pattern] = {
                    "bottom": y_pos_claude,
                    "top": y_pos_claude + height,
                    "center": y_pos_claude + height / 2,
                }
                y_pos_claude += height + 2  # Add gap

        # Calculate positions for 1P API (right side)
        patterns_sorted_api = sorted(
            [p for p in patterns if p in flows_api],
            key=lambda p: flows_api.get(p, 0),
            reverse=True,
        )
        y_pos_api = offset_api
        api_positions = {}
        for pattern in patterns_sorted_api:
            if pattern in flows_api and flows_api[pattern] > 0:
                height = flows_api[pattern]
                api_positions[pattern] = {
                    "bottom": y_pos_api,
                    "top": y_pos_api + height,
                    "center": y_pos_api + height / 2,
                }
                y_pos_api += height + 2  # Add gap

        # Create shapes for flows
        shapes = []
        for pattern in patterns:
            if pattern in claude_positions and pattern in api_positions:
                # Create a quadrilateral connecting the two sides
                x_left = 0.2
                x_right = 0.8

                claude_bottom = claude_positions[pattern]["bottom"]
                claude_top = claude_positions[pattern]["top"]
                api_bottom = api_positions[pattern]["bottom"]
                api_top = api_positions[pattern]["top"]

                # Create path for the flow
                path = f"M {x_left} {claude_bottom} L {x_left} {claude_top} L {x_right} {api_top} L {x_right} {api_bottom} Z"

                hex_color = pattern_colors[pattern]
                r = int(hex_color[1:3], 16)
                g = int(hex_color[3:5], 16)
                b = int(hex_color[5:7], 16)

                shapes.append(
                    dict(
                        type="path",
                        path=path,
                        fillcolor=f"rgba({r},{g},{b},0.5)",
                        line=dict(color=f"rgba({r},{g},{b},1)", width=1),
                    )
                )

        # Create text annotations
        annotations = []

        # Claude.ai labels
        for pattern in patterns_sorted:
            if pattern in claude_positions:
                annotations.append(
                    dict(
                        x=x_left - 0.02,
                        y=claude_positions[pattern]["center"],
                        text=f"{pattern.replace('_', ' ').title()}<br>{flows_claude[pattern]:.1f}%",
                        showarrow=False,
                        xanchor="right",
                        yanchor="middle",
                        font=dict(size=10),
                    )
                )

        # 1P API labels
        for pattern in patterns_sorted_api:
            if pattern in api_positions:
                annotations.append(
                    dict(
                        x=x_right + 0.02,
                        y=api_positions[pattern]["center"],
                        text=f"{pattern.replace('_', ' ').title()}<br>{flows_api[pattern]:.1f}%",
                        showarrow=False,
                        xanchor="left",
                        yanchor="middle",
                        font=dict(size=10),
                    )
                )

        # Platform labels
        annotations.extend(
            [
                dict(
                    x=x_left,
                    y=max(y_pos_claude, y_pos_api) + 5,
                    text="Claude.ai",
                    showarrow=False,
                    xanchor="center",
                    font=dict(size=14, color="black"),
                ),
                dict(
                    x=x_right,
                    y=max(y_pos_claude, y_pos_api) + 5,
                    text="1P API",
                    showarrow=False,
                    xanchor="center",
                    font=dict(size=14, color="black"),
                ),
            ]
        )

        return shapes, annotations, max(y_pos_claude, y_pos_api)

    # Create augmentation diagram
    aug_shapes, aug_annotations, aug_height = create_alluvial_traces(
        augmentation_types, 1
    )

    # Create automation diagram
    auto_shapes, auto_annotations, auto_height = create_alluvial_traces(
        automation_types, 2
    )

    # Add invisible traces to create subplots
    fig.add_trace(
        go.Scatter(x=[0], y=[0], mode="markers", marker=dict(size=0)), row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=[0], y=[0], mode="markers", marker=dict(size=0)), row=2, col=1
    )

    # Update layout with shapes and annotations
    fig.update_layout(
        title=dict(
            text="<b>Collaboration Modes: Claude.ai Conversations vs 1P API Transcripts</b>",
            font=dict(size=16, family="Styrene B LC", color="#B86046"),
            x=0.5,
            xanchor="center",
        ),
        height=800,
        width=1200,
        paper_bgcolor="white",
        plot_bgcolor="white",
        showlegend=False,
    )

    # Ensure white background for both subplots
    fig.update_xaxes(showgrid=False, zeroline=False, showticklabels=False, row=1, col=1)
    fig.update_xaxes(showgrid=False, zeroline=False, showticklabels=False, row=2, col=1)
    fig.update_yaxes(showgrid=False, zeroline=False, showticklabels=False, row=1, col=1)
    fig.update_yaxes(showgrid=False, zeroline=False, showticklabels=False, row=2, col=1)

    # Add shapes and annotations to each subplot
    for shape in aug_shapes:
        fig.add_shape(shape, row=1, col=1)
    for shape in auto_shapes:
        fig.add_shape(shape, row=2, col=1)

    for ann in aug_annotations:
        fig.add_annotation(ann, row=1, col=1)
    for ann in auto_annotations:
        fig.add_annotation(ann, row=2, col=1)

    # Set axis ranges and ensure white background
    fig.update_xaxes(
        range=[0, 1],
        showgrid=False,
        zeroline=False,
        showticklabels=False,
        row=1,
        col=1,
    )
    fig.update_xaxes(
        range=[0, 1],
        showgrid=False,
        zeroline=False,
        showticklabels=False,
        row=2,
        col=1,
    )

    fig.update_yaxes(
        range=[0, aug_height + 10],
        showgrid=False,
        zeroline=False,
        showticklabels=False,
        row=1,
        col=1,
    )
    fig.update_yaxes(
        range=[0, auto_height + 10],
        showgrid=False,
        zeroline=False,
        showticklabels=False,
        row=2,
        col=1,
    )

    # Save plot
    output_path = Path(output_dir) / "collaboration_alluvial.png"
    fig.write_image(str(output_path), width=1200, height=800, scale=2)
    fig.show()
    return str(output_path)


def get_collaboration_shares(df):
    """
    Extract collaboration mode shares for each ONET task from intersection data.

    Args:
        df: Preprocessed data DataFrame

    Returns:
        dict: {task_name: {mode: percentage}}
    """
    # Filter to GLOBAL data only and use pre-calculated percentages
    collab_data = df[
        (df["geo_id"] == "GLOBAL")
        & (df["facet"] == "onet_task::collaboration")
        & (df["variable"] == "onet_task_collaboration_pct")
    ].copy()

    # Split the cluster_name into task and collaboration mode
    collab_data[["task", "mode"]] = collab_data["cluster_name"].str.rsplit(
        "::", n=1, expand=True
    )

    # Filter out 'none' and 'not_classified' modes
    collab_data = collab_data[~collab_data["mode"].isin(["none", "not_classified"])]

    # Use pre-calculated percentages directly
    collaboration_modes = [
        "directive",
        "feedback loop",
        "learning",
        "task iteration",
        "validation",
    ]
    result = {}

    for _, row in collab_data.iterrows():
        task = row["task"]
        mode = row["mode"]

        if mode in collaboration_modes:
            if task not in result:
                result[task] = {}
            result[task][mode] = float(row["value"])

    return result


def create_automation_augmentation_panel(api_df, cai_df, output_dir):
    """
    Create combined panel figure showing automation vs augmentation for both platforms.

    Args:
        api_df: API preprocessed data DataFrame
        cai_df: Claude.ai preprocessed data DataFrame
        output_dir: Directory to save the figure
    """
    # Create figure with subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

    def create_automation_augmentation_subplot(df, ax, title, platform_name):
        """Helper function to create one automation vs augmentation subplot"""
        # Get collaboration shares for each task
        collab_shares = get_collaboration_shares(df)

        # Get task usage counts for bubble sizing
        df_global = df[df["geo_id"] == "GLOBAL"]
        task_counts = (
            df_global[
                (df_global["facet"] == "onet_task")
                & (df_global["variable"] == "onet_task_count")
                & (~df_global["cluster_name"].isin(["none", "not_classified"]))
            ]
            .set_index("cluster_name")["value"]
            .to_dict()
        )

        # Prepare data for plotting
        tasks = []
        automation_scores = []
        augmentation_scores = []
        bubble_sizes = []

        for task_name, shares in collab_shares.items():
            if task_name in task_counts:
                # Calculate automation score (directive + feedback loop)
                automation = shares.get("directive", 0) + shares.get("feedback loop", 0)

                # Calculate augmentation score (learning + task iteration + validation)
                augmentation = (
                    shares.get("learning", 0)
                    + shares.get("task iteration", 0)
                    + shares.get("validation", 0)
                )

                # Only include tasks with some collaboration data
                if automation + augmentation > 0:
                    tasks.append(task_name)
                    automation_scores.append(automation)
                    augmentation_scores.append(augmentation)
                    bubble_sizes.append(task_counts[task_name])

        # Convert to numpy arrays for plotting
        automation_scores = np.array(automation_scores)
        augmentation_scores = np.array(augmentation_scores)
        bubble_sizes = np.array(bubble_sizes)

        # Scale bubble sizes
        bubble_sizes_scaled = (bubble_sizes / bubble_sizes.max()) * 800 + 40

        # Color points based on whether automation or augmentation dominates
        colors = []
        for auto, aug in zip(automation_scores, augmentation_scores, strict=True):
            if auto > aug:
                colors.append("#8e6bb1")  # Automation dominant
            else:
                colors.append("#4f76c7")  # Augmentation dominant

        # Create scatter plot
        ax.scatter(
            automation_scores,
            augmentation_scores,
            s=bubble_sizes_scaled,
            c=colors,
            alpha=0.7,
            edgecolors="black",
            linewidth=0.5,
        )

        # Add diagonal line (automation = augmentation)
        max_val = max(automation_scores.max(), augmentation_scores.max())
        ax.plot([0, max_val], [0, max_val], "--", color="gray", alpha=0.5, linewidth=2)

        # Labels and formatting (increased font sizes)
        ax.set_xlabel("Automation Share (%)", fontsize=14)
        ax.set_ylabel(
            "Augmentation Score (%)",
            fontsize=14,
        )
        ax.set_title(title, fontsize=14, fontweight="bold", pad=15)

        # Calculate percentages for legend
        automation_dominant_count = sum(
            1
            for auto, aug in zip(automation_scores, augmentation_scores, strict=True)
            if auto > aug
        )
        augmentation_dominant_count = len(automation_scores) - automation_dominant_count
        total_tasks = len(automation_scores)

        automation_pct = (automation_dominant_count / total_tasks) * 100
        augmentation_pct = (augmentation_dominant_count / total_tasks) * 100

        # Add legend with percentages centered at top
        automation_patch = plt.scatter(
            [],
            [],
            c="#8e6bb1",
            alpha=0.7,
            s=100,
            label=f"Automation dominant ({automation_pct:.1f}% of Tasks)",
        )
        augmentation_patch = plt.scatter(
            [],
            [],
            c="#4f76c7",
            alpha=0.7,
            s=100,
            label=f"Augmentation dominant ({augmentation_pct:.1f}% of Tasks)",
        )
        ax.legend(
            handles=[automation_patch, augmentation_patch],
            loc="upper center",
            bbox_to_anchor=(0.5, 0.95),
            fontsize=12,
            frameon=True,
            facecolor="white",
        )

        # Grid and styling
        ax.grid(True, alpha=0.3)
        ax.set_axisbelow(True)
        ax.tick_params(axis="both", which="major", labelsize=12)

        return len(tasks), automation_pct, augmentation_pct

    # Create API subplot
    create_automation_augmentation_subplot(api_df, ax1, "1P API", "1P API")

    # Create Claude.ai subplot
    create_automation_augmentation_subplot(cai_df, ax2, "Claude.ai", "Claude.ai")

    # Add overall title
    fig.suptitle(
        "Automation and augmentation dominance across tasks: Claude.ai vs. 1P API",
        fontsize=16,
        fontweight="bold",
        y=0.95,
        color="#B86046",
    )

    plt.tight_layout()
    plt.subplots_adjust(top=0.85)  # More room for suptitle

    # Save plot
    output_path = Path(output_dir) / "automation_vs_augmentation_panel.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.show()
    return str(output_path)


def extract_token_metrics_from_intersections(df):
    """
    Extract token metrics from preprocessed intersection data.

    Args:
        df: Preprocessed dataframe with intersection facets

    Returns:
        DataFrame with token metrics for analysis
    """
    # Extract data using new variable names from mean value intersections
    cost_data = df[
        (df.facet == "onet_task::cost") & (df.variable == "cost_index")
    ].copy()
    cost_data["base_task"] = cost_data["cluster_name"].str.replace("::index", "")
    onet_cost = cost_data.set_index("base_task")["value"].copy()

    prompt_data = df[
        (df.facet == "onet_task::prompt_tokens")
        & (df.variable == "prompt_tokens_index")
    ].copy()
    prompt_data["base_task"] = prompt_data["cluster_name"].str.replace("::index", "")
    onet_prompt = prompt_data.set_index("base_task")["value"].copy()

    completion_data = df[
        (df.facet == "onet_task::completion_tokens")
        & (df.variable == "completion_tokens_index")
    ].copy()
    completion_data["base_task"] = completion_data["cluster_name"].str.replace(
        "::index", ""
    )
    onet_completion = completion_data.set_index("base_task")["value"].copy()

    # Get API call counts for bubble sizing and WLS weights
    api_records_data = df[
        (df.facet == "onet_task::prompt_tokens")
        & (df.variable == "prompt_tokens_count")
    ].copy()
    api_records_data["base_task"] = api_records_data["cluster_name"].str.replace(
        "::count", ""
    )
    onet_api_records = api_records_data.set_index("base_task")["value"].copy()

    # Create metrics DataFrame - values are already re-indexed during preprocessing
    metrics = pd.DataFrame(
        {
            "cluster_name": onet_cost.index,
            "cost_per_record": onet_cost,  # Already indexed (1.0 = average)
            "avg_prompt_tokens": onet_prompt.reindex(
                onet_cost.index
            ),  # Already indexed
            "avg_completion_tokens": onet_completion.reindex(
                onet_cost.index
            ),  # Already indexed
        }
    )

    # Get task usage percentages
    usage_pct_data = df[
        (df.facet == "onet_task") & (df.variable == "onet_task_pct")
    ].copy()
    usage_pct_data["base_task"] = usage_pct_data["cluster_name"]
    onet_usage_pct = usage_pct_data.set_index("base_task")["value"].copy()

    # Add API records and usage percentages
    metrics["api_records"] = onet_api_records.reindex(onet_cost.index)
    metrics["usage_pct"] = onet_usage_pct.reindex(onet_cost.index)

    # Calculate derived metrics
    metrics["output_input_ratio"] = (
        metrics["avg_completion_tokens"] / metrics["avg_prompt_tokens"]
    )
    metrics["total_tokens"] = (
        metrics["avg_prompt_tokens"] + metrics["avg_completion_tokens"]
    )

    return metrics


def add_occupational_categories_to_metrics(
    task_metrics, task_statements, soc_structure
):
    """
    Add occupational categories to task metrics based on ONET mappings.

    Args:
        task_metrics: DataFrame with task metrics
        task_statements: ONET task statements DataFrame
        soc_structure: SOC structure DataFrame

    Returns:
        DataFrame with occupational categories added
    """
    # Standardize task descriptions for matching
    task_statements["task_standardized"] = (
        task_statements["Task"].str.strip().str.lower()
    )
    task_metrics["cluster_name_standardized"] = (
        task_metrics["cluster_name"].str.strip().str.lower()
    )

    # Create mapping from standardized task to major group
    task_to_major_group = {}
    for _, row in task_statements.iterrows():
        if pd.notna(row["Task"]) and pd.notna(row["soc_major_group"]):
            std_task = row["task_standardized"]
            major_group = str(int(row["soc_major_group"]))
            task_to_major_group[std_task] = major_group

    # Map cluster names to major groups
    task_metrics["soc_major"] = task_metrics["cluster_name_standardized"].map(
        task_to_major_group
    )

    # Get major occupational groups from SOC structure
    major_groups = soc_structure[soc_structure["Major Group"].notna()].copy()
    major_groups["soc_major"] = major_groups["Major Group"].astype(str).str[:2]
    major_groups["title"] = major_groups["SOC or O*NET-SOC 2019 Title"]

    # Create a clean mapping from major group code to title
    major_group_mapping = (
        major_groups[["soc_major", "title"]]
        .drop_duplicates()
        .set_index("soc_major")["title"]
        .to_dict()
    )

    # Map major group codes to titles
    task_metrics["occupational_category"] = task_metrics["soc_major"].map(
        major_group_mapping
    )

    # Remove unmapped/not classified tasks from analysis
    task_metrics = task_metrics[task_metrics["occupational_category"].notna()].copy()

    # Find top 6 categories by usage share (API calls) and group others as "All Other"
    category_usage = (
        task_metrics.groupby("occupational_category")["api_records"]
        .sum()
        .sort_values(ascending=False)
    )
    top_6_categories = list(category_usage.head(6).index)

    # Group smaller categories as "All Other"
    task_metrics["occupational_category"] = task_metrics["occupational_category"].apply(
        lambda x: x if x in top_6_categories else "All Other"
    )

    return task_metrics


def create_token_output_bar_chart(df, output_dir):
    """
    Create bar chart showing average output (completion) tokens by occupational category.

    Args:
        df: Preprocessed data DataFrame
        output_dir: Directory to save the figure
    """
    # Load ONET mappings for occupational categories
    task_statements, soc_structure = load_onet_mappings()

    # Use preprocessed intersection data
    task_metrics = extract_token_metrics_from_intersections(df)

    # Add occupational categories
    task_metrics = add_occupational_categories_to_metrics(
        task_metrics, task_statements, soc_structure
    )

    # Calculate average output tokens by occupational category
    category_stats = (
        task_metrics.groupby("occupational_category")
        .agg(
            {
                "avg_completion_tokens": "mean",  # Average across tasks
                "api_records": "sum",  # Total API calls for ranking
            }
        )
        .reset_index()
    )

    # Find top 6 categories by total API calls
    top_6_categories = category_stats.nlargest(6, "api_records")[
        "occupational_category"
    ].tolist()

    # Group smaller categories as "All Other"
    def categorize(cat):
        return cat if cat in top_6_categories else "All Other"

    task_metrics["category_group"] = task_metrics["occupational_category"].apply(
        categorize
    )

    # Recalculate stats with grouped categories
    final_stats = (
        task_metrics.groupby("category_group")
        .agg(
            {
                "avg_completion_tokens": "mean",  # Average output tokens across tasks
                "api_records": "sum",  # Total usage for reference
            }
        )
        .reset_index()
    )

    # Sort by output tokens (descending)
    final_stats = final_stats.sort_values("avg_completion_tokens", ascending=True)

    # Create figure
    fig, ax = plt.subplots(figsize=(12, 8))

    # Create horizontal bar chart
    y_pos = np.arange(len(final_stats))
    colors = [COLOR_CYCLE[i % len(COLOR_CYCLE)] for i in range(len(final_stats))]

    ax.barh(
        y_pos,
        final_stats["avg_completion_tokens"],
        color=colors,
        alpha=0.8,
        edgecolor="#333333",
        linewidth=0.5,
    )

    # Add value labels
    for i, (idx, row) in enumerate(final_stats.iterrows()):
        ax.text(
            row["avg_completion_tokens"] + 0.02,
            i,
            f"{row['avg_completion_tokens']:.2f}",
            va="center",
            fontsize=11,
            fontweight="bold",
        )

    # Clean up category labels
    labels = []
    for cat in final_stats["category_group"]:
        clean_cat = cat.replace(" Occupations", "").replace(", and ", " & ")
        labels.append(clean_cat)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=10)

    # Formatting
    ax.set_xlabel(
        "Average output token index for observed tasks in a given category",
        fontsize=12,
    )
    ax.set_title(
        "Average output token index across leading occupational categories",
        fontsize=14,
        fontweight="bold",
        pad=20,
    )

    # Grid and styling
    ax.grid(True, alpha=0.3, axis="x")
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(axis="x", which="major", labelsize=11)

    plt.tight_layout()

    # Save plot
    output_path = Path(output_dir) / "token_output_bar_chart.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.show()
    return str(output_path)


def create_completion_vs_input_tokens_scatter(df, output_dir):
    """
    Create scatter plot of ln(completion tokens) vs ln(input tokens) by occupational category.

    Args:
        df: Preprocessed data DataFrame
        output_dir: Directory to save the figure
    """
    # Use preprocessed intersection data
    task_metrics = extract_token_metrics_from_intersections(df)

    # Create figure
    fig, ax = plt.subplots(figsize=(12, 8))

    # Transform to natural log
    ln_input = np.log(task_metrics["avg_prompt_tokens"])
    ln_output = np.log(task_metrics["avg_completion_tokens"])

    # Load ONET mappings for occupational categories
    task_statements, soc_structure = load_onet_mappings()

    # Add occupational categories
    # Standardize task descriptions for matching
    task_statements["task_standardized"] = (
        task_statements["Task"].str.strip().str.lower()
    )
    task_metrics["cluster_name_standardized"] = (
        task_metrics.index.str.strip().str.lower()
    )

    # Create mapping from standardized task to major group
    task_to_major_group = {}
    for _, row in task_statements.iterrows():
        if pd.notna(row["Task"]) and pd.notna(row["soc_major_group"]):
            std_task = row["task_standardized"]
            major_group = str(int(row["soc_major_group"]))[:2]
            task_to_major_group[std_task] = major_group

    # Map cluster names to major groups
    task_metrics["soc_major"] = task_metrics["cluster_name_standardized"].map(
        task_to_major_group
    )

    # Get major occupational groups from SOC structure
    major_groups = soc_structure[soc_structure["Major Group"].notna()].copy()
    major_groups["soc_major"] = major_groups["Major Group"].astype(str).str[:2]
    major_groups["title"] = major_groups["SOC or O*NET-SOC 2019 Title"]

    # Create mapping from major group code to title
    major_group_mapping = (
        major_groups[["soc_major", "title"]]
        .drop_duplicates()
        .set_index("soc_major")["title"]
        .to_dict()
    )

    # Map major group codes to titles
    task_metrics["occupational_category"] = task_metrics["soc_major"].map(
        major_group_mapping
    )

    # Remove unmapped tasks
    task_metrics = task_metrics[task_metrics["occupational_category"].notna()].copy()

    # Find top 6 categories by total API calls and group others as "All Other"
    category_usage = (
        task_metrics.groupby("occupational_category")["api_records"]
        .sum()
        .sort_values(ascending=False)
    )
    top_6_categories = list(category_usage.head(6).index)

    # Group smaller categories as "All Other"
    task_metrics["occupational_category"] = task_metrics["occupational_category"].apply(
        lambda x: x if x in top_6_categories else "All Other"
    )

    # Transform to natural log
    ln_input = np.log(task_metrics["avg_prompt_tokens"])
    ln_output = np.log(task_metrics["avg_completion_tokens"])

    # Create scatter plot with same color scheme as bar chart
    # Use exact same logic as token output bar chart for consistent colors
    category_stats = (
        task_metrics.groupby("occupational_category")
        .agg(
            {
                "avg_completion_tokens": "mean",
                "api_records": "sum",
            }
        )
        .reset_index()
    )

    # Find top 6 categories by total API calls
    top_6_categories = category_stats.nlargest(6, "api_records")[
        "occupational_category"
    ].tolist()

    # Group smaller categories as "All Other"
    def categorize(cat):
        return cat if cat in top_6_categories else "All Other"

    task_metrics["category_group"] = task_metrics["occupational_category"].apply(
        categorize
    )

    # Recalculate final stats with grouped categories
    final_stats = (
        task_metrics.groupby("category_group")
        .agg({"avg_completion_tokens": "mean"})
        .reset_index()
        .sort_values("avg_completion_tokens", ascending=True)
    )

    # Use exact same color assignment as bar chart
    categories_ordered = final_stats["category_group"].tolist()
    category_colors = {}
    for i, category in enumerate(categories_ordered):
        category_colors[category] = COLOR_CYCLE[i % len(COLOR_CYCLE)]

    for category in categories_ordered:
        category_data = task_metrics[task_metrics["category_group"] == category]
        if not category_data.empty:
            ln_input_cat = np.log(category_data["avg_prompt_tokens"])
            ln_output_cat = np.log(category_data["avg_completion_tokens"])
            bubble_sizes_cat = np.sqrt(category_data["api_records"]) * 2

            # Clean up category name for legend
            clean_name = category.replace(" Occupations", "").replace(", and ", " & ")

            ax.scatter(
                ln_input_cat,
                ln_output_cat,
                s=bubble_sizes_cat,
                alpha=0.8,
                c=category_colors[category],
                edgecolors="black",
                linewidth=0.2,
            )

    # Create uniform legend entries
    legend_elements = []
    for category in categories_ordered:
        clean_name = category.replace(" Occupations", "").replace(", and ", " & ")
        # Get count for this category
        category_count = len(task_metrics[task_metrics["category_group"] == category])
        legend_elements.append(
            plt.scatter(
                [],
                [],
                s=100,
                alpha=0.8,
                c=category_colors[category],
                edgecolors="black",
                linewidth=0.2,
                label=f"{clean_name} (N={category_count})",
            )
        )

    # Add legend for occupational categories with uniform sizes
    ax.legend(
        bbox_to_anchor=(1.05, 1), loc="upper left", frameon=True, facecolor="white"
    )

    # Add line of best fit
    model = sm.OLS(ln_output, sm.add_constant(ln_input)).fit()
    slope = model.params.iloc[1]
    intercept = model.params.iloc[0]
    r_squared = model.rsquared

    line_x = np.linspace(ln_input.min(), ln_input.max(), 100)
    line_y = slope * line_x + intercept
    ax.plot(
        line_x,
        line_y,
        "k--",
        alpha=0.7,
        linewidth=2,
        label=f"Best fit (R² = {r_squared:.3f}, $\\beta$ = {slope:.3f})",
    )
    ax.legend()

    # Customize plot
    ax.set_xlabel("ln(Input Token Index)", fontsize=12)
    ax.set_ylabel("ln(Output Token Index)", fontsize=12)
    ax.set_title(
        "Output Token Index vs Input Token Index across tasks",
        fontsize=14,
        fontweight="bold",
        pad=20,
    )
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    # Save plot
    output_path = Path(output_dir) / "completion_vs_input_tokens_scatter.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.show()
    return str(output_path)


def create_occupational_usage_cost_scatter(df, output_dir):
    """
    Create aggregated scatter plot of usage share vs average cost per API call by occupational category.

    Args:
        df: Preprocessed data DataFrame
        output_dir: Directory to save the figure
    """
    # Load ONET mappings for occupational categories
    task_statements, soc_structure = load_onet_mappings()

    # Use preprocessed intersection data
    task_metrics = extract_token_metrics_from_intersections(df)

    # Add occupational categories without grouping into "All Other"
    # Standardize task descriptions for matching
    task_statements["task_standardized"] = (
        task_statements["Task"].str.strip().str.lower()
    )
    task_metrics["cluster_name_standardized"] = (
        task_metrics["cluster_name"].str.strip().str.lower()
    )

    # Create mapping from standardized task to major group
    task_to_major_group = {}
    for _, row in task_statements.iterrows():
        if pd.notna(row["Task"]) and pd.notna(row["soc_major_group"]):
            std_task = row["task_standardized"]
            major_group = str(int(row["soc_major_group"]))
            task_to_major_group[std_task] = major_group

    # Map cluster names to major groups
    task_metrics["soc_major"] = task_metrics["cluster_name_standardized"].map(
        task_to_major_group
    )

    # Get major occupational groups from SOC structure
    major_groups = soc_structure[soc_structure["Major Group"].notna()].copy()
    major_groups["soc_major"] = major_groups["Major Group"].astype(str).str[:2]
    major_groups["title"] = major_groups["SOC or O*NET-SOC 2019 Title"]

    # Create a clean mapping from major group code to title
    major_group_mapping = (
        major_groups[["soc_major", "title"]]
        .drop_duplicates()
        .set_index("soc_major")["title"]
        .to_dict()
    )

    # Map major group codes to titles
    task_metrics["occupational_category"] = task_metrics["soc_major"].map(
        major_group_mapping
    )

    # Remove unmapped/not classified tasks from analysis
    task_metrics = task_metrics[task_metrics["occupational_category"].notna()].copy()

    # Aggregate by occupational category using pre-calculated percentages
    category_aggregates = (
        task_metrics.groupby("occupational_category")
        .agg(
            {
                "usage_pct": "sum",  # Sum of pre-calculated task percentages within category
                "cost_per_record": "mean",  # Average cost per API call for this category
            }
        )
        .reset_index()
    )

    # Usage share is already calculated from preprocessing
    category_aggregates["usage_share"] = category_aggregates["usage_pct"]

    # Create figure
    fig, ax = plt.subplots(figsize=(12, 8))

    # Transform variables to natural log
    ln_cost = np.log(category_aggregates["cost_per_record"])
    ln_usage = np.log(category_aggregates["usage_share"])

    # Get colors for each category - use same logic as token output bar chart
    # Sort by a metric to ensure consistent ordering (using usage_share descending)
    category_aggregates_sorted = category_aggregates.sort_values(
        "usage_share", ascending=False
    )

    category_colors = {}
    for i, category in enumerate(category_aggregates_sorted["occupational_category"]):
        category_colors[category] = COLOR_CYCLE[i % len(COLOR_CYCLE)]

    # Create invisible scatter plot to maintain axis limits
    ax.scatter(
        ln_cost,
        ln_usage,
        s=0,  # Invisible markers
        alpha=0,
    )

    # Add line of best fit
    model = sm.OLS(ln_usage, sm.add_constant(ln_cost)).fit()
    slope = model.params.iloc[1]
    intercept = model.params.iloc[0]
    r_squared = model.rsquared

    # Generate line points
    x_line = np.linspace(ln_cost.min(), ln_cost.max(), 50)
    y_line = slope * x_line + intercept

    # Plot the line of best fit
    ax.plot(
        x_line,
        y_line,
        "--",
        color="black",
        linewidth=2,
        alpha=0.8,
        label=f"Best fit (R² = {r_squared:.3f}, $\\beta$ = {slope:.3f})",
    )

    # Add legend
    legend = ax.legend(loc="best", frameon=True, facecolor="white")
    legend.get_frame().set_alpha(0.9)

    # Add category labels centered at data points with text wrapping
    for i, row in category_aggregates.iterrows():
        # Clean up and wrap category names
        clean_name = (
            row["occupational_category"]
            .replace(" Occupations", "")
            .replace(", and ", " & ")
        )
        # Wrap long category names to multiple lines
        wrapped_name = "\n".join(wrap(clean_name, 20))

        ax.text(
            ln_cost.iloc[i],
            ln_usage.iloc[i],
            wrapped_name,
            ha="center",
            va="center",
            fontsize=8,
            alpha=0.9,
        )

    # Set labels and title
    ax.set_xlabel("ln(Average API Cost Index across tasks)", fontsize=12)
    ax.set_ylabel("ln(Usage share (%))", fontsize=12)
    ax.set_title(
        "Usage share and average API cost index by occupational category",
        fontsize=14,
        fontweight="bold",
        pad=20,
    )

    # Add grid
    ax.grid(True, alpha=0.3)

    # Adjust layout and save
    plt.tight_layout()

    output_path = Path(output_dir) / "occupational_usage_cost_scatter.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.show()
    return str(output_path)


def get_merged_api_claude_task_data(api_df, cai_df):
    """
    Create merged dataset with API cost/usage data and Claude.ai collaboration modes.

    Args:
        api_df: API preprocessed data DataFrame
        cai_df: Claude.ai preprocessed data DataFrame

    Returns:
        DataFrame with API cost data + Claude.ai collaboration patterns for common tasks
    """
    # Extract API token metrics
    api_metrics = extract_token_metrics_from_intersections(api_df)

    # Get Claude.ai collaboration shares
    claude_collab_shares = get_collaboration_shares(cai_df)

    # Find common tasks between both platforms
    api_tasks = set(api_metrics.index)
    claude_tasks = set(claude_collab_shares.keys())
    common_tasks = api_tasks.intersection(claude_tasks)

    # Create merged dataset
    merged_data = []

    for task_name in common_tasks:
        # Get API metrics for this task
        api_row = api_metrics.loc[task_name]

        # Get Claude.ai collaboration for this task
        claude_collab = claude_collab_shares[task_name]

        # Create merged row
        merged_row = {
            "cluster_name": task_name,
            "cost_per_record": api_row["cost_per_record"],
            "avg_prompt_tokens": api_row["avg_prompt_tokens"],
            "avg_completion_tokens": api_row["avg_completion_tokens"],
            "api_records": api_row["api_records"],
            "output_input_ratio": api_row["output_input_ratio"],
            "total_tokens": api_row["total_tokens"],
            # Claude.ai collaboration modes
            "collab_directive": claude_collab.get("directive", 0),
            "collab_feedback_loop": claude_collab.get("feedback loop", 0),
            "collab_learning": claude_collab.get("learning", 0),
            "collab_task_iteration": claude_collab.get("task iteration", 0),
            "collab_validation": claude_collab.get("validation", 0),
        }
        merged_data.append(merged_row)

    merged_df = pd.DataFrame(merged_data)
    merged_df.set_index("cluster_name", inplace=True)

    return merged_df


def reg_build_df(api_df, cai_df):
    """
    Build complete regression dataset for partial regression and full regression analysis.
    Each row is an ONET task with all variables needed for figures and regression.

    Args:
        api_df: API preprocessed data DataFrame
        cai_df: Claude.ai preprocessed data DataFrame

    Returns:
        DataFrame with complete regression dataset
    """
    # Load ONET mappings
    task_statements, soc_structure = load_onet_mappings()

    # Use merged dataset with API metrics + Claude.ai collaboration
    task_metrics = get_merged_api_claude_task_data(api_df, cai_df)

    # Add occupational categories (includes "All Other" grouping)
    task_metrics_with_names = task_metrics.reset_index()
    task_metrics_with_names = add_occupational_categories_to_metrics(
        task_metrics_with_names, task_statements, soc_structure
    )
    task_metrics = task_metrics_with_names.set_index("cluster_name")

    # Add collaboration missing dummies
    collaboration_modes = [
        "directive",
        "feedback_loop",
        "learning",
        "task_iteration",
        "validation",
    ]

    for mode in collaboration_modes:
        collab_col = f"collab_{mode}"
        missing_col = f"collab_{mode}_missing"
        if collab_col in task_metrics.columns:
            task_metrics[missing_col] = (task_metrics[collab_col] == 0).astype(int)
        else:
            task_metrics[missing_col] = 1

    # Calculate usage variables
    total_api_records = task_metrics["api_records"].sum()
    task_metrics["usage_share"] = (
        task_metrics["api_records"] / total_api_records
    ) * 100
    task_metrics["ln_usage_share"] = np.log(task_metrics["usage_share"])
    task_metrics["ln_cost_per_task"] = np.log(task_metrics["cost_per_record"])

    # Use all data
    valid_data = task_metrics

    # Create occupational category dummies while preserving original column
    valid_data = pd.get_dummies(
        valid_data, columns=["occupational_category"], prefix="occ"
    )

    # Restore the original occupational_category column for grouping operations
    # Extract category name from the dummy columns that are 1
    occ_cols = [col for col in valid_data.columns if col.startswith("occ_")]
    valid_data["occupational_category"] = ""
    for col in occ_cols:
        category_name = col.replace("occ_", "")
        mask = valid_data[col] == 1
        valid_data.loc[mask, "occupational_category"] = category_name

    return valid_data


def create_partial_regression_plot(api_df, cai_df, output_dir):
    """
    Create partial regression scatter plot of usage share vs cost, controlling for occupational categories.

    Args:
        api_df: API preprocessed data DataFrame
        cai_df: Claude.ai preprocessed data DataFrame
        output_dir: Directory to save the figure

    Returns:
        Tuple of (output_path, regression_results_dict)
    """
    # Use centralized data preparation (includes occupational dummies)
    valid_metrics = reg_build_df(api_df, cai_df)

    # Extract occupational dummies and collaboration variables
    occ_cols = [col for col in valid_metrics.columns if col.startswith("occ_")]
    collab_vars = [
        "collab_directive",
        "collab_feedback_loop",
        "collab_learning",
        "collab_task_iteration",
        "collab_validation",
    ]
    collab_missing_vars = [
        "collab_directive_missing",
        "collab_feedback_loop_missing",
        "collab_learning_missing",
        "collab_task_iteration_missing",
        "collab_validation_missing",
    ]

    # Control variables (all occupational dummies + collaboration modes)
    control_vars = valid_metrics[occ_cols + collab_vars + collab_missing_vars].astype(
        float
    )

    # Ensure dependent variables are float
    y_usage = valid_metrics["ln_usage_share"].astype(float)
    y_cost = valid_metrics["ln_cost_per_task"].astype(float)

    # Step 1: Regress ln(usage_share) on controls (no constant)
    usage_model = sm.OLS(y_usage, control_vars).fit()
    usage_residuals = usage_model.resid

    # Step 2: Regress ln(cost) on controls (no constant)
    cost_model = sm.OLS(y_cost, control_vars).fit()
    cost_residuals = cost_model.resid

    # Find top 6 categories by usage share for coloring
    category_usage = (
        valid_metrics.groupby("occupational_category")["api_records"]
        .sum()
        .sort_values(ascending=False)
    )
    top_6_categories = list(category_usage.head(6).index)

    # Create category grouping for coloring
    valid_metrics["category_group"] = valid_metrics["occupational_category"].apply(
        lambda x: x if x in top_6_categories else "All Other"
    )

    # Create figure
    fig, ax = plt.subplots(figsize=(14, 10))

    # Create color mapping for top 6 + "All Other"
    unique_groups = valid_metrics["category_group"].unique()
    group_colors = {}
    color_idx = 0

    # Assign colors to top 6 categories first
    for cat in top_6_categories:
        if cat in unique_groups:
            group_colors[cat] = COLOR_CYCLE[color_idx % len(COLOR_CYCLE)]
            color_idx += 1

    # Assign color to "All Other"
    if "All Other" in unique_groups:
        group_colors["All Other"] = "#999999"  # Gray for all other

    # Create single scatter plot (no color by group)
    ax.scatter(
        cost_residuals,
        usage_residuals,
        s=100,
        alpha=0.8,
        color=COLOR_CYCLE[0],
        edgecolors="black",
        linewidth=0.2,
    )

    # Add overall trend line for residuals
    model = sm.OLS(usage_residuals, sm.add_constant(cost_residuals)).fit()
    slope = model.params.iloc[1]
    intercept = model.params.iloc[0]
    r_squared = model.rsquared

    line_x = np.linspace(cost_residuals.min(), cost_residuals.max(), 100)
    line_y = slope * line_x + intercept
    ax.plot(
        line_x,
        line_y,
        "k--",
        alpha=0.8,
        linewidth=2,
        label=f"Partial relationship (R² = {r_squared:.3f})",
    )

    # Customize plot
    ax.set_xlabel("Residual ln(API Cost Index)")
    ax.set_ylabel("Residual ln(Usage share (%))")
    ax.set_title(
        "Task usage share vs API Cost Index \n(partial regression after controlling for task characteristics)",
        fontsize=16,
        fontweight="bold",
        pad=20,
    )
    ax.grid(True, alpha=0.3)

    # Simple legend with just the trend line
    ax.legend(loc="best", frameon=True, facecolor="white", framealpha=0.9, fontsize=11)

    plt.tight_layout()

    # Save plot
    output_path = Path(output_dir) / "partial_regression_plot.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.show()

    # Save regression results
    regression_results = {
        "partial_correlation": np.sqrt(r_squared),
        "partial_r_squared": r_squared,
        "slope": slope,
        "intercept": intercept,
        "n_observations": len(valid_metrics),
        "usage_model_summary": str(usage_model.summary()),
        "cost_model_summary": str(cost_model.summary()),
    }

    # Print regression results instead of saving to file
    print("Partial Regression Analysis Results")
    print("=" * 50)
    print(f"Partial correlation: {np.sqrt(r_squared):.4f}")
    print(f"Partial R-squared: {r_squared:.4f}")
    print(f"Slope: {slope:.4f}")
    print(f"Intercept: {intercept:.4f}")
    print(f"Number of observations: {len(valid_metrics)}")
    print("\nUsage Model Summary:")
    print("-" * 30)
    print(usage_model.summary())
    print("\nCost Model Summary:")
    print("-" * 30)
    print(cost_model.summary())

    return str(output_path), regression_results


def perform_usage_share_regression_unweighted(api_df, cai_df, output_dir):
    """
    Perform unweighted usage share regression analysis using Claude.ai collaboration modes.

    Args:
        api_df: API preprocessed data DataFrame
        cai_df: Claude.ai preprocessed data DataFrame
        output_dir: Directory to save regression results

    Returns:
        OLS model results
    """
    # Use centralized data preparation (includes all dummies)
    valid_data = reg_build_df(api_df, cai_df)

    # Extract all regression variables
    X_cols = ["ln_cost_per_task"]
    X_cols.extend(
        [
            f"collab_{mode}"
            for mode in [
                "directive",
                "feedback_loop",
                "learning",
                "task_iteration",
                "validation",
            ]
        ]
    )
    X_cols.extend(
        [
            f"collab_{mode}_missing"
            for mode in [
                "directive",
                "feedback_loop",
                "learning",
                "task_iteration",
                "validation",
            ]
        ]
    )
    X_cols.extend([col for col in valid_data.columns if col.startswith("occ_")])

    # Ensure all columns are numeric
    X = valid_data[X_cols].astype(float)
    y = valid_data["ln_usage_share"].astype(float)

    # Run unweighted OLS without constant (to include all occupational dummies)
    model = sm.OLS(y, X).fit()

    # Get heteroskedasticity-robust standard errors (HC1)
    model_robust = model.get_robustcov_results(cov_type="HC1")

    return model_robust


def create_btos_ai_adoption_chart(btos_df, ref_dates_df, output_dir):
    """
    Create BTOS AI adoption time series chart.

    Args:
        btos_df: BTOS response estimates DataFrame
        ref_dates_df: Collection and reference dates DataFrame
        output_dir: Directory to save the figure
    """
    # Filter for Question ID 7, Answer ID 1 (Yes response to AI usage)
    btos_filtered = btos_df[(btos_df["Question ID"] == 7) & (btos_df["Answer ID"] == 1)]

    # Get date columns (string columns that look like YYYYWW)
    date_columns = [
        col for col in btos_df.columns[4:] if str(col).isdigit() and len(str(col)) == 6
    ]

    # Extract time series
    btos_ts = btos_filtered[date_columns].T
    btos_ts.columns = ["percentage"]

    # Map to reference end dates
    ref_dates_df["Ref End"] = pd.to_datetime(ref_dates_df["Ref End"])
    btos_ts = btos_ts.reset_index()
    btos_ts["smpdt"] = btos_ts["index"].astype(int)
    btos_ts = btos_ts.merge(
        ref_dates_df[["Smpdt", "Ref End"]],
        left_on="smpdt",
        right_on="Smpdt",
        how="left",
    )
    btos_ts = btos_ts.set_index("Ref End")[["percentage"]]

    # Convert percentage strings to numeric
    btos_ts["percentage"] = btos_ts["percentage"].str.rstrip("%").astype(float)
    btos_ts = btos_ts.sort_index().dropna()

    # Calculate 3-period moving average
    btos_ts["moving_avg"] = btos_ts["percentage"].rolling(window=3).mean()

    # Create figure
    fig, ax = plt.subplots(figsize=(14, 8))

    # Plot main line
    ax.plot(
        btos_ts.index,
        btos_ts["percentage"],
        linewidth=3,
        marker="o",
        markersize=6,
        label="AI Adoption Rate Among US Businesses",
        zorder=3,
    )

    # Plot moving average
    ax.plot(
        btos_ts.index,
        btos_ts["moving_avg"],
        linewidth=2,
        linestyle="--",
        alpha=0.8,
        label="3-Period Moving Average",
        zorder=2,
    )

    # Styling
    ax.set_xlabel("Date", fontsize=14)
    ax.set_ylabel("AI adoption rate (%)", fontsize=14)
    ax.set_title(
        "Census reported AI adoption rates among US businesses from the Business Trends and Outlook Survey",
        fontsize=16,
        fontweight="bold",
        pad=20,
    )

    # Format y-axis as percentage
    ax.set_ylim(0, max(btos_ts["percentage"]) * 1.1)

    # Rotate x-axis labels
    ax.tick_params(axis="x", rotation=45)

    # Grid and styling
    ax.grid(True, alpha=0.3, linestyle="--")
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Legend
    ax.legend(loc="upper left", fontsize=11, frameon=True, facecolor="white")

    plt.tight_layout()

    # Save plot
    output_path = Path(output_dir) / "btos_ai_adoption_chart.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.show()
    return str(output_path)
