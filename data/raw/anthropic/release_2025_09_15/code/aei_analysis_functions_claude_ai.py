#!/usr/bin/env python3
"""
Analysis functions for AEI Report v3 Claude.ai chapter
"""

import textwrap

import geopandas as gpd
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
from matplotlib.colors import LinearSegmentedColormap, Normalize, TwoSlopeNorm
from matplotlib.lines import Line2D
from matplotlib.patches import FancyBboxPatch, Patch
from mpl_toolkits.axes_grid1 import make_axes_locatable

# global list of excluded countries (ISO-3 codes)
EXCLUDED_COUNTRIES = [
    "AFG",
    "BLR",
    "COD",
    "CAF",
    "CHN",
    "CUB",
    "ERI",
    "ETH",
    "HKG",
    "IRN",
    "PRK",
    "LBY",
    "MLI",
    "MMR",
    "MAC",
    "NIC",
    "RUS",
    "SDN",
    "SOM",
    "SSD",
    "SYR",
    "VEN",
    "YEM",
]

# Minimum observation thresholds
MIN_OBSERVATIONS_COUNTRY = 200  # Threshold for countries
MIN_OBSERVATIONS_US_STATE = 100  # Threshold for US states

# Define the tier colors
TIER_COLORS_LIST = ["#E6DBD0", "#E5C5AB", "#E4AF86", "#E39961", "#D97757"]

# Anthropic brand color for borders
ANTHROPIC_OAT = "#E3DACC"
AUGMENTATION_COLOR = "#00A078"
AUTOMATION_COLOR = "#FF9940"

# Standard tier color mapping used throughout
TIER_COLORS_DICT = {
    "Minimal": TIER_COLORS_LIST[0],  # Lightest
    "Emerging (bottom 25%)": TIER_COLORS_LIST[1],
    "Lower middle (25-50%)": TIER_COLORS_LIST[2],
    "Upper middle (50-75%)": TIER_COLORS_LIST[3],
    "Leading (top 25%)": TIER_COLORS_LIST[4],  # Darkest
}

# Standard tier ordering
TIER_ORDER = [
    "Leading (top 25%)",
    "Upper middle (50-75%)",
    "Lower middle (25-50%)",
    "Emerging (bottom 25%)",
    "Minimal",
]

# Numeric tier color mapping (for tier values 0-4)
TIER_COLORS_NUMERIC = {i: color for i, color in enumerate(TIER_COLORS_LIST)}

# Numeric tier name mapping (for tier values 1-4 in actual data)
TIER_NAMES_NUMERIC = {
    1: "Emerging (bottom 25%)",
    2: "Lower middle (25-50%)",
    3: "Upper middle (50-75%)",
    4: "Leading (top 25%)",
}

# Create a custom colormap that can be used for continuous variables
CUSTOM_CMAP = LinearSegmentedColormap.from_list("custom_tier", TIER_COLORS_LIST, N=256)

# Map layout constants
MAP_PADDING_X = 0.25  # Horizontal padding for legend space
MAP_PADDING_Y = 0.05  # Vertical padding
ALASKA_INSET_BOUNDS = [0.26, 0.18, 0.15, 0.15]  # [left, bottom, width, height]
HAWAII_INSET_BOUNDS = [0.40, 0.18, 0.11, 0.11]  # [left, bottom, width, height]


# Figure style and setup
def setup_plot_style():
    """Configure matplotlib."""
    plt.style.use("default")
    plt.rcParams.update(
        {
            "figure.dpi": 150,
            "savefig.dpi": 150,
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
        }
    )


def create_figure(figsize=(12, 8), tight_layout=True, nrows=1, ncols=1):
    """Create a figure with consistent settings.

    Args:
        figsize: Figure size tuple
        tight_layout: Whether to use tight layout
        nrows: Number of subplot rows
        ncols: Number of subplot columns

    Returns:
        fig, ax or fig, axes depending on subplot configuration
    """
    fig, ax = plt.subplots(nrows, ncols, figsize=figsize)
    if tight_layout:
        fig.tight_layout()
    else:
        # Explicitly disable the layout engine to prevent warnings
        fig.set_layout_engine(layout="none")
    return fig, ax


def format_axis(
    ax,
    xlabel=None,
    ylabel=None,
    title=None,
    xlabel_size=11,
    ylabel_size=11,
    title_size=13,
    grid=True,
    grid_alpha=0.3,
):
    """Apply consistent axis formatting."""
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=xlabel_size)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=ylabel_size)
    if title:
        ax.set_title(title, fontsize=title_size, fontweight="bold", pad=15)
    if grid:
        ax.grid(True, alpha=grid_alpha)
    return ax


def get_color_normalizer(values, center_at_one=False, vmin=None, vmax=None):
    """Create appropriate color normalizer for data."""
    if center_at_one:
        # Use TwoSlopeNorm for diverging around 1.0
        if vmin is None:
            vmin = min(values.min(), 0.1)
        if vmax is None:
            vmax = max(values.max(), 2.0)
        return TwoSlopeNorm(vmin=vmin, vcenter=1.0, vmax=vmax)
    else:
        # Use regular normalization
        if vmin is None:
            vmin = values.min()
        if vmax is None:
            vmax = values.max()
        return Normalize(vmin=vmin, vmax=vmax)


def create_tier_legend(
    ax,
    tier_colors,
    tiers_in_data,
    excluded_countries=False,
    no_data=False,
    loc="lower left",
    title="Anthropic AI Usage Index tier",
):
    """Create a consistent tier legend for maps."""
    legend_elements = []
    for tier in TIER_ORDER:
        if tier in tiers_in_data:
            legend_elements.append(
                mpatches.Patch(
                    facecolor=tier_colors[tier], edgecolor="none", label=tier
                )
            )

    if excluded_countries:
        legend_elements.append(
            mpatches.Patch(
                facecolor="#c0c0c0", edgecolor="white", label="Claude not available"
            )
        )

    if no_data:
        legend_elements.append(
            mpatches.Patch(facecolor="#f0f0f0", edgecolor="white", label="No data")
        )

    if legend_elements:
        ax.legend(
            handles=legend_elements,
            loc=loc,
            fontsize=10,
            bbox_to_anchor=(0, 0) if loc == "lower left" else None,
            title=title,
            title_fontsize=11,
            frameon=True,
            fancybox=True,
            shadow=True,
        )

    return ax


# Data wrangling helpers


def filter_df(df, **kwargs):
    """Universal filter helper for dataframes.

    Args:
        df: DataFrame to filter
        **kwargs: Column-value pairs to filter on
                  Lists are handled with .isin()

    Returns:
        Filtered DataFrame
    """
    mask = pd.Series([True] * len(df), index=df.index)

    for key, value in kwargs.items():
        if value is None:
            continue  # Skip None values
        if key in df.columns:
            if isinstance(value, list):
                mask = mask & df[key].isin(value)
            else:
                mask = mask & (df[key] == value)

    return df[mask]


def get_filtered_geographies(df, min_obs_country=None, min_obs_state=None):
    """
    Get lists of countries and states that meet MIN_OBSERVATIONS thresholds.

    This function does NOT filter the dataframe - it only identifies which
    geographies meet the thresholds. The full dataframe is preserved
    so we can still report statistics for all geographies.

    Args:
        df: Input dataframe
        min_obs_country: Minimum observations for countries (default: MIN_OBSERVATIONS_COUNTRY)
        min_obs_state: Minimum observations for states (default: MIN_OBSERVATIONS_US_STATE)

    Returns:
        Tuple of (filtered_countries list, filtered_states list)
    """
    # Use defaults if not specified
    if min_obs_country is None:
        min_obs_country = MIN_OBSERVATIONS_COUNTRY
    if min_obs_state is None:
        min_obs_state = MIN_OBSERVATIONS_US_STATE

    # Get country usage counts
    country_usage = filter_df(df, facet="country", variable="usage_count").set_index(
        "geo_id"
    )["value"]

    # Get state usage counts
    state_usage = filter_df(df, facet="state_us", variable="usage_count").set_index(
        "geo_id"
    )["value"]

    # Get countries that meet threshold (excluding not_classified)
    filtered_countries = country_usage[country_usage >= min_obs_country].index.tolist()
    filtered_countries = [c for c in filtered_countries if c != "not_classified"]

    # Get states that meet threshold (excluding not_classified)
    filtered_states = state_usage[state_usage >= min_obs_state].index.tolist()
    filtered_states = [s for s in filtered_states if s != "not_classified"]

    return filtered_countries, filtered_states


def filter_requests_by_threshold(df, geography, geo_id, level=1, threshold=1.0):
    """
    Filter requests to only include requests at a specific level that meet threshold requirements.

    Args:
        df: Long format dataframe with request data
        geography: Current geography level ('country' or 'state_us')
        geo_id: Current geography ID (e.g., 'USA', 'CA')
        level: Request level to filter (default=1 for middle aggregated)
        threshold: Minimum percentage threshold (default=1.0%)

    Returns:
        List of valid cluster_names that:
        1. Are at the specified level (default level 1)
        2. Have >= threshold % in the current geography
        3. Have >= threshold % in the parent geography (USA for states, GLOBAL for countries)
    """
    # Determine parent geography
    if geography == "state_us":
        parent_geo = "USA"
        parent_geography = "country"
    elif geography == "country":
        parent_geo = "GLOBAL"
        parent_geography = "global"
    else:  # global
        # For global, no parent filtering needed
        df_local = filter_df(
            df,
            geography=geography,
            geo_id=geo_id,
            facet="request",
            level=level,
            variable="request_pct",
        )
        return df_local[df_local["value"] >= threshold]["cluster_name"].tolist()

    # Get local request percentages at specified level
    df_local = filter_df(
        df,
        geography=geography,
        geo_id=geo_id,
        facet="request",
        level=level,
        variable="request_pct",
    )

    # Get parent request percentages at same level
    df_parent = filter_df(
        df,
        geography=parent_geography,
        geo_id=parent_geo,
        facet="request",
        level=level,
        variable="request_pct",
    )

    # Filter by local threshold
    local_valid = set(df_local[df_local["value"] >= threshold]["cluster_name"])

    # Filter by parent threshold
    parent_valid = set(df_parent[df_parent["value"] >= threshold]["cluster_name"])

    # Return intersection (must meet both thresholds)
    return list(local_valid & parent_valid)


# Data loading


def load_world_shapefile():
    """Load and prepare world shapefile for mapping."""
    url = "https://naciscdn.org/naturalearth/10m/cultural/ne_10m_admin_0_countries_iso.zip"
    world = gpd.read_file(url)

    # Remove Antarctica from the dataset entirely
    world = world[world["ISO_A3_EH"] != "ATA"]

    # Use Robinson projection for better world map appearance
    world = world.to_crs("+proj=robin")

    # Mark excluded countries using global EXCLUDED_COUNTRIES
    world["is_excluded"] = world["ISO_A3_EH"].isin(EXCLUDED_COUNTRIES)

    return world


def load_us_states_shapefile():
    """Load and prepare US states shapefile for mapping."""
    import ssl

    # Create unverified SSL context to handle Census Bureau cert issues
    ssl._create_default_https_context = ssl._create_unverified_context

    states_url = (
        "https://www2.census.gov/geo/tiger/GENZ2018/shp/cb_2018_us_state_20m.zip"
    )
    states = gpd.read_file(states_url)

    # Filter out territories but keep all 50 states and DC
    states = states[~states["STUSPS"].isin(["PR", "VI", "MP", "GU", "AS"])]

    return states


def merge_geo_data(shapefile, df_data, geo_column, columns_to_merge, is_tier=False):
    """Merge data with geographic shapefile.

    Args:
        shapefile: GeoDataFrame (world or states)
        df_data: DataFrame with data to merge
        geo_column: Column in shapefile to join on (e.g., 'ISO_A3_EH', 'STUSPS')
        columns_to_merge: List of columns to merge from df_data
        is_tier: Whether this is tier data (includes cluster_name)

    Returns:
        Merged GeoDataFrame
    """
    if is_tier and "cluster_name" not in columns_to_merge:
        columns_to_merge = columns_to_merge + ["cluster_name"]

    return shapefile.merge(
        df_data[columns_to_merge], left_on=geo_column, right_on="geo_id", how="left"
    )


def prepare_map_data(
    geo_df,
    value_column="value",
    center_at_one=False,
    excluded_mask=None,
):
    """Prepare data and normalization for map plotting.

    Args:
        geo_df: GeoDataFrame with geographic data and values to plot
        value_column: Name of column containing values to plot (default: "value")
        center_at_one: If True, center color scale at 1.0 for diverging colormap (default: False)
        excluded_mask: Boolean Series indicating which rows to exclude from normalization
                       (e.g., countries where service isn't available). If None, no exclusions.

    Returns:
        tuple: (plot_column_name, norm) where norm is the matplotlib Normalize object
    """
    if excluded_mask is None:
        excluded_mask = pd.Series([False] * len(geo_df), index=geo_df.index)

    valid_data = geo_df[geo_df[value_column].notna() & ~excluded_mask][value_column]

    vmin = valid_data.min() if len(valid_data) > 0 else 0
    vmax = valid_data.max() if len(valid_data) > 0 else 1
    norm = get_color_normalizer(
        valid_data, center_at_one=center_at_one, vmin=vmin, vmax=vmax
    )

    return value_column, norm


# Main visualization functions


def plot_world_map(
    ax, world, data_column="value", tier_colors=None, cmap=None, norm=None
):
    """Plot world map with data.

    Args:
        ax: matplotlib axis
        world: GeoDataFrame with world data (already merged with values)
        data_column: column name containing data to plot
        tier_colors: dict mapping tier names to colors (for categorical)
        cmap: colormap (for continuous)
        norm: normalization (for continuous)
    """
    if tier_colors:
        # Plot each tier with its color
        for tier, color in tier_colors.items():
            tier_countries = world[
                (world["cluster_name"] == tier) & (~world["is_excluded"])
            ]
            tier_countries.plot(ax=ax, color=color, edgecolor="white", linewidth=0.5)
    else:
        # Plot continuous data
        world_with_data = world[
            world[data_column].notna() & (world["is_excluded"] == False)
        ]
        world_with_data.plot(
            column=data_column, ax=ax, cmap=cmap, norm=norm, legend=False
        )

    # Plot excluded countries
    excluded = world[world["is_excluded"] == True]
    if not excluded.empty:
        excluded.plot(ax=ax, color="#c0c0c0", edgecolor="white", linewidth=0.5)

    # Plot no-data countries
    no_data = world[
        (world[data_column if not tier_colors else "cluster_name"].isna())
        & (~world["is_excluded"])
    ]
    if not no_data.empty:
        no_data.plot(ax=ax, color="#f0f0f0", edgecolor="white", linewidth=0.5)

    # Set appropriate bounds for Robinson projection
    ax.set_xlim(-17000000, 17000000)
    ax.set_ylim(-8500000, 8500000)


def plot_us_states_map(
    fig, ax, states, data_column="value", tier_colors=None, cmap=None, norm=None
):
    """Plot US states map with Alaska and Hawaii insets.

    Args:
        fig: matplotlib figure
        ax: main axis for continental US
        states: GeoDataFrame with state data (already merged with values)
        data_column: column name containing data to plot
        tier_colors: dict mapping tier names to colors (for categorical)
        cmap: colormap (for continuous)
        norm: normalization (for continuous)
    """
    # Project to EPSG:2163 for US Albers Equal Area
    states = states.to_crs("EPSG:2163")

    # Plot continental US (everything except AK and HI)
    continental = states[~states["STUSPS"].isin(["AK", "HI"])]

    # First plot all continental states as no-data background
    continental.plot(ax=ax, color="#f0f0f0", edgecolor="white", linewidth=0.5)

    # Plot continental states with data
    if tier_colors:
        # Plot each tier with its color
        for tier, color in tier_colors.items():
            tier_states = continental[continental["cluster_name"] == tier]
            if not tier_states.empty:
                tier_states.plot(ax=ax, color=color, edgecolor="white", linewidth=0.5)
    else:
        # Plot continuous data
        continental_with_data = continental[continental[data_column].notna()]
        if not continental_with_data.empty:
            continental_with_data.plot(
                column=data_column, ax=ax, cmap=cmap, norm=norm, legend=False
            )

    # Set axis limits with padding for legend
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    x_padding = (xlim[1] - xlim[0]) * MAP_PADDING_X
    y_padding = (ylim[1] - ylim[0]) * MAP_PADDING_Y
    ax.set_xlim(xlim[0] - x_padding, xlim[1] + x_padding)
    ax.set_ylim(ylim[0] - y_padding, ylim[1] + y_padding)

    # Add Alaska inset
    akax = fig.add_axes(ALASKA_INSET_BOUNDS)
    akax.axis("off")

    alaska = states[states["STUSPS"] == "AK"]
    if not alaska.empty:
        alaska.plot(ax=akax, color="#f0f0f0", edgecolor="white", linewidth=0.5)

        if tier_colors and alaska["cluster_name"].notna().any():
            tier_name = alaska["cluster_name"].iloc[0]
            if tier_name in tier_colors:
                alaska.plot(
                    ax=akax,
                    color=tier_colors[tier_name],
                    edgecolor="white",
                    linewidth=0.5,
                )
        elif not tier_colors and alaska[data_column].notna().any():
            alaska.plot(column=data_column, ax=akax, cmap=cmap, norm=norm, legend=False)

    # Add Hawaii inset
    hiax = fig.add_axes(HAWAII_INSET_BOUNDS)
    hiax.axis("off")

    hawaii = states[states["STUSPS"] == "HI"]
    if not hawaii.empty:
        hawaii.plot(ax=hiax, color="#f0f0f0", edgecolor="white", linewidth=0.5)

        if tier_colors and hawaii["cluster_name"].notna().any():
            tier_name = hawaii["cluster_name"].iloc[0]
            if tier_name in tier_colors:
                hawaii.plot(
                    ax=hiax,
                    color=tier_colors[tier_name],
                    edgecolor="white",
                    linewidth=0.5,
                )
        elif not tier_colors and hawaii[data_column].notna().any():
            hawaii.plot(column=data_column, ax=hiax, cmap=cmap, norm=norm, legend=False)


def plot_usage_index_bars(
    df,
    geography="country",
    top_n=None,
    figsize=(12, 8),
    title=None,
    filtered_entities=None,
    show_usage_counts=True,
    cmap=CUSTOM_CMAP,
):
    """
    Create horizontal bar chart of Anthropic AI Usage Index.

    Args:
        df: Long format dataframe
        geography: 'country' or 'state_us'
        top_n: Number of top entities to show (None for all)
        figsize: Figure size
        title: Chart title
        filtered_entities: List of geo_id values to include (if None, include all)
        show_usage_counts: If True, show usage counts in labels (default: True)
    """
    # Get data
    df_metric = filter_df(
        df, geography=geography, facet=geography, variable="usage_per_capita_index"
    )

    # Apply entity filtering if provided
    if filtered_entities is not None:
        df_metric = df_metric[df_metric["geo_id"].isin(filtered_entities)]

    # Get usage counts for display if requested
    if show_usage_counts:
        df_usage = filter_df(
            df, geography=geography, facet=geography, variable="usage_count"
        )
        # Merge to get usage counts
        df_metric = df_metric.merge(
            df_usage[["geo_id", "value"]],
            on="geo_id",
            suffixes=("", "_usage"),
            how="left",
        )

    # Select entities to display
    if top_n is None or top_n >= len(df_metric):
        # Show all entities, sorted by lowest value first (will appear at bottom of chart)
        df_top = df_metric.sort_values("value", ascending=True)
        # Adjust figure height for many entities
        if len(df_top) > 20:
            figsize = (figsize[0], max(10, len(df_top) * 0.3))
    else:
        # Select top N entities, then sort ascending so highest values appear at top
        df_top = df_metric.nlargest(top_n, "value")
        df_top = df_top.sort_values("value", ascending=True)

    # Create figure
    fig, ax = create_figure(figsize=figsize)

    # Get colormap and create diverging colors centered at 1
    values = df_top["value"].values
    min_val = values.min()
    max_val = values.max()

    # Determine the range for symmetric color scaling around 1
    max_distance = max(abs(min_val - 1), abs(max_val - 1))

    # Normalize values for color mapping
    if max_distance > 0:
        # Normalize to 0-1 centered at 0.5 for value 1
        normalized = 0.5 + (values - 1) / (2 * max_distance)
        # Truncate colormap to avoid too light colors
        truncate_low = 0.2
        truncate_high = 0.8
        normalized = truncate_low + normalized * (truncate_high - truncate_low)
        normalized = np.clip(normalized, truncate_low, truncate_high)
    else:
        normalized = np.ones_like(values) * 0.5

    colors = cmap(normalized)

    # Create horizontal bars
    y_positions = range(len(df_top))
    bars = ax.barh(y_positions, values, color=colors, height=0.7)

    # Set y-tick labels
    ax.set_yticks(y_positions)
    ax.set_yticklabels(df_top["geo_name"].values)

    # Set y-axis limits to reduce white space
    ax.set_ylim(-0.5, len(df_top) - 0.5)

    # Add baseline reference line at 1.0
    ax.axvline(x=1.0, color="black", linestyle="--", alpha=0.5, linewidth=1)

    # Calculate and set x-axis limits with extra space for labels
    if max_val > 2:
        ax.set_xlim(0, max_val * 1.25)
    else:
        ax.set_xlim(0, max_val * 1.2)

    # Add value labels and usage counts
    for i, bar in enumerate(bars):
        width = bar.get_width()
        # Always use 2 decimal places for consistency
        label = f"{width:.2f}"

        # Get usage count
        usage_count = df_top.iloc[i]["value_usage"]
        if usage_count >= 1000:
            usage_str = f"{usage_count / 1000:.1f}k"
        else:
            usage_str = f"{int(usage_count)}"

        # For top_n > 20, combine label with usage count to avoid overlap
        if not top_n or top_n > 20:
            combined_label = f"{label} (N={usage_str})"
            ax.text(
                width + 0.03,
                bar.get_y() + bar.get_height() / 2.0,
                combined_label,
                ha="left",
                va="center",
                fontsize=8,
            )
        else:
            # Add value label to the right of the bar
            ax.text(
                width + 0.03,
                bar.get_y() + bar.get_height() / 2.0,
                label,
                ha="left",
                va="center",
                fontsize=9,
            )

            # Add usage count inside the bar
            usage_str_full = f"N = {usage_str}"
            ax.text(
                0.05,
                bar.get_y() + bar.get_height() / 2.0,
                usage_str_full,
                ha="left",
                va="center",
                fontsize=8,
                color="white",
            )

    # Set labels and title
    if top_n:
        default_title = f"Top {top_n} {'countries' if geography == 'country' else 'US states'} by Anthropic AI Usage Index"
    else:
        default_title = f"Anthropic AI Usage Index by {'country' if geography == 'country' else 'US state'}"

    format_axis(
        ax,
        xlabel="Anthropic AI Usage Index (usage % / working-age population %)",
        title=title or default_title,
        grid=True,
        grid_alpha=0.3,
    )

    return fig


def plot_variable_bars(
    df,
    variable,
    facet,
    geography="country",
    geo_id=None,
    top_n=None,
    figsize=(12, 8),
    title=None,
    xlabel=None,
    filtered_entities=None,
    cmap=CUSTOM_CMAP,
    normalize=False,
    exclude_not_classified=False,
):
    """
    Create horizontal bar chart for any variable.

    Args:
        df: Long format dataframe
        variable: Variable name to plot (e.g., 'soc_pct', 'gdp_per_capita')
        facet: Facet to use
        geography: 'country' or 'state_us'
        geo_id: Optional specific geo_id to filter (e.g., 'USA' for SOC data)
        top_n: Number of top entities to show (None for all)
        figsize: Figure size
        title: Chart title
        xlabel: x-axis label
        filtered_entities: List of cluster_name or geo_id values to include
        cmap: Colormap to use
        normalize: If True, rescale values to sum to 100% (useful for percentages)
        exclude_not_classified: If True, exclude 'not_classified' entries before normalizing
    """
    # Get data
    df_metric = filter_df(
        df, geography=geography, facet=facet, variable=variable, geo_id=geo_id
    )

    # Exclude not_classified if requested (before normalization)
    if exclude_not_classified:
        # Check both cluster_name and geo_id columns
        if "cluster_name" in df_metric.columns:
            df_metric = df_metric[
                ~df_metric["cluster_name"].isin(["not_classified", "none"])
            ]
        if "geo_id" in df_metric.columns:
            df_metric = df_metric[~df_metric["geo_id"].isin(["not_classified", "none"])]

    # Normalize if requested (after filtering not_classified)
    if normalize:
        total_sum = df_metric["value"].sum()
        if total_sum > 0:
            df_metric["value"] = (df_metric["value"] / total_sum) * 100

    # Apply entity filtering if provided
    if filtered_entities is not None:
        # Check if we're filtering by cluster_name or geo_id
        if "cluster_name" in df_metric.columns:
            df_metric = df_metric[df_metric["cluster_name"].isin(filtered_entities)]
        else:
            df_metric = df_metric[df_metric["geo_id"].isin(filtered_entities)]

    # Select entities to display
    if top_n is None or top_n >= len(df_metric):
        # Show all entities, sorted by lowest value first
        df_top = df_metric.sort_values("value", ascending=True)
        # Adjust figure height for many entities
        if len(df_top) > 20:
            figsize = (figsize[0], max(10, len(df_top) * 0.3))
    else:
        # Select top N entities
        df_top = df_metric.nlargest(top_n, "value")
        df_top = df_top.sort_values("value", ascending=True)

    # Create figure
    fig, ax = create_figure(figsize=figsize)

    # Get colormap and colors
    values = df_top["value"].values
    min_val = values.min()
    max_val = values.max()

    # Linear color mapping
    if max_val > min_val:
        normalized = (values - min_val) / (max_val - min_val)
        # Truncate to avoid extremes
        normalized = 0.2 + normalized * 0.6
    else:
        normalized = np.ones_like(values) * 0.5

    colors = cmap(normalized)

    # Create horizontal bars
    y_positions = range(len(df_top))
    bars = ax.barh(y_positions, values, color=colors, height=0.7)

    # Set y-tick labels
    ax.set_yticks(y_positions)
    # Use cluster_name or geo_name depending on what's available
    if "cluster_name" in df_top.columns:
        labels = df_top["cluster_name"].values
    elif "geo_name" in df_top.columns:
        labels = df_top["geo_name"].values
    else:
        labels = df_top["geo_id"].values
    ax.set_yticklabels(labels)

    # Set y-axis limits to reduce white space
    ax.set_ylim(-0.5, len(df_top) - 0.5)

    # Calculate and set x-axis limits
    x_range = max_val - min_val
    if min_val < 0:
        # Include negative values with some padding
        ax.set_xlim(min_val - x_range * 0.1, max_val + x_range * 0.2)
    else:
        # Positive values only
        ax.set_xlim(0, max_val * 1.2)

    # Add value labels
    for _, bar in enumerate(bars):
        width = bar.get_width()
        # Format based on value magnitude
        if abs(width) >= 1000:
            label = f"{width:.0f}"
        elif abs(width) >= 10:
            label = f"{width:.1f}"
        else:
            label = f"{width:.2f}"

        # Position label
        if width < 0:
            ha = "right"
            x_offset = -0.01 * (max_val - min_val)
        else:
            ha = "left"
            x_offset = 0.01 * (max_val - min_val)

        ax.text(
            width + x_offset,
            bar.get_y() + bar.get_height() / 2.0,
            label,
            ha=ha,
            va="center",
            fontsize=8 if len(df_top) > 20 else 9,
        )

    # Set labels and title
    if not title:
        if top_n:
            title = f"Top {top_n} by {variable}"
        else:
            title = f"{variable} distribution"

    format_axis(
        ax,
        xlabel=xlabel or variable,
        title=title,
        grid=True,
        grid_alpha=0.3,
    )

    return fig


def plot_usage_share_bars(
    df,
    geography="country",
    top_n=20,
    figsize=(12, 8),
    title=None,
    filtered_entities=None,
    cmap=CUSTOM_CMAP,
):
    """
    Create bar chart showing share of global usage.

    Args:
        df: Long format dataframe
        geography: Geographic level
        top_n: Number of top entities
        figsize: Figure size
        title: Chart title
        filtered_entities: List of geo_id values to include (if None, include all)

    """
    # Get data
    df_metric = filter_df(
        df, geography=geography, facet=geography, variable="usage_pct"
    )

    # Exclude "not_classified" from the data
    df_metric = df_metric[df_metric["geo_id"] != "not_classified"]

    # Apply entity filtering if provided
    if filtered_entities is not None:
        df_metric = df_metric[df_metric["geo_id"].isin(filtered_entities)]

    # Get top n
    df_top = df_metric.nlargest(top_n, "value")

    # Create figure
    fig, ax = create_figure(figsize=figsize)

    # Create bars
    positions = range(len(df_top))
    values = df_top["value"].values
    names = df_top["geo_name"].values

    # Use custom colormap
    norm = get_color_normalizer(values, center_at_one=False)
    colors = [cmap(norm(val)) for val in values]

    bars = ax.bar(positions, values, color=colors, alpha=0.8)

    # Customize
    ax.set_xticks(positions)
    ax.set_xticklabels(names, rotation=45, ha="right")
    # Reduce horizontal margins to bring bars closer to plot borders
    ax.margins(x=0.01)

    default_title = f"Top {top_n} {'countries' if geography == 'country' else 'US states'} by share of global Claude usage"
    format_axis(
        ax, ylabel="Share of global usage (%)", title=title or default_title, grid=False
    )

    # Add value labels
    for bar, value in zip(bars, values, strict=True):
        label = f"{value:.1f}%"

        # Add value label above the bar
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value + 0.1,
            label,
            ha="center",
            fontsize=8,
        )

    # Grid
    ax.grid(True, axis="y", alpha=0.3)

    return fig


def plot_usage_index_histogram(
    df, geography="country", bins=30, figsize=(10, 6), title=None, cmap=CUSTOM_CMAP
):
    """
    Create histogram of Anthropic AI Usage Index distribution.

    Args:
        df: Long format dataframe
        geography: Geographic level
        bins: Number of histogram bins
        figsize: Figure size
        title: Chart title
    """
    # Get data
    df_metric = filter_df(
        df, geography=geography, facet=geography, variable="usage_per_capita_index"
    )

    # Create figure
    fig, ax = create_figure(figsize=figsize)

    # Create histogram
    values = df_metric["value"].values
    _, bins_edges, patches = ax.hist(
        values, bins=bins, edgecolor="white", linewidth=0.5
    )

    # Color bars with custom gradient based on value
    norm = get_color_normalizer(
        values,
        center_at_one=False,
        vmin=min(bins_edges[0], 0),
        vmax=max(bins_edges[-1], 2),
    )

    for patch, left_edge, right_edge in zip(
        patches, bins_edges[:-1], bins_edges[1:], strict=True
    ):
        # Use the midpoint of the bin for color
        mid_val = (left_edge + right_edge) / 2
        color = cmap(norm(mid_val))
        patch.set_facecolor(color)

    # Add vertical line at 1.0 (where usage and population shares match)
    ax.axvline(x=1.0, color="black", linestyle="--", alpha=0.5, linewidth=1)

    # Add statistics
    mean_val = values.mean()
    median_val = np.median(values)

    stats_text = f"Mean: {mean_val:.2f}\nMedian: {median_val:.2f}\nN = {len(values)}"
    ax.text(
        0.98,
        0.97,
        stats_text,
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=9,
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
    )

    # Customize
    geo_label = "countries" if geography == "country" else "US states"
    default_title = f"Distribution of Anthropic AI Usage Index ({geo_label})"

    format_axis(
        ax,
        xlabel="Anthropic AI Usage Index (usage % / working-age population %)",
        ylabel=f"Number of {geo_label}",
        title=title or default_title,
    )

    return fig


def plot_gdp_scatter(
    df,
    geography="country",
    figsize=(10, 8),
    title=None,
    cmap=CUSTOM_CMAP,
    filtered_entities=None,
):
    """
    Create log-log scatter plot of GDP vs Anthropic AI Usage Index.

    Args:
        df: Long format dataframe
        geography: Geographic level
        figsize: Figure size
        title: Chart title
        cmap: Colormap to use
        filtered_entities: List of geo_id values that meet MIN_OBSERVATIONS threshold (optional)
    """
    # Get usage data
    df_usage = filter_df(
        df, geography=geography, facet=geography, variable="usage_per_capita_index"
    )

    # Apply filtering if provided
    if filtered_entities is not None:
        df_usage = df_usage[df_usage["geo_id"].isin(filtered_entities)]

    df_usage = df_usage[["geo_id", "cluster_name", "value"]].rename(
        columns={"value": "usage_index"}
    )

    # Get GDP data
    df_gdp = filter_df(
        df, geography=geography, facet=geography, variable="gdp_per_working_age_capita"
    )

    # Apply same filtering to GDP data
    if filtered_entities is not None:
        df_gdp = df_gdp[df_gdp["geo_id"].isin(filtered_entities)]

    df_gdp = df_gdp[["geo_id", "value"]].rename(columns={"value": "gdp_per_capita"})

    # Merge
    df_plot = df_usage.merge(df_gdp, on="geo_id", how="inner")

    # Filter out zeros and negative values for log scale
    # Explicitly check both GDP and usage are positive (will be true for filtered geos)
    mask = (df_plot["gdp_per_capita"] > 0) & (df_plot["usage_index"] > 0)
    df_plot = df_plot[mask]

    # Create figure
    fig, ax = create_figure(figsize=figsize)

    # Create scatter plot with geo_id values as labels
    x = df_plot["gdp_per_capita"].values
    y = df_plot["usage_index"].values

    # Transform to log space for plotting
    log_x = np.log(x)
    log_y = np.log(y)

    # Create norm for colorbar (using natural log)
    norm = plt.Normalize(vmin=log_y.min(), vmax=log_y.max())

    # First, plot invisible points to ensure matplotlib's autoscaling includes all data points
    ax.scatter(log_x, log_y, s=0, alpha=0)  # Size 0, invisible points for autoscaling

    # Plot the geo_id values as text at the exact data points in log space
    for ln_x, ln_y, geo_id in zip(log_x, log_y, df_plot["geo_id"].values, strict=True):
        # Get color from colormap based on ln(usage_index)
        color_val = norm(ln_y)
        text_color = cmap(color_val)

        ax.text(
            ln_x,
            ln_y,
            geo_id,
            fontsize=7,
            ha="center",
            va="center",
            color=text_color,
            alpha=0.9,
            weight="bold",
        )

    # Add constant for intercept
    X_with_const = sm.add_constant(log_x)

    # Fit OLS regression in log space
    model = sm.OLS(log_y, X_with_const)
    results = model.fit()

    # Extract statistics
    intercept = results.params[0]
    slope = results.params[1]
    r_squared = results.rsquared
    p_value = results.pvalues[1]  # p-value for slope

    # Create fit line (we're already in log space)
    x_fit = np.linspace(log_x.min(), log_x.max(), 100)
    y_fit = intercept + slope * x_fit
    ax.plot(
        x_fit,
        y_fit,
        "gray",
        linestyle="--",
        alpha=0.7,
        linewidth=2,
        label=f"Power law: AUI ~ GDP^{slope:.2f}",
    )

    # Add regression statistics
    # Format p-value display
    if p_value < 0.001:
        p_str = "p < 0.001"
    else:
        p_str = f"p = {p_value:.3f}"

    ax.text(
        0.05,
        0.95,
        f"$\\beta = {slope:.3f}\\ ({p_str})$\n$R^2 = {r_squared:.3f}$",
        transform=ax.transAxes,
        fontsize=10,
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
        verticalalignment="top",
    )

    # Customize labels for log-transformed values
    xlabel = "ln(GDP per working-age capita in USD)"
    ylabel = "ln(Anthropic AI Usage Index)"
    default_title = f"Income and Anthropic AI Usage Index by {'country' if geography == 'country' else 'US state'}"

    format_axis(
        ax, xlabel=xlabel, ylabel=ylabel, title=title or default_title, grid=False
    )

    # Grid for log scale
    ax.grid(True, alpha=0.3, which="both", linestyle="-", linewidth=0.5)

    # Add legend
    ax.legend(loc="best")

    # Create colorbar using ScalarMappable
    scalar_mappable = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    scalar_mappable.set_array([])
    cbar = plt.colorbar(scalar_mappable, ax=ax)
    cbar.set_label(
        "ln(Anthropic AI Usage Index)", fontsize=9, rotation=270, labelpad=15
    )

    return fig


def plot_request_comparison_cards(
    df,
    geo_ids,
    title,
    geography,
    top_n=5,
    figsize=(10, 6),
    exclude_not_classified=True,
    request_level=1,
    request_threshold=1.0,
):
    """
    Create a condensed card visualization showing top overrepresented request categories
    for multiple geographies (countries or states).

    Args:
        df: Long format dataframe
        geo_ids: List of geography IDs to compare (e.g., ['USA', 'BRA', 'VNM', 'IND'])
        title: Title for the figure (required)
        geography: Geographic level ('country' or 'state_us')
        top_n: Number of top requests to show per geography (default 5)
        figsize: Figure size as tuple
        exclude_not_classified: Whether to exclude "not_classified" entries
        request_level: Request hierarchy level to use (default 1)
        request_threshold: Minimum percentage threshold for requests (default 1.0%)
    """
    # Get data for specified geography
    data_subset = filter_df(df, facet="request", geo_id=geo_ids, geography=geography)

    # Filter for request_pct_index variable and specified level
    data_subset = filter_df(
        data_subset, variable="request_pct_index", level=request_level
    )

    # Exclude not_classified if requested
    if exclude_not_classified:
        data_subset = data_subset[
            ~data_subset["cluster_name"].str.contains("not_classified", na=False)
        ]

    # Get tier and geo_name information
    geo_info = filter_df(
        df, geography=geography, variable="usage_tier", geo_id=geo_ids
    )[["geo_id", "geo_name", "value"]].drop_duplicates()
    tier_map = dict(zip(geo_info["geo_id"], geo_info["value"], strict=True))
    name_map = dict(zip(geo_info["geo_id"], geo_info["geo_name"], strict=True))

    # Set up figure with 2x2 grid for 4 geographies
    n_rows, n_cols = 2, 2
    fig, axes = create_figure(figsize=figsize, nrows=n_rows, ncols=n_cols)
    axes = axes.flatten()

    # Use global tier colors
    tier_colors = TIER_COLORS_NUMERIC

    # Process each geography
    for idx, geo_id in enumerate(geo_ids):
        ax = axes[idx]

        # Apply request threshold filtering to get valid requests for this geography
        valid_requests = filter_requests_by_threshold(
            df, geography, geo_id, level=request_level, threshold=request_threshold
        )

        # Get data for this geography, filtered by valid requests
        geo_data = data_subset[
            (data_subset["geo_id"] == geo_id)
            & (data_subset["cluster_name"].isin(valid_requests))
            & (data_subset["value"] > 1.0)  # Only show overrepresented requests
        ].copy()

        # Get top n from the filtered requests
        geo_data = geo_data.nlargest(top_n, "value")

        # Get tier color
        tier = tier_map[geo_id]
        base_color = tier_colors[tier]

        # Create a lighter version of the tier color for the card background
        rgb = mcolors.to_rgb(base_color)
        # Mix with white (85% white, 15% color for very subtle background)
        pastel_rgb = tuple(0.85 + 0.15 * c for c in rgb)
        card_bg_color = mcolors.to_hex(pastel_rgb)

        # Fill entire axis with background color
        ax.set_facecolor(card_bg_color)

        # Create card with requests
        card_height = 0.9  # Fixed height for all cards
        card_bottom = 0.965 - card_height  # Consistent positioning

        card_rect = FancyBboxPatch(
            (0.10, card_bottom),
            0.80,
            card_height,
            transform=ax.transAxes,
            boxstyle="round,pad=0.02,rounding_size=0.035",
            facecolor=card_bg_color,
            edgecolor="none",
            linewidth=2,
            clip_on=False,
        )
        ax.add_patch(card_rect)

        # Header bar
        header_top = 0.965 - 0.10
        header_rect = FancyBboxPatch(
            (0.14, header_top),
            0.72,
            0.08,
            transform=ax.transAxes,
            boxstyle="round,pad=0.01,rounding_size=0.03",
            facecolor=base_color,
            edgecolor="none",
            alpha=0.7,
            clip_on=False,
        )
        ax.add_patch(header_rect)

        # Add geography name
        geo_name = name_map[geo_id]

        ax.text(
            0.5,
            header_top + 0.04,
            geo_name,
            transform=ax.transAxes,
            ha="center",
            va="center",
            fontsize=12,
            fontweight="bold",
            color="#1C1C1C",
        )

        # Adjust start position below header upwards
        y_pos = header_top - 0.05

        for _, row in geo_data.iterrows():
            request = row["cluster_name"]
            value = row["value"]

            # Format ratio
            if value >= 10:
                ratio_str = f"{value:.0f}x"
            elif value >= 2:
                ratio_str = f"{value:.1f}x"
            else:
                ratio_str = f"{value:.2f}x"

            # Wrap text
            wrapped_text = textwrap.fill(request, width=46, break_long_words=False)
            lines = wrapped_text.split("\n")

            # Display text lines with sufficient line spacing
            line_spacing = 0.045
            for j, line in enumerate(lines):
                ax.text(
                    0.13,  # Adjust text position for wider card
                    y_pos - j * line_spacing,
                    line,
                    transform=ax.transAxes,
                    ha="left",
                    va="top",
                    fontsize=9,
                    color="#1C1C1C",
                    rasterized=False,
                )

            # Position ratio with adjusted margin for wide card
            text_height = len(lines) * line_spacing
            ax.text(
                0.85,
                y_pos - (text_height - line_spacing) / 2,
                ratio_str,
                transform=ax.transAxes,
                ha="right",
                va="center",
                fontsize=10,
                fontweight="bold",
                color="#B85450",
                rasterized=False,
            )

            # Add space between different requests
            y_pos -= text_height + 0.05

        # Remove axes
        ax.axis("off")

    # Add title
    fig.suptitle(title, fontsize=14, fontweight="bold", y=0.98)

    plt.tight_layout()
    plt.subplots_adjust(
        top=0.92, bottom=0.02, left=0.01, right=0.99, hspace=0.02, wspace=0.02
    )

    return fig


def plot_dc_task_request_cards(
    df,
    title,
    figsize=(10, 5),
):
    """
    Create professional card visualizations showing top overrepresented O*NET tasks and requests for Washington, DC.

    Args:
        df: Long format dataframe
        figsize: Figure size as tuple
        title: Optional title for the figure
    """
    # Fixed parameters for DC
    geo_id = "DC"
    geography = "state_us"
    top_n = 5

    # Get tier for color
    tier_data = filter_df(
        df, geography=geography, variable="usage_tier", geo_id=[geo_id]
    )
    tier = tier_data["value"].iloc[0]

    # Use tier color
    tier_colors = TIER_COLORS_NUMERIC
    base_color = tier_colors[tier]

    # Create lighter version for card background
    rgb = mcolors.to_rgb(base_color)
    pastel_rgb = tuple(0.85 + 0.15 * c for c in rgb)
    card_bg_color = mcolors.to_hex(pastel_rgb)

    # Create figure with 2 subplots (cards)
    fig, axes = create_figure(figsize=figsize, ncols=2)

    # Card 1: Top O*NET Tasks
    ax1 = axes[0]
    ax1.set_facecolor(card_bg_color)

    # Get O*NET task data
    df_tasks = filter_df(
        df,
        geography=geography,
        geo_id=[geo_id],
        facet="onet_task",
        variable="onet_task_pct_index",
    )

    # Exclude not_classified and none
    df_tasks = df_tasks[~df_tasks["cluster_name"].isin(["not_classified", "none"])]

    # Get top n overrepresented tasks
    df_tasks = df_tasks[df_tasks["value"] > 1.0].nlargest(top_n, "value")

    # Use fixed card heights
    card_height_tasks = 0.955
    card_bottom_tasks = 0.965 - card_height_tasks

    # Draw card for O*NET tasks
    card_rect1 = FancyBboxPatch(
        (0.10, card_bottom_tasks),
        0.80,
        card_height_tasks,
        transform=ax1.transAxes,
        boxstyle="round,pad=0.02,rounding_size=0.035",
        facecolor=card_bg_color,
        edgecolor="none",
        linewidth=2,
        clip_on=False,
    )
    ax1.add_patch(card_rect1)

    # Header for O*NET tasks
    header_top = 0.965 - 0.10
    header_rect1 = FancyBboxPatch(
        (0.12, header_top),
        0.76,
        0.08,
        transform=ax1.transAxes,
        boxstyle="round,pad=0.01,rounding_size=0.03",
        facecolor=base_color,
        edgecolor="none",
        alpha=0.7,
        clip_on=False,
    )
    ax1.add_patch(header_rect1)

    ax1.text(
        0.5,
        header_top + 0.04,
        "Top 5 overrepresented O*NET tasks in DC",
        transform=ax1.transAxes,
        ha="center",
        va="center",
        fontsize=11,
        fontweight="bold",
        color="#1C1C1C",
    )

    # Add task items
    y_pos = header_top - 0.05

    for _, row in df_tasks.iterrows():
        task = row["cluster_name"]
        value = row["value"]

        # Convert to sentence case and remove trailing period
        task = task[0].upper() + task[1:].lower() if task else task
        task = task.rstrip(".")  # Remove trailing period

        # Format ratio - always with 2 decimal places
        ratio_str = f"{value:.2f}x"

        # Wrap text
        wrapped_text = textwrap.fill(task, width=46, break_long_words=False)
        lines = wrapped_text.split("\n")

        # Display text lines
        line_spacing = 0.045
        for j, line in enumerate(lines):
            ax1.text(
                0.13,
                y_pos - j * line_spacing,
                line,
                transform=ax1.transAxes,
                ha="left",
                va="top",
                fontsize=9,
                color="#1C1C1C",
                rasterized=False,
            )

        # Add ratio at the right with consistent color
        ax1.text(
            0.87,
            y_pos - (len(lines) - 1) * line_spacing / 2,
            ratio_str,
            transform=ax1.transAxes,
            ha="right",
            va="center",
            fontsize=10,
            color="#B85450",
            fontweight="bold",
        )

        # Move to next item position
        y_pos -= len(lines) * line_spacing + 0.025

    ax1.axis("off")

    # Card 2: Top Requests
    ax2 = axes[1]
    ax2.set_facecolor(card_bg_color)

    # Get valid requests using threshold
    valid_requests = filter_requests_by_threshold(
        df, geography, geo_id, level=1, threshold=1.0
    )

    # Get request data
    df_requests = filter_df(
        df,
        geography=geography,
        geo_id=[geo_id],
        facet="request",
        variable="request_pct_index",
        level=1,
    )

    # Filter by valid requests and overrepresented
    df_requests = df_requests[
        (df_requests["cluster_name"].isin(valid_requests))
        & (df_requests["value"] > 1.0)
        & (~df_requests["cluster_name"].str.contains("not_classified", na=False))
    ]

    # Get top n
    df_requests = df_requests.nlargest(top_n, "value")

    # Draw card for requests with fixed height
    card_height_requests = 0.72
    card_bottom_requests = 0.965 - card_height_requests

    card_rect2 = FancyBboxPatch(
        (0.10, card_bottom_requests),
        0.80,
        card_height_requests,
        transform=ax2.transAxes,
        boxstyle="round,pad=0.02,rounding_size=0.035",
        facecolor=card_bg_color,
        edgecolor="none",
        linewidth=2,
        clip_on=False,
    )
    ax2.add_patch(card_rect2)

    # Header for requests
    header_rect2 = FancyBboxPatch(
        (0.12, header_top),
        0.76,
        0.08,
        transform=ax2.transAxes,
        boxstyle="round,pad=0.01,rounding_size=0.03",
        facecolor=base_color,
        edgecolor="none",
        alpha=0.7,
        clip_on=False,
    )
    ax2.add_patch(header_rect2)

    ax2.text(
        0.5,
        header_top + 0.04,
        "Top 5 overrepresented request clusters in DC",
        transform=ax2.transAxes,
        ha="center",
        va="center",
        fontsize=11,
        fontweight="bold",
        color="#1C1C1C",
    )

    # Add request items
    y_pos = header_top - 0.05

    for _, row in df_requests.iterrows():
        request = row["cluster_name"]
        value = row["value"]

        # Format ratio always with 2 decimal places
        ratio_str = f"{value:.2f}x"

        # Wrap text
        wrapped_text = textwrap.fill(request, width=46, break_long_words=False)
        lines = wrapped_text.split("\n")

        # Display text lines
        line_spacing = 0.045
        for j, line in enumerate(lines):
            ax2.text(
                0.13,
                y_pos - j * line_spacing,
                line,
                transform=ax2.transAxes,
                ha="left",
                va="top",
                fontsize=9,
                color="#1C1C1C",
                rasterized=False,
            )

        # Add ratio at the right with consistent color
        ax2.text(
            0.87,
            y_pos - (len(lines) - 1) * line_spacing / 2,
            ratio_str,
            transform=ax2.transAxes,
            ha="right",
            va="center",
            fontsize=10,
            color="#B85450",
            fontweight="bold",
        )

        # Move to next item position
        y_pos -= len(lines) * line_spacing + 0.025

    ax2.axis("off")

    # Add subtle title if provided
    fig.suptitle(title, fontsize=13, fontweight="bold", y=0.98)

    plt.tight_layout()
    return fig


# Summary statistics function
def plot_tier_summary_table(df, geography="country", figsize=(12, 6)):
    """
    Create a visual table showing entities per tier and example members.

    Args:
        df: Long format dataframe
        geography: 'country' or 'state_us'
        figsize: Figure size
    """
    # Get tier data
    df_tier = filter_df(df, geography=geography, variable="usage_tier")

    # Exclude US territories that appear as countries (may be confusing to readers)
    if geography == "country":
        us_territories_as_countries = [
            "PRI",
            "VIR",
            "GUM",
            "ASM",
            "MNP",
        ]  # Puerto Rico, Virgin Islands, Guam, American Samoa, Northern Mariana Islands
        df_tier = df_tier[~df_tier["geo_id"].isin(us_territories_as_countries)]

    # Get usage per capita index for sorting entities within tiers
    df_usage_index = filter_df(
        df, geography=geography, variable="usage_per_capita_index"
    )

    # Apply same territory filter to usage index data
    if geography == "country":
        df_usage_index = df_usage_index[
            ~df_usage_index["geo_id"].isin(us_territories_as_countries)
        ]

    # Merge tier with usage index
    df_tier_full = df_tier[["geo_id", "geo_name", "cluster_name"]].merge(
        df_usage_index[["geo_id", "value"]],
        on="geo_id",
        how="left",
        suffixes=("", "_index"),
    )

    # Use global tier colors
    tier_colors = TIER_COLORS_DICT

    # Calculate appropriate figure height based on number of tiers
    n_tiers = sum(
        1 for tier in TIER_ORDER if tier in df_tier_full["cluster_name"].values
    )
    # Adjust height: minimal padding for compact display
    fig_height = 0.5 + n_tiers * 0.3  # Much more compact

    # Create figure with calculated size
    fig, ax = create_figure(figsize=(figsize[0], fig_height))
    ax.axis("tight")
    ax.axis("off")

    # Make background transparent
    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)

    # Prepare table data
    table_data = []
    entity_type = "countries" if geography == "country" else "states"
    col_labels = [
        "Tier",
        "AUI range",
        f"# of {entity_type}",
        f"Example {entity_type}",
    ]

    for tier in TIER_ORDER:
        if tier in df_tier_full["cluster_name"].values:
            # Get entities in this tier
            tier_entities = filter_df(df_tier_full, cluster_name=tier)
            count = len(tier_entities)

            # Calculate usage index range for this tier
            min_index = tier_entities["value"].min()
            max_index = tier_entities["value"].max()
            index_range = f"{min_index:.2f} - {max_index:.2f}"

            # For Minimal tier where all have 0 index, pick shortest names
            if tier == "Minimal" and tier_entities["value"].max() == 0:
                tier_entities = tier_entities.copy()
                tier_entities["name_length"] = tier_entities["geo_name"].str.len()
                top_entities = tier_entities.nsmallest(5, "name_length")[
                    "geo_name"
                ].tolist()
            else:
                # Get top 5 entities by usage index in this tier
                top_entities = tier_entities.nlargest(5, "value")["geo_name"].tolist()

            # Format the example entities as a comma-separated string
            examples = ", ".join(top_entities[:5])

            table_data.append([tier, index_range, str(count), examples])

    # Create table with better column widths
    table = ax.table(
        cellText=table_data,
        colLabels=col_labels,
        cellLoc="left",
        loc="center",
        colWidths=[0.20, 0.18, 0.12, 0.50],
        colColours=[ANTHROPIC_OAT] * 4,
    )

    # Style the table
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 2.2)

    # Set all cell edges to Anthropic oat color
    for _, cell in table.get_celld().items():
        cell.set_edgecolor(ANTHROPIC_OAT)
        cell.set_linewidth(1.5)

    # Color code the rows with consistent black text
    for i, row_data in enumerate(table_data):
        tier_name = row_data[0]
        if tier_name in tier_colors:
            # Color the tier name cell with full opacity
            table[(i + 1, 0)].set_facecolor(tier_colors[tier_name])
            table[(i + 1, 0)].set_text_props(color="black", weight="bold")

            # Light background for usage index range column
            table[(i + 1, 1)].set_facecolor(tier_colors[tier_name])
            table[(i + 1, 1)].set_alpha(0.3)
            table[(i + 1, 1)].set_text_props(ha="center", color="black")

            # Light background for count column
            table[(i + 1, 2)].set_facecolor(tier_colors[tier_name])
            table[(i + 1, 2)].set_alpha(0.2)
            table[(i + 1, 2)].set_text_props(ha="center", color="black")

            # Even lighter background for examples column
            table[(i + 1, 3)].set_facecolor(tier_colors[tier_name])
            table[(i + 1, 3)].set_alpha(0.1)
            table[(i + 1, 3)].set_text_props(color="black")

    # Style header row with Anthropic oat and black text
    for j in range(4):
        table[(0, j)].set_facecolor(ANTHROPIC_OAT)
        table[(0, j)].set_text_props(color="black", weight="bold")

    # Center the count column
    for i in range(len(table_data)):
        table[(i + 1, 1)].set_text_props(ha="center")

    return fig


def plot_tier_map(
    df,
    title,
    geography,
    figsize=(16, 10),
    show_labels=True,
):
    """
    Create a map showing per Anthropic AI Usage Tiers.

    Args:
        df: Long format dataframe with usage_tier variable
        geography: 'country' or 'state_us'
        figsize: Figure size
        title: Map title
        show_labels: whether to show title and legend (False for clean export)
    """
    # Filter for tier data
    df_tier = filter_df(df, geography=geography, variable="usage_tier").copy()

    # Use global tier colors definition
    tier_colors = TIER_COLORS_DICT

    # Map tiers to colors
    df_tier["color"] = df_tier["cluster_name"].map(tier_colors)

    # Set up figure
    # Create figure with tight_layout disabled
    fig, ax = create_figure(figsize=figsize, tight_layout=False)

    if geography == "country":
        # Load world shapefile function
        world = load_world_shapefile()

        # Merge with world data using geo_id (which contains ISO-3 codes)
        # Use ISO_A3_EH for merging as it's complete (ISO_A3 has -99 for France)
        world = merge_geo_data(
            world,
            df_tier,
            "ISO_A3_EH",
            ["geo_id", "color", "cluster_name"],
            is_tier=True,
        )

        # Plot world map
        plot_world_map(ax, world, data_column="cluster_name", tier_colors=tier_colors)

    else:  # state_us
        # Load US states shapefile function
        states = load_us_states_shapefile()

        # Merge with tier data BEFORE projection
        states = merge_geo_data(
            states, df_tier, "STUSPS", ["geo_id", "color", "cluster_name"], is_tier=True
        )

        # Pot states with insets
        plot_us_states_map(
            fig, ax, states, data_column="cluster_name", tier_colors=tier_colors
        )

    # Remove axes
    ax.set_axis_off()

    # Add title only if show_labels=True
    if show_labels:
        format_axis(ax, title=title, title_size=14, grid=False)

    # Check which tiers actually appear in the data
    tiers_in_data = df_tier["cluster_name"].unique()

    # Add legend only if show_labels=True
    if show_labels:
        # Check for excluded countries and no data
        excluded = False
        no_data = False
        if geography == "country":
            if "world" in locals() and "is_excluded" in world.columns:
                excluded = world["is_excluded"].any()
            if "world" in locals():
                no_data = world["cluster_name"].isna().any()
        else:  # state_us
            if "states" in locals():
                no_data = states["cluster_name"].isna().any()

        create_tier_legend(
            ax, tier_colors, tiers_in_data, excluded_countries=excluded, no_data=no_data
        )

    return fig


def plot_variable_map(
    df,
    variable,
    geography="country",
    figsize=(16, 10),
    title=None,
    cmap=CUSTOM_CMAP,
    center_at_one=None,
):
    """
    Create static map for any variable.

    Args:
        df: Long format dataframe
        variable: Variable to plot (e.g., 'usage_pct')
        geography: 'country' or 'state_us'
        figsize: Figure size (width, height) in inches
        title: Map title
        cmap: Matplotlib colormap or name (default uses custom colormap)
        center_at_one: Whether to center the color scale at 1.0 (default True for usage_per_capita_index)
    """
    # Get data for the specified variable
    df_data = filter_df(df, geography=geography, facet=geography, variable=variable)

    # Create figure
    fig = plt.figure(figsize=figsize, dpi=150)
    fig.set_layout_engine(layout="none")  # Disable layout engine for custom axes
    ax = fig.add_subplot(111)

    if geography == "country":
        # Load world shapefile function (automatically marks excluded countries)
        world = load_world_shapefile()

        # Merge using geo_id (which contains ISO-3 codes)
        world = merge_geo_data(
            world, df_data, "ISO_A3_EH", ["geo_id", "value"], is_tier=False
        )

        # Prepare data and normalization
        plot_column, norm = prepare_map_data(
            world, "value", center_at_one, world["is_excluded"]
        )

        # Plot world map
        plot_world_map(ax, world, data_column=plot_column, cmap=cmap, norm=norm)

    else:  # state_us
        # Load US states shapefile function
        states = load_us_states_shapefile()

        # Merge our data with the states shapefile
        states = merge_geo_data(
            states, df_data, "STUSPS", ["geo_id", "value"], is_tier=False
        )

        # Prepare data and normalization
        plot_column, norm = prepare_map_data(states, "value", center_at_one)

        # Plot states with insets
        plot_us_states_map(
            fig, ax, states, data_column=plot_column, cmap=cmap, norm=norm
        )

    # Remove axes
    ax.set_axis_off()

    # Add colorbar with proper size and positioning
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="3%", pad=0.1)

    # Create colorbar
    scalar_mappable = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    scalar_mappable.set_array([])
    cbar = plt.colorbar(scalar_mappable, cax=cax)

    # Set colorbar label based on variable
    if variable == "usage_pct":
        cbar.set_label("Usage share (%)", fontsize=10, rotation=270, labelpad=15)
    elif variable == "usage_per_capita_index":
        cbar.set_label(
            "Anthropic AI Usage Index", fontsize=10, rotation=270, labelpad=15
        )
    else:
        cbar.set_label(variable, fontsize=10, rotation=270, labelpad=15)

    # Set title
    if variable == "usage_pct":
        default_title = "Share of Claude usage by " + (
            "country" if geography == "country" else "US state"
        )
    else:
        default_title = f"{variable} by " + (
            "country" if geography == "country" else "US state"
        )

    format_axis(ax, title=title or default_title, title_size=14, grid=False)

    # Add legend for excluded countries and no data
    legend_elements = []

    # Check if we have excluded countries or no data regions
    if geography == "country":
        # Check for excluded countries (world['is_excluded'] == True)
        if "is_excluded" in world.columns:
            excluded_countries = world[world["is_excluded"] == True]
            if not excluded_countries.empty:
                legend_elements.append(
                    Patch(
                        facecolor="#c0c0c0",
                        edgecolor="white",
                        label="Claude not available",
                    )
                )

            # Check for countries with no data
            no_data_countries = world[
                (world["value"].isna()) & (world["is_excluded"] != True)
            ]
            if not no_data_countries.empty:
                legend_elements.append(
                    Patch(facecolor="#f0f0f0", edgecolor="white", label="No data")
                )

    if legend_elements:
        ax.legend(
            handles=legend_elements,
            loc="lower left",
            fontsize=9,
            frameon=True,
            fancybox=True,
            shadow=True,
            bbox_to_anchor=(0, 0),
        )

    return fig


def plot_soc_usage_scatter(
    df,
    geography,
    filtered_entities=None,
):
    """
    Create faceted scatterplot of SOC percentages vs Anthropic AI Usage Index.
    Always creates a 2x2 grid of square subplots showing the top 4 SOC groups.

    Args:
        df: Long format dataframe with enriched data
        geography: 'country' or 'state_us'
        filtered_entities: List of geo_id values that meet MIN_OBSERVATIONS threshold
    """
    # Fixed configuration for 2x2 grid
    n_cols = 2
    n_rows = 2
    n_top_groups = 4

    # Apply MIN_OBSERVATIONS filtering if not provided
    if filtered_entities is None:
        filtered_countries, filtered_states = get_filtered_geographies(df)
        filtered_entities = (
            filtered_countries if geography == "country" else filtered_states
        )

    # Get Anthropic AI Usage Index data
    df_usage_index = filter_df(
        df,
        geography=geography,
        variable="usage_per_capita_index",
        geo_id=filtered_entities,
    )[["geo_id", "value"]].rename(columns={"value": "ai_usage_index"})

    # Get usage counts for bubble sizes
    df_usage = filter_df(
        df, geography=geography, variable="usage_count", geo_id=filtered_entities
    )[["geo_id", "value"]].rename(columns={"value": "usage_count"})

    # Get tier data for colors
    df_tier = filter_df(
        df, geography=geography, variable="usage_tier", geo_id=filtered_entities
    )[["geo_id", "cluster_name", "value"]].rename(
        columns={"cluster_name": "tier_name", "value": "tier_value"}
    )

    # Get SOC percentages
    df_soc = filter_df(
        df,
        geography=geography,
        facet="soc_occupation",
        variable="soc_pct",
        geo_id=filtered_entities,
    )[["geo_id", "cluster_name", "value"]].rename(
        columns={"cluster_name": "soc_group", "value": "soc_pct"}
    )

    # Merge all data
    df_plot = df_soc.merge(
        df_usage_index, on="geo_id", how="inner"
    )  # inner join because some geographies don't have data for all SOC groups
    df_plot = df_plot.merge(df_usage, on="geo_id", how="left")
    df_plot = df_plot.merge(
        df_tier[["geo_id", "tier_name", "tier_value"]], on="geo_id", how="left"
    )

    # Use parent geography reference for consistent SOC selection
    if geography == "country":
        # Use global reference for countries
        reference_soc = filter_df(
            df,
            geography="global",
            geo_id="GLOBAL",
            facet="soc_occupation",
            variable="soc_pct",
        )
    else:  # state_us
        # Use US reference for states
        reference_soc = filter_df(
            df,
            geography="country",
            geo_id="USA",
            facet="soc_occupation",
            variable="soc_pct",
        )

    # Get top SOC groups from reference (excluding not_classified)
    reference_filtered = reference_soc[
        ~reference_soc["cluster_name"].str.contains("not_classified", na=False)
    ]
    plot_soc_groups = reference_filtered.nlargest(n_top_groups, "value")[
        "cluster_name"
    ].tolist()

    # Filter to selected SOC groups
    df_plot = df_plot[df_plot["soc_group"].isin(plot_soc_groups)]

    tier_colors = TIER_COLORS_DICT

    # Fixed square subplot size for 2x2 grid
    subplot_size = 6  # Each subplot is 6x6 inches
    figsize = (subplot_size * n_cols, subplot_size * n_rows)

    # Create figure
    fig, axes = create_figure(figsize=figsize, nrows=n_rows, ncols=n_cols)
    fig.suptitle(
        "Occupation group shares vs Anthropic AI Usage Index",
        fontsize=16,
        fontweight="bold",
        y=0.98,
    )

    # Flatten axes for easier iteration (always 2x2 grid)
    axes_flat = axes.flatten()

    # Plot each SOC group
    for idx, soc_group in enumerate(plot_soc_groups):
        ax = axes_flat[idx]

        # Get data for this SOC group
        soc_data = filter_df(df_plot, soc_group=soc_group)

        # Create scatter plot for each tier
        for tier_name in tier_colors.keys():
            tier_data = filter_df(soc_data, tier_name=tier_name)

            # Scale bubble sizes using sqrt for better visibility
            sizes = np.sqrt(tier_data["usage_count"]) * 2

            ax.scatter(
                tier_data["ai_usage_index"],
                tier_data["soc_pct"],
                s=sizes,
                c=tier_colors[tier_name],
                alpha=0.6,
                edgecolors="black",
                linewidth=0.5,
                label=tier_name,
            )

        # Add trend line and regression statistics
        X = sm.add_constant(soc_data["ai_usage_index"].values)
        y = soc_data["soc_pct"].values

        model = sm.OLS(y, X)
        results = model.fit()

        intercept = results.params[0]
        slope = results.params[1]
        r_squared = results.rsquared
        p_value = results.pvalues[1]  # p-value for slope

        # Plot trend line
        x_line = np.linspace(
            soc_data["ai_usage_index"].min(), soc_data["ai_usage_index"].max(), 100
        )
        y_line = intercept + slope * x_line
        ax.plot(x_line, y_line, "--", color="gray", alpha=0.5, linewidth=1)

        # Format p-value display
        if p_value < 0.001:
            p_str = "p < 0.001"
        else:
            p_str = f"p = {p_value:.3f}"

        # Add regression statistics
        ax.text(
            0.95,
            0.95,
            f"$\\beta = {slope:.3f}\\ ({p_str})$\n$R^2 = {r_squared:.3f}$",
            transform=ax.transAxes,
            ha="right",
            va="top",
            fontsize=9,
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
        )

        # Format axes
        format_axis(
            ax,
            xlabel="Anthropic AI Usage Index (usage % / working-age population %)",
            ylabel="Occupation group share (%)",
            title=soc_group,
            xlabel_size=10,
            ylabel_size=10,
            grid=False,
        )
        ax.grid(True, alpha=0.3)

    # Add legend
    handles, labels = axes_flat[0].get_legend_handles_labels()
    if handles:
        # Create new handles with consistent size for legend only
        # This doesn't modify the actual plot markers
        legend_handles = []
        for handle in handles:
            # Get the color from the original handle
            color = (
                handle.get_facecolor()[0]
                if hasattr(handle, "get_facecolor")
                else "gray"
            )
            # Create a Line2D object with circle marker for legend
            new_handle = Line2D(
                [0],
                [0],
                marker="o",
                color="w",
                markerfacecolor=color,
                markersize=8,
                markeredgecolor="black",
                markeredgewidth=0.5,
                alpha=0.6,
            )
            legend_handles.append(new_handle)

        # Position tier legend centered under the left column with vertical layout
        fig.legend(
            legend_handles,
            labels,
            title="Anthropic AI Usage Index tier",
            loc="upper center",
            bbox_to_anchor=(0.25, -0.03),
            frameon=True,
            fancybox=True,
            shadow=True,
            ncol=2,
            borderpad=0.6,
        )

    # Add size legend using actual scatter points for perfect matching
    reference_counts = [100, 1000, 10000]

    # Create invisible scatter points with the exact same size formula as the plot
    size_legend_elements = []
    for count in reference_counts:
        # Use exact same formula as in the plot
        size = np.sqrt(count) * 2
        # Create scatter on first axis (will be invisible) just for legend
        scatter = axes_flat[0].scatter(
            [],
            [],  # Empty data
            s=size,
            c="gray",
            alpha=0.6,
            edgecolors="black",
            linewidth=0.5,
            label=f"{count:,}",
        )
        size_legend_elements.append(scatter)

    # Add size legend centered under the right column with vertical layout
    fig.legend(
        handles=size_legend_elements,
        title="Claude usage count",
        loc="upper center",
        bbox_to_anchor=(0.75, -0.03),
        frameon=True,
        fancybox=True,
        shadow=True,
        ncol=1,
        borderpad=0.6,
    )

    plt.tight_layout(rect=[0, -0.03, 1, 0.98])
    return fig


def collaboration_task_regression(df, geography="country"):
    """
    Analyze automation vs augmentation patterns controlling for task mix for
    geographies that meet the minimum observation threshold.

    Uses global task weights to calculate expected automation for each geography,
    then compares actual vs expected automation.

    Note: Includes "none" tasks in calculations since they have automation/augmentation
    patterns in the data. Excludes "not_classified" tasks which lack collaboration data.

    Args:
        df: Input dataframe
        geography: "country" or "state_us"
    """
    # Filter to geographies that meet min observation threshold
    filtered_countries, filtered_states = get_filtered_geographies(df)
    filtered_geos = filtered_countries if geography == "country" else filtered_states

    # Get collaboration automation data
    df_automation = filter_df(
        df,
        facet="collaboration_automation_augmentation",
        geography=geography,
        variable="automation_pct",
        geo_id=filtered_geos,
    )[["geo_id", "value"]].rename(columns={"value": "automation_pct"})

    # Get Anthropic AI Usage Index data
    df_usage = filter_df(
        df,
        geography=geography,
        facet=geography,
        variable="usage_per_capita_index",
        geo_id=filtered_geos,
    )[["geo_id", "geo_name", "value"]].copy()
    df_usage.rename(columns={"value": "usage_per_capita_index"}, inplace=True)

    # Get geography-specific task weights (percentages)
    df_geo_tasks = filter_df(
        df,
        facet="onet_task",
        geography=geography,
        variable="onet_task_pct",
        geo_id=filtered_geos,
    ).copy()

    # Exclude not_classified and none tasks
    df_geo_tasks = df_geo_tasks[
        ~df_geo_tasks["cluster_name"].isin(["not_classified", "none"])
    ]

    # Get global task-specific collaboration patterns (only available at global level)
    df_task_collab = filter_df(
        df,
        facet="onet_task::collaboration",
        geography="global",
        geo_id="GLOBAL",
        variable="onet_task_collaboration_pct",
    ).copy()

    # Parse task name and collaboration type from cluster_name
    df_task_collab["task_name"] = df_task_collab["cluster_name"].str.split("::").str[0]
    df_task_collab["collab_type"] = (
        df_task_collab["cluster_name"].str.split("::").str[1]
    )

    # Map collaboration types to automation/augmentation
    # Automation: directive, feedback loop
    # Augmentation: validation, task iteration, learning
    # Excluded: none, not_classified
    def is_automation(collab_type):
        if collab_type in ["directive", "feedback loop"]:
            return True
        elif collab_type in [
            "validation",
            "task iteration",
            "learning",
        ]:
            return False
        else:  # none, not_classified
            return None

    df_task_collab["is_automation"] = df_task_collab["collab_type"].apply(is_automation)

    # Exclude not_classified tasks upfront
    df_task_collab_valid = df_task_collab[
        df_task_collab["task_name"] != "not_classified"
    ]

    # Calculate automation percentage for each task
    task_automation_rates = {}
    for task_name in df_task_collab_valid["task_name"].unique():
        task_data = df_task_collab_valid[
            (df_task_collab_valid["task_name"] == task_name)
            & (df_task_collab_valid["is_automation"].notna())
        ]

        # Skip tasks that only have "not_classified" collaboration types
        if task_data.empty or task_data["value"].sum() == 0:
            continue

        automation_sum = task_data[task_data["is_automation"]]["value"].sum()
        total_sum = task_data["value"].sum()
        task_automation_rates[task_name] = (automation_sum / total_sum) * 100

    # Calculate expected automation for each country using its own task weights
    expected_automation = []
    geo_ids = []

    for geo_id in filtered_geos:
        # Get this geography's task distribution (excluding not_classified)
        geo_tasks = df_geo_tasks[
            (df_geo_tasks["geo_id"] == geo_id)
            & (df_geo_tasks["cluster_name"] != "not_classified")
        ]

        # Skip geographies with no task data
        if geo_tasks.empty:
            continue

        # Calculate weighted automation using geography's task weights
        weighted_auto = 0.0
        total_weight = 0.0

        for _, row in geo_tasks.iterrows():
            task = row["cluster_name"]
            weight = row["value"]  # Already in percentage

            # Get automation rate for this task (from global data)
            if task in task_automation_rates:
                auto_rate = task_automation_rates[task]
                weighted_auto += weight * auto_rate
                total_weight += weight

        # Calculate expected automation
        expected_auto = weighted_auto / total_weight
        expected_automation.append(expected_auto)
        geo_ids.append(geo_id)

    # Create dataframe with expected automation
    df_expected = pd.DataFrame(
        {"geo_id": geo_ids, "expected_automation_pct": expected_automation}
    )

    # Merge all data
    df_regression = df_automation.merge(df_expected, on="geo_id", how="inner")
    df_regression = df_regression.merge(df_usage, on="geo_id", how="inner")

    # Count unique tasks for reporting
    n_tasks = len(task_automation_rates)

    # Calculate residuals from regressions for proper partial correlation
    # For automation, regress actual on expected to get residuals
    X_expected = sm.add_constant(df_regression["expected_automation_pct"])
    model_automation = sm.OLS(df_regression["automation_pct"], X_expected)
    results_automation = model_automation.fit()
    df_regression["automation_residuals"] = results_automation.resid

    # For usage, regress on expected automation to get residuals
    model_usage = sm.OLS(df_regression["usage_per_capita_index"], X_expected)
    results_usage = model_usage.fit()
    df_regression["usage_residuals"] = results_usage.resid

    # Partial regression is regression of residuals
    # We want usage (X) to explain automation (Y)
    X_partial = sm.add_constant(df_regression["usage_residuals"])
    model_partial = sm.OLS(df_regression["automation_residuals"], X_partial)
    results_partial = model_partial.fit()
    partial_slope = results_partial.params.iloc[1]
    partial_r2 = results_partial.rsquared
    partial_p = results_partial.pvalues.iloc[1]

    # Create visualization - only show partial correlation
    fig, ax = create_figure(figsize=(10, 8))

    # Define colormap for automation residuals
    colors_automation = [AUGMENTATION_COLOR, AUTOMATION_COLOR]
    cmap_automation = LinearSegmentedColormap.from_list(
        "automation", colors_automation, N=100
    )

    # Plot partial correlation
    # Create colormap normalization for automation residuals
    norm = plt.Normalize(
        vmin=df_regression["automation_residuals"].min(),
        vmax=df_regression["automation_residuals"].max(),
    )

    # Plot invisible points to ensure matplotlib's autoscaling includes all data points
    ax.scatter(
        df_regression["usage_residuals"],
        df_regression["automation_residuals"],
        s=0,  # invisible points for autoscaling
        alpha=0,
    )

    # Plot country geo_id values as text instead of scatter points
    for _, row in df_regression.iterrows():
        color_val = norm(row["automation_residuals"])
        text_color = cmap_automation(color_val)

        ax.text(
            row["usage_residuals"],
            row["automation_residuals"],
            row["geo_id"],
            fontsize=7,
            ha="center",
            va="center",
            color=text_color,
            alpha=0.9,
            weight="bold",
        )

    # Create a ScalarMappable for the colorbar
    scalar_mappable = plt.cm.ScalarMappable(cmap=cmap_automation, norm=norm)
    scalar_mappable.set_array([])

    # Add regression line using actual regression results
    # OLS model: automation_residuals = intercept + slope * usage_residuals
    x_resid_line = np.linspace(
        df_regression["usage_residuals"].min(),
        df_regression["usage_residuals"].max(),
        100,
    )
    intercept = results_partial.params.iloc[0]
    y_resid_line = intercept + partial_slope * x_resid_line
    ax.plot(
        x_resid_line,
        y_resid_line,
        "grey",
        linestyle="--",
        linewidth=2,
        alpha=0.7,
    )

    # Set axis labels and title
    format_axis(
        ax,
        xlabel="Anthropic AI Usage Index residuals\n(per capita usage not explained by task mix)",
        ylabel="Automation % residuals\n(automation not explained by task mix)",
        title="Relationship between Anthropic AI Usage Index and automation",
        grid=False,
    )

    # Add correlation info inside the plot
    if partial_p < 0.001:
        p_str = "p < 0.001"
    else:
        p_str = f"p = {partial_p:.3f}"

    ax.text(
        0.08,
        0.975,
        f"Partial regression (controlling for task mix): $\\beta = {partial_slope:.3f}, R^2 = {partial_r2:.3f}\\ ({p_str})$",
        transform=ax.transAxes,
        fontsize=10,
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
        verticalalignment="top",
    )

    ax.axhline(y=0, color="gray", linestyle=":", linewidth=1, alpha=0.3)
    ax.axvline(x=0, color="gray", linestyle=":", linewidth=1, alpha=0.3)
    ax.grid(True, alpha=0.3, linestyle="--")

    # Add colorbar
    fig.subplots_adjust(right=0.92)
    cbar_ax = fig.add_axes([0.94, 0.2, 0.02, 0.6])
    cbar = plt.colorbar(scalar_mappable, cax=cbar_ax)
    cbar.set_label("Automation % residuals", fontsize=10, rotation=270, labelpad=15)

    # Adjust plot to make room for titles and ensure all data is visible
    plt.subplots_adjust(top=0.92, right=0.92, left=0.12, bottom=0.12)

    # Return results
    return {
        "figure": fig,
        "partial_slope": partial_slope,
        "partial_r2": partial_r2,
        "partial_pvalue": partial_p,
        "n_countries": len(df_regression),
        "n_tasks": n_tasks,
        "df_residuals": df_regression,
    }


def plot_automation_preference_residuals(df, geography="country", figsize=(14, 12)):
    """Plot automation vs augmentation preference after controlling for task mix.

    For geographies meeting minimum observation threshold only.

    Args:
        df: Input dataframe
        geography: "country" or "state_us"
        figsize: Figure size
    """
    # First run the collaboration analysis to get residuals
    results = collaboration_task_regression(df, geography=geography)

    # Suppress figure created by collaboration_task_regression
    plt.close(results["figure"])

    # Get the dataframe with residuals
    df_residuals = results["df_residuals"]

    # Sort by automation residuals (most augmentation to most automation)
    df_plot = df_residuals.sort_values("automation_residuals", ascending=True)

    # Adjust figure size based on number of geographies
    n_geos = len(df_plot)
    fig_height = max(8, n_geos * 0.25)
    fig, ax = create_figure(figsize=(figsize[0], fig_height))

    # Create color map
    colors = [
        AUGMENTATION_COLOR if x < 0 else AUTOMATION_COLOR
        for x in df_plot["automation_residuals"]
    ]

    # Create horizontal bar chart
    ax.barh(
        range(len(df_plot)),
        df_plot["automation_residuals"].values,
        color=colors,
        alpha=0.8,
    )

    # Set y-axis labels with geography names only
    y_labels = [row["geo_name"] for _, row in df_plot.iterrows()]
    ax.set_yticks(range(len(df_plot)))
    ax.set_yticklabels(y_labels, fontsize=7)

    # Reduce white space at top and bottom
    ax.set_ylim(-0.5, len(df_plot) - 0.5)

    # Add vertical line at zero
    ax.axvline(x=0, color="black", linestyle="-", linewidth=1, alpha=0.7)

    # Labels and title
    geo_label = "Countries'" if geography == "country" else "States'"
    format_axis(
        ax,
        xlabel="Automation % residual (after controlling for task mix)",
        ylabel="",
        title=f"{geo_label} automation vs augmentation preference\n(after controlling for task composition)",
        grid=False,
    )

    # Add grid
    ax.grid(True, axis="x", alpha=0.3, linestyle="--")

    # Add value labels on the bars
    for i, (_, row) in enumerate(df_plot.iterrows()):
        value = row["automation_residuals"]
        x_offset = 0.2 if abs(value) < 5 else 0.3
        x_pos = value + (x_offset if value > 0 else -x_offset)
        ax.text(
            x_pos,
            i,
            f"{value:.1f}",
            ha="left" if value > 0 else "right",
            va="center",
            fontsize=8,
        )

    # Add annotations
    y_range = ax.get_ylim()
    annotation_y = y_range[1] * 0.85

    # Left annotation for augmentation
    ax.text(
        ax.get_xlim()[0] * 0.7,
        annotation_y,
        "Prefer augmentation",
        fontsize=9,
        color=AUGMENTATION_COLOR,
        fontweight="bold",
        ha="left",
        va="center",
    )

    # Right annotation for automation
    ax.text(
        ax.get_xlim()[1] * 0.7,
        annotation_y,
        "Prefer automation",
        fontsize=9,
        color=AUTOMATION_COLOR,
        fontweight="bold",
        ha="right",
        va="center",
    )

    plt.tight_layout()

    return fig


def plot_soc_distribution(
    df, geo_list, geography, figsize=(14, 10), title=None, exclude_not_classified=True
):
    """
    Plot SOC occupation distribution for multiple geographies (countries or states) with horizontal bars, colored by tier.

    Args:
        df: Long format dataframe
        geo_list: List of geo_id values to compare (e.g., ['USA', 'BRA'] for countries or ['CA', 'TX'] for states)
        geography: Geographic level ('country' or 'state_us')
        figsize: Figure size
        title: Chart title
        exclude_not_classified: If True, excludes 'not_classified' from the chart
    """
    # Use global tier colors and names
    tier_colors = TIER_COLORS_NUMERIC
    tier_names = TIER_NAMES_NUMERIC

    # Get usage tier and geo_name for each geography
    tier_data = filter_df(
        df, geography=geography, variable="usage_tier", facet=geography, geo_id=geo_list
    )[["geo_id", "geo_name", "value"]].rename(columns={"value": "tier"})

    # Collect SOC data for all geographies first to determine consistent ordering
    all_soc_data = []
    for geo_id in geo_list:
        geo_soc = filter_df(
            df,
            geography=geography,
            geo_id=geo_id,
            facet="soc_occupation",
            variable="soc_pct",
        ).copy()

        if not geo_soc.empty:
            # Optionally filter out not_classified
            if exclude_not_classified:
                geo_soc = geo_soc[geo_soc["cluster_name"] != "not_classified"].copy()

            geo_soc["geo"] = geo_id
            all_soc_data.append(geo_soc)

    combined_data = pd.concat(all_soc_data)

    # Use global SOC distribution for countries, USA distribution for states
    if geography == "country":
        reference_data = filter_df(
            df,
            geography="global",
            geo_id="GLOBAL",
            facet="soc_occupation",
            variable="soc_pct",
        )
    else:  # state_us
        reference_data = filter_df(
            df,
            geography="country",
            geo_id="USA",
            facet="soc_occupation",
            variable="soc_pct",
        )

    # Filter out not_classified from reference data if needed
    if exclude_not_classified:
        reference_data = reference_data[
            reference_data["cluster_name"] != "not_classified"
        ]

    # Sort by reference values ascending so highest appears at top when plotted
    soc_order = reference_data.sort_values("value", ascending=True)[
        "cluster_name"
    ].tolist()

    # Create figure
    fig, ax = create_figure(figsize=figsize)

    # Width of bars and positions
    n_geos = len(geo_list)
    bar_width = 0.95 / n_geos  # Wider bars, less spacing within groups
    y_positions = (
        np.arange(len(soc_order)) * 1.05
    )  # Reduce spacing between SOC groups to 5%

    # Sort geo_list to ensure highest tier appears at top within each group
    # Reverse the order so tier 4 is plotted first and appears on top
    geo_tier_map = dict(zip(tier_data["geo_id"], tier_data["tier"], strict=True))
    geo_list_sorted = sorted(geo_list, key=lambda x: geo_tier_map[x])

    # Plot bars for each geography
    for i, geo_id in enumerate(geo_list_sorted):
        geo_data = filter_df(combined_data, geo=geo_id)
        geo_name = filter_df(tier_data, geo_id=geo_id)["geo_name"].iloc[0]
        geo_tier = filter_df(tier_data, geo_id=geo_id)["tier"].iloc[0]

        # Get values in the right order
        values = []
        for soc in soc_order:
            val_data = filter_df(geo_data, cluster_name=soc)["value"]
            # Use NaN for missing data
            values.append(val_data.iloc[0] if not val_data.empty else float("nan"))

        # Determine color based on tier
        color = tier_colors[int(geo_tier)]

        # Create bars with offset for multiple geographies
        # Reverse the offset calculation so first geo (lowest tier) goes to bottom
        offset = ((n_geos - 1 - i) - n_geos / 2 + 0.5) * bar_width

        # Get tier name for label
        tier_label = tier_names[int(geo_tier)]
        label_text = f"{geo_name} ({tier_label})"

        bars = ax.barh(
            y_positions + offset,
            values,
            bar_width,
            label=label_text,
            color=color,
            alpha=0.8,
        )

        # Add value labels for bars with data
        for bar, value in zip(bars, values, strict=True):
            if not pd.isna(value):
                ax.text(
                    value + 0.1,
                    bar.get_y() + bar.get_height() / 2,
                    f"{value:.1f}%",
                    va="center",
                    fontsize=5,
                )

    # Set y-axis labels - position them at the center of each SOC group
    ax.set_yticks(y_positions)
    ax.set_yticklabels(soc_order, fontsize=9, va="center")

    # Reduce white space at top and bottom
    ax.set_ylim(y_positions[0] - 0.5, y_positions[-1] + 0.5)

    # Customize plot
    format_axis(
        ax,
        xlabel="Share of Claude task usage (%)",
        ylabel="Standard Occupation Classification group",
        grid=False,
    )

    if title is None:
        title = "Claude task usage by occupation: Comparison by AI usage tier"
    format_axis(ax, title=title, title_size=14, grid=False)

    # Add legend
    ax.legend(loc="lower right", fontsize=10, framealpha=0.95)

    # Grid
    ax.grid(True, axis="x", alpha=0.3, linestyle="--")
    ax.set_xlim(0, max(combined_data["value"]) * 1.15)

    plt.tight_layout()
    return fig
