"""Biểu đồ của bước 4. Chỉ vẽ danh mục gộp nhiều mã, không vẽ từng mã."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import ScalarFormatter

SURFACE = "#fcfcfb"
TEXT = "#0b0b0b"
TEXT_MUTED = "#52514e"
GRID = "#e4e3df"
BLUE = "#2a78d6"
ORANGE = "#eb6834"
MIDDLE_QUINTILE = "#c3c2b7"
Z_95 = 1.96
SPEC_STYLE = {
    "raw": (BLUE, "o", "Xếp chung cả rổ"),
    "neutral": (ORANGE, "s", "Xếp trong từng mẫu BCTC"),
}


def _style(ax: plt.Axes) -> None:
    ax.set_facecolor(SURFACE)
    ax.tick_params(colors=TEXT_MUTED, labelsize=8, length=0)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(GRID)


def plot_spreads(summary: pd.DataFrame, path: Path) -> None:
    """Spread Q5-Q1 của từng factor, kèm khoảng tin cậy 95% theo Newey-West."""

    data = summary[summary["window"] == "full"]
    factors = list(dict.fromkeys(data["factor"]))
    fig, ax = plt.subplots(figsize=(8, 8.5), facecolor=SURFACE)
    _style(ax)
    for offset, (spec, (color, marker, label)) in zip((-0.17, 0.17), SPEC_STYLE.items()):
        rows = data[data["spec"] == spec].set_index("factor").loc[factors]
        half_width = Z_95 * (rows["spread_pct_m"] / rows["spread_t_nw"]).abs()
        y = [i + offset for i in range(len(factors))]
        ax.errorbar(rows["spread_pct_m"], y, xerr=half_width, fmt=marker, color=color,
                    markersize=5, elinewidth=1.5, capsize=0, label=label)
    ax.axvline(0, color=TEXT_MUTED, linewidth=1)
    ax.set_yticks(range(len(factors)), factors, color=TEXT)
    ax.invert_yaxis()
    ax.grid(axis="x", color=GRID, linewidth=0.7)
    ax.set_axisbelow(True)
    ax.set_xlabel("Spread Q5 − Q1, %/tháng (số dương: factor đúng hướng kỳ vọng)", color=TEXT_MUTED, fontsize=9)
    ax.set_title("Spread long-short theo factor, khoảng tin cậy 95% (Newey-West)",
                 loc="left", color=TEXT, fontsize=11)
    ax.legend(frameon=False, fontsize=9, loc="upper center", bbox_to_anchor=(0.5, -0.06), ncol=2)
    fig.tight_layout()
    fig.savefig(path, dpi=160, facecolor=SURFACE)
    plt.close(fig)


def plot_cumulative(all_series: dict, path: Path, spec: str = "neutral") -> None:
    """Giá trị tích lũy của 1 đồng trong từng nhóm, mỗi factor một ô, trục log chung."""

    factors = [factor for factor, s in all_series if s == spec]
    n_cols = 4
    n_rows = -(-len(factors) // n_cols)
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(12, 2.25 * n_rows + 0.8), sharex=True,
                             sharey=True, facecolor=SURFACE)
    axes = axes.ravel()
    for ax, factor in zip(axes, factors):
        _style(ax)
        series = all_series[(factor, spec)]
        for q, color, width in ((2, MIDDLE_QUINTILE, 1), (3, MIDDLE_QUINTILE, 1), (4, MIDDLE_QUINTILE, 1),
                                (1, ORANGE, 2), (5, BLUE, 2)):
            ax.plot(series.index, (1 + series[f"q{q}"].fillna(0)).cumprod(), color=color, linewidth=width)
        ax.axhline(1, color=GRID, linewidth=0.7, zorder=0)
        ax.set_yscale("log")
        ax.set_title(factor, loc="left", color=TEXT, fontsize=9)
    for ax in axes[len(factors):]:
        ax.set_visible(False)
    # Ô cuối mỗi cột còn hiện phải có nhãn năm, kể cả khi hàng cuối không đủ ô.
    for ax in axes[max(len(factors) - n_cols, 0):len(factors)]:
        ax.tick_params(labelbottom=True)
    axes[0].yaxis.set_major_formatter(ScalarFormatter())
    axes[0].set_yticks([1, 2, 4, 8])
    axes[0].minorticks_off()
    handles = [
        plt.Line2D([], [], color=BLUE, linewidth=2, label="Q5 (kỳ vọng cao)"),
        plt.Line2D([], [], color=MIDDLE_QUINTILE, linewidth=1, label="Q2–Q4"),
        plt.Line2D([], [], color=ORANGE, linewidth=2, label="Q1 (kỳ vọng thấp)"),
    ]
    fig.legend(handles=handles, frameon=False, fontsize=9, loc="lower center", ncol=3)
    fig.suptitle("Giá trị tích lũy của 1 đồng theo quintile, trước chi phí, xếp trong từng mẫu BCTC",
                 x=0.01, ha="left", color=TEXT, fontsize=11)
    fig.tight_layout(rect=(0, 0.03, 1, 0.98))
    fig.savefig(path, dpi=160, facecolor=SURFACE)
    plt.close(fig)
