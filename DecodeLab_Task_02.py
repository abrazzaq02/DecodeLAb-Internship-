"""
================================================================================
 AI DATA CLASSIFICATION SYSTEM  |  DecodeLabs Project 2
================================================================================
A professional, single-file desktop AI application demonstrating supervised
machine learning and data classification using the Iris dataset.

Features
--------
- Dataset loading, inspection, and exploration (searchable table + stats)
- Train/Test split with configurable test size
- Decision Tree and Random Forest classifiers
- Accuracy evaluation, classification report, confusion matrix
- Matplotlib-powered visualization center embedded in the dashboard
- Real-time prediction lab with confidence scores and class explanations
- Export results to CSV, save/load trained model to .pkl
- Modern dark "glassmorphism-inspired" dashboard UI built on Tkinter/ttk,
  using ttkbootstrap when available (falls back gracefully if not installed)
- Animated progress bar, fade-in startup, hover/glow effects on buttons,
  sliding sidebar navigation, animated card entrance effects

Author: DecodeLabs Project 2 Submission
Tech Stack: Python, Tkinter, Scikit-Learn, Pandas, NumPy, Matplotlib,
            ttkbootstrap (optional, recommended for best visuals)

Run:
    python ai_classification_system.py

Dependencies:
    pip install scikit-learn pandas numpy matplotlib ttkbootstrap
    (ttkbootstrap is optional - the app degrades gracefully without it)
================================================================================
"""

import os
import sys
import threading
import traceback
import pickle
from datetime import datetime

import numpy as np
import pandas as pd

import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# ttkbootstrap gives us modern flat dark widgets out of the box.
# If it isn't installed, we fall back to plain ttk + manual dark styling
# so the application still runs everywhere.
TTKBOOTSTRAP_AVAILABLE = True
try:
    import ttkbootstrap as tb
    from ttkbootstrap.constants import *
except ImportError:
    TTKBOOTSTRAP_AVAILABLE = False
    tb = None

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)
from sklearn.preprocessing import StandardScaler


# ==============================================================================
# THEME / DESIGN CONSTANTS
# ==============================================================================
class Theme:
    """Central color palette & style constants (single source of truth)."""

    BG = "#0B1120"            # App background
    BG_SECONDARY = "#101827"  # Slightly lighter panel background
    CARD_BG = "#141C2E"       # "Glass" card background
    CARD_BORDER = "#1E293B"   # Card border / divider
    SIDEBAR_BG = "#0D1424"

    PRIMARY = "#2563EB"
    SECONDARY = "#7C3AED"
    ACCENT = "#06B6D4"
    SUCCESS = "#10B981"
    WARNING = "#F59E0B"
    DANGER = "#EF4444"

    TEXT = "#F8FAFC"
    TEXT_MUTED = "#94A3B8"
    TEXT_FAINT = "#64748B"

    FONT_FAMILY = "Segoe UI"
    FONT_FAMILY_MONO = "Consolas"

    # Gradient-esque pairs used for "neon" accents on canvases (since Tkinter
    # has no native CSS gradients, we approximate with layered colors)
    GRADIENT_PRIMARY = ("#2563EB", "#06B6D4")
    GRADIENT_SECONDARY = ("#7C3AED", "#2563EB")
    GRADIENT_SUCCESS = ("#10B981", "#06B6D4")

    RADIUS = 16  # conceptual corner radius used by rounded-canvas helpers


# Matplotlib dark style tuned to the same palette, used by every chart.
plt.rcParams.update({
    "figure.facecolor": Theme.CARD_BG,
    "axes.facecolor": Theme.CARD_BG,
    "axes.edgecolor": Theme.CARD_BORDER,
    "axes.labelcolor": Theme.TEXT,
    "xtick.color": Theme.TEXT_MUTED,
    "ytick.color": Theme.TEXT_MUTED,
    "text.color": Theme.TEXT,
    "axes.titlecolor": Theme.TEXT,
    "grid.color": Theme.CARD_BORDER,
    "font.family": "sans-serif",
})


# ==============================================================================
# REUSABLE UI WIDGETS  (rounded "glass" cards, gradient buttons, etc.)
# ==============================================================================
class RoundedCard(tk.Canvas):
    """
    A canvas-drawn rounded rectangle "glass card" container.
    Tkinter has no native rounded-corner frame, so we draw one on a Canvas
    and place a regular Frame on top of it for content - this is the closest
    practical approximation of a glassmorphism panel in pure Tkinter.
    """

    def __init__(self, parent, width=300, height=160, radius=18,
                 bg=Theme.CARD_BG, border=Theme.CARD_BORDER, border_width=1,
                 **kwargs):
        super().__init__(parent, width=width, height=height,
                          bg=parent["bg"] if isinstance(parent, (tk.Frame, tk.Canvas)) else Theme.BG,
                          highlightthickness=0, **kwargs)
        self.radius = radius
        self.card_bg = bg
        self.border_color = border
        self.border_width = border_width
        self._width = width
        self._height = height
        self.inner = tk.Frame(self, bg=bg)
        self.bind("<Configure>", self._on_resize)
        self._draw()
        # place inner frame with small padding so the rounded border shows
        self.inner.place(x=border_width + 2, y=border_width + 2,
                          width=width - 2 * (border_width + 2),
                          height=height - 2 * (border_width + 2))

    def _draw(self):
        self.delete("card")
        w, h, r = self._width, self._height, self.radius
        self._round_rect(2, 2, w - 2, h - 2, r,
                          fill=self.card_bg, outline=self.border_color,
                          width=self.border_width, tags="card")
        self.tag_lower("card")

    def _round_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = [
            x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
            x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
            x1, y2, x1, y2 - r, x1, y1 + r, x1, y1,
        ]
        return self.create_polygon(points, smooth=True, **kwargs)

    def _on_resize(self, event):
        self._width = max(event.width, 10)
        self._height = max(event.height, 10)
        self._draw()
        self.inner.place(x=self.border_width + 2, y=self.border_width + 2,
                          width=self._width - 2 * (self.border_width + 2),
                          height=self._height - 2 * (self.border_width + 2))


class GlowButton(tk.Canvas):
    """
    A modern rounded button with a gradient-ish fill, hover "glow" effect,
    and a smooth scale animation on hover - approximating the requested
    neon hover / gradient / glow button design using only Tkinter primitives.
    """

    def __init__(self, parent, text="Button", command=None, width=180, height=44,
                 color1=Theme.PRIMARY, color2=Theme.ACCENT, text_color=Theme.TEXT,
                 font_size=11, icon="", radius=12, disabled=False):
        bgc = parent["bg"] if isinstance(parent, (tk.Frame, tk.Canvas)) else Theme.BG
        super().__init__(parent, width=width, height=height, bg=bgc,
                          highlightthickness=0, cursor="hand2" if not disabled else "arrow")
        self.command = command
        self.color1 = color1
        self.color2 = color2
        self.text_color = text_color
        self.label = (icon + "  " + text).strip() if icon else text
        self.font_size = font_size
        self.radius = radius
        self.w = width
        self.h = height
        self._scale = 1.0
        self._disabled = disabled
        self._hover = False
        self._draw()
        if not disabled:
            self.bind("<Enter>", self._on_enter)
            self.bind("<Leave>", self._on_leave)
            self.bind("<Button-1>", self._on_click)

    def set_disabled(self, disabled: bool):
        self._disabled = disabled
        self.config(cursor="arrow" if disabled else "hand2")
        self._draw()

    def _blend(self, c1, c2, t):
        """Linear-interpolate two hex colors for a fake gradient strip."""
        c1 = c1.lstrip("#")
        c2 = c2.lstrip("#")
        r1, g1, b1 = int(c1[0:2], 16), int(c1[2:4], 16), int(c1[4:6], 16)
        r2, g2, b2 = int(c2[0:2], 16), int(c2[2:4], 16), int(c2[4:6], 16)
        r = int(r1 + (r2 - r1) * t)
        g = int(g1 + (g2 - g1) * t)
        b = int(b1 + (b2 - b1) * t)
        return f"#{r:02x}{g:02x}{b:02x}"

    def _round_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = [
            x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
            x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
            x1, y2, x1, y2 - r, x1, y1 + r, x1, y1,
        ]
        return self.create_polygon(points, smooth=True, **kwargs)

    def _draw(self):
        self.delete("all")
        pad = 3 if self._hover else 0
        x1, y1, x2, y2 = pad, pad, self.w - pad, self.h - pad

        if self._disabled:
            self._round_rect(x1, y1, x2, y2, self.radius,
                              fill=Theme.CARD_BORDER, outline="")
            self.create_text(self.w / 2, self.h / 2, text=self.label,
                              fill=Theme.TEXT_FAINT,
                              font=(Theme.FONT_FAMILY, self.font_size, "bold"))
            return

        # Glow halo when hovered (drawn as soft outer rectangles)
        if self._hover:
            for i, alpha_color in enumerate([self.color2]):
                glow_pad = 6 - i * 2
                self._round_rect(x1 - glow_pad, y1 - glow_pad, x2 + glow_pad, y2 + glow_pad,
                                  self.radius + 4, fill="", outline=self.color2)

        # Fake gradient: draw N thin vertical strips blending color1 -> color2
        strips = 24
        strip_w = (x2 - x1) / strips
        for i in range(strips):
            t = i / (strips - 1)
            color = self._blend(self.color1, self.color2, t)
            sx1 = x1 + i * strip_w
            sx2 = sx1 + strip_w + 1
            self.create_rectangle(sx1, y1, sx2, y2, fill=color, outline="")

        # Re-mask corners to round them off (draw background-colored corner triangles)
        bg = self["bg"]
        corner = self.radius
        self.create_arc(x1, y1, x1 + 2 * corner, y1 + 2 * corner, start=90, extent=90,
                         style="pieslice", fill=bg, outline=bg)
        self.create_arc(x2 - 2 * corner, y1, x2, y1 + 2 * corner, start=0, extent=90,
                         style="pieslice", fill=bg, outline=bg)
        self.create_arc(x1, y2 - 2 * corner, x1 + 2 * corner, y2, start=180, extent=90,
                         style="pieslice", fill=bg, outline=bg)
        self.create_arc(x2 - 2 * corner, y2 - 2 * corner, x2, y2, start=270, extent=90,
                         style="pieslice", fill=bg, outline=bg)
        # redraw rounded border on top for a crisp edge
        self._round_rect(x1, y1, x2, y2, self.radius, fill="", outline=self.color2 if self._hover else "")

        self.create_text(self.w / 2, self.h / 2, text=self.label,
                          fill=self.text_color,
                          font=(Theme.FONT_FAMILY, self.font_size, "bold"))

    def _on_enter(self, event):
        if self._disabled:
            return
        self._hover = True
        self._draw()

    def _on_leave(self, event):
        if self._disabled:
            return
        self._hover = False
        self._draw()

    def _on_click(self, event):
        if self._disabled or self.command is None:
            return
        self._flash_then_call()

    def _flash_then_call(self):
        # quick visual "press" feedback
        self.delete("flash")
        self.create_rectangle(0, 0, self.w, self.h, fill=Theme.TEXT, stipple="gray25", tags="flash")
        self.after(80, lambda: (self.delete("flash"), self.command()))


class AnimatedProgressBar(tk.Canvas):
    """A smooth animated gradient progress bar used during model training."""

    def __init__(self, parent, width=400, height=14, radius=7):
        bgc = parent["bg"] if isinstance(parent, (tk.Frame, tk.Canvas)) else Theme.BG
        super().__init__(parent, width=width, height=height, bg=bgc, highlightthickness=0)
        self.w = width
        self.h = height
        self.radius = radius
        self.progress = 0.0  # 0..1
        self._draw_track()

    def _round_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = [
            x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
            x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
            x1, y2, x1, y2 - r, x1, y1 + r, x1, y1,
        ]
        return self.create_polygon(points, smooth=True, **kwargs)

    def _draw_track(self):
        self.delete("track")
        self._round_rect(0, 0, self.w, self.h, self.radius,
                          fill=Theme.CARD_BORDER, outline="", tags="track")
        self.tag_lower("track")

    def set_progress(self, value):
        """value: 0..1"""
        self.progress = max(0.0, min(1.0, value))
        self.delete("fill")
        fill_w = int(self.w * self.progress)
        if fill_w > 2:
            strips = max(2, fill_w // 4)
            for i in range(strips):
                t = i / max(1, strips - 1)
                c1 = Theme.PRIMARY.lstrip("#")
                c2 = Theme.ACCENT.lstrip("#")
                r1, g1, b1 = int(c1[0:2], 16), int(c1[2:4], 16), int(c1[4:6], 16)
                r2, g2, b2 = int(c2[0:2], 16), int(c2[2:4], 16), int(c2[4:6], 16)
                r = int(r1 + (r2 - r1) * t)
                g = int(g1 + (g2 - g1) * t)
                b = int(b1 + (b2 - b1) * t)
                color = f"#{r:02x}{g:02x}{b:02x}"
                sx1 = i * (fill_w / strips)
                sx2 = sx1 + (fill_w / strips) + 1
                self.create_rectangle(sx1, 0, sx2, self.h, fill=color, outline="", tags="fill")
        self.update_idletasks()

    def animate_to(self, target, duration_ms=900, steps=30, on_complete=None):
        """Animate progress smoothly from current value to target."""
        start = self.progress
        delta = target - start
        if steps <= 0:
            steps = 1
        interval = max(1, duration_ms // steps)

        def step(i=0):
            if i > steps:
                if on_complete:
                    on_complete()
                return
            t = i / steps
            # ease-out cubic for a "smooth micro-interaction" feel
            eased = 1 - (1 - t) ** 3
            self.set_progress(start + delta * eased)
            self.after(interval, lambda: step(i + 1))

        step()


class StatCard(RoundedCard):
    """Dashboard statistic card: big number + label + small icon glyph."""

    def __init__(self, parent, title, value, icon="", color=Theme.PRIMARY,
                 width=220, height=120):
        super().__init__(parent, width=width, height=height, bg=Theme.CARD_BG)
        self.color_accent = color
        top = tk.Frame(self.inner, bg=Theme.CARD_BG)
        top.pack(fill="x", padx=16, pady=(14, 0))

        icon_lbl = tk.Label(top, text=icon, font=(Theme.FONT_FAMILY, 18),
                             bg=Theme.CARD_BG, fg=color)
        icon_lbl.pack(side="left")

        title_lbl = tk.Label(top, text=title.upper(), font=(Theme.FONT_FAMILY, 9, "bold"),
                              bg=Theme.CARD_BG, fg=Theme.TEXT_MUTED)
        title_lbl.pack(side="left", padx=(8, 0))

        self.value_var = tk.StringVar(value=str(value))
        self.value_lbl = tk.Label(self.inner, textvariable=self.value_var,
                                   font=(Theme.FONT_FAMILY, 26, "bold"),
                                   bg=Theme.CARD_BG, fg=Theme.TEXT)
        self.value_lbl.pack(anchor="w", padx=16, pady=(8, 14))

        # thin accent underline for a touch of "neon" detailing
        underline = tk.Frame(self.inner, bg=color, height=3)
        underline.pack(fill="x", padx=16, side="bottom", pady=(0, 0))

    def set_value(self, value):
        self.value_var.set(str(value))


def fade_in(widget, root, duration_ms=400, steps=12):
    """
    Note: kept as a documented no-op hook. The application's real startup
    fade-in is implemented via window-level alpha animation in
    AIClassificationApp._animate_startup, since per-widget alpha blending
    is not supported by native Tkinter widgets.
    """
    return


# ==============================================================================
# MACHINE LEARNING ENGINE  (data + model logic, fully decoupled from the UI)
# ==============================================================================
class ClassificationEngine:
    """
    Encapsulates the entire ML pipeline: dataset loading, preprocessing,
    train/test splitting, model training (Decision Tree / Random Forest),
    evaluation, and single-sample prediction.

    Kept independent of any GUI code so it could be unit-tested or reused
    in a CLI / API context - a core requirement of clean, scalable,
    production-ready architecture.
    """

    MODEL_REGISTRY = {
        "Decision Tree": DecisionTreeClassifier,
        "Random Forest": RandomForestClassifier,
    }

    def __init__(self):
        self.raw_bunch = None
        self.dataframe: pd.DataFrame | None = None
        self.feature_names = []
        self.target_names = []

        self.X_train = self.X_test = self.y_train = self.y_test = None
        self.scaler = StandardScaler()
        self.is_scaled = False

        self.models = {}            # name -> fitted model
        self.results = {}           # name -> metrics dict
        self.active_model_name = None
        self.test_size = 0.2
        self.random_state = 42

    # ---------------------------------------------------------------- load --
    def load_iris_dataset(self):
        """Load the classic Iris dataset via scikit-learn and build a DataFrame."""
        self.raw_bunch = load_iris()
        self.feature_names = [str(f) for f in self.raw_bunch.feature_names]
        self.target_names = [str(t) for t in self.raw_bunch.target_names]

        df = pd.DataFrame(self.raw_bunch.data, columns=self.feature_names)
        df["target"] = self.raw_bunch.target
        df["species"] = df["target"].apply(lambda i: self.target_names[i])
        self.dataframe = df
        return df

    def dataset_summary(self) -> dict:
        """Return high-level dataset info for the dashboard stat cards."""
        if self.dataframe is None:
            return {}
        df = self.dataframe
        return {
            "total_samples": len(df),
            "total_features": len(self.feature_names),
            "num_classes": len(self.target_names),
            "class_names": self.target_names,
            "class_distribution": df["species"].value_counts().to_dict(),
            "missing_values": int(df[self.feature_names].isnull().sum().sum()),
        }

    def feature_statistics(self) -> pd.DataFrame:
        """Descriptive statistics (mean, std, min, max, etc.) per feature."""
        if self.dataframe is None:
            return pd.DataFrame()
        return self.dataframe[self.feature_names].describe().round(3)

    # ------------------------------------------------------------- split --
    def split_data(self, test_size=0.2, random_state=42, scale=True):
        """Split into train/test sets and optionally standardize features."""
        if self.dataframe is None:
            raise ValueError("Dataset not loaded. Call load_iris_dataset() first.")

        X = self.dataframe[self.feature_names].values
        y = self.dataframe["target"].values

        self.test_size = test_size
        self.random_state = random_state

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )

        if scale:
            X_train = self.scaler.fit_transform(X_train)
            X_test = self.scaler.transform(X_test)
            self.is_scaled = True
        else:
            self.is_scaled = False

        self.X_train, self.X_test = X_train, X_test
        self.y_train, self.y_test = y_train, y_test
        return X_train, X_test, y_train, y_test

    # ----------------------------------------------------------- training --
    def train_model(self, model_name: str, **hyperparams):
        """
        Train a classifier by name ('Decision Tree' or 'Random Forest').
        Returns the fitted model and a metrics dictionary.
        """
        if self.X_train is None:
            raise ValueError("Data not split yet. Call split_data() first.")
        if model_name not in self.MODEL_REGISTRY:
            raise ValueError(f"Unknown model: {model_name}")

        model_cls = self.MODEL_REGISTRY[model_name]
        default_params = {"random_state": self.random_state}
        default_params.update(hyperparams)
        model = model_cls(**default_params)

        model.fit(self.X_train, self.y_train)
        predictions = model.predict(self.X_test)

        accuracy = accuracy_score(self.y_test, predictions)
        report = classification_report(
            self.y_test, predictions, target_names=self.target_names,
            output_dict=True, zero_division=0
        )
        report_text = classification_report(
            self.y_test, predictions, target_names=self.target_names,
            zero_division=0
        )
        cm = confusion_matrix(self.y_test, predictions)

        self.models[model_name] = model
        self.results[model_name] = {
            "accuracy": accuracy,
            "report_dict": report,
            "report_text": report_text,
            "confusion_matrix": cm,
            "predictions": predictions,
            "trained_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        self.active_model_name = model_name
        return model, self.results[model_name]

    def get_feature_importance(self, model_name: str):
        """Return feature importances if the model supports them."""
        model = self.models.get(model_name)
        if model is None or not hasattr(model, "feature_importances_"):
            return None
        return dict(zip(self.feature_names, model.feature_importances_))

    # ---------------------------------------------------------- prediction --
    def predict_single(self, model_name: str, feature_values: list):
        """
        Predict the class for a single sample (list of 4 feature values).
        Returns (predicted_class_name, confidence_score, probability_dict).
        """
        model = self.models.get(model_name)
        if model is None:
            raise ValueError(f"Model '{model_name}' has not been trained yet.")

        sample = np.array(feature_values).reshape(1, -1)
        if self.is_scaled:
            sample = self.scaler.transform(sample)

        pred_idx = model.predict(sample)[0]
        pred_class = self.target_names[pred_idx]

        proba_dict = {}
        confidence = None
        if hasattr(model, "predict_proba"):
            probs = model.predict_proba(sample)[0]
            proba_dict = {self.target_names[i]: float(p) for i, p in enumerate(probs)}
            confidence = float(probs[pred_idx])

        return pred_class, confidence, proba_dict

    # ------------------------------------------------------------- export --
    def export_results_csv(self, model_name: str, filepath: str):
        """Export predictions vs actual values (for the test set) to CSV."""
        if model_name not in self.results:
            raise ValueError(f"No results available for '{model_name}'.")

        res = self.results[model_name]
        df_out = pd.DataFrame(self.X_test, columns=self.feature_names)
        if self.is_scaled:
            # reverse-transform for human-readable export
            df_out = pd.DataFrame(self.scaler.inverse_transform(self.X_test),
                                   columns=self.feature_names)
        df_out["actual_class"] = [self.target_names[i] for i in self.y_test]
        df_out["predicted_class"] = [self.target_names[i] for i in res["predictions"]]
        df_out["correct"] = df_out["actual_class"] == df_out["predicted_class"]
        df_out.to_csv(filepath, index=False)
        return filepath

    def save_model(self, model_name: str, filepath: str):
        """Persist a trained model (plus the scaler) to a .pkl file."""
        if model_name not in self.models:
            raise ValueError(f"Model '{model_name}' has not been trained yet.")
        payload = {
            "model": self.models[model_name],
            "scaler": self.scaler if self.is_scaled else None,
            "feature_names": self.feature_names,
            "target_names": self.target_names,
            "model_name": model_name,
            "is_scaled": self.is_scaled,
            "saved_at": datetime.now().isoformat(),
        }
        with open(filepath, "wb") as f:
            pickle.dump(payload, f)
        return filepath

    @staticmethod
    def load_model(filepath: str):
        """Load a previously saved .pkl model payload."""
        with open(filepath, "rb") as f:
            return pickle.load(f)


# ==============================================================================
# MAIN APPLICATION
# ==============================================================================
class AIClassificationApp:
    """
    Main application controller. Owns the root window, sidebar navigation,
    header, and the five content pages (Dashboard, Dataset Explorer,
    Training Center, Visualization Center, Prediction Lab).

    Each page is built lazily into its own Frame and shown/hidden via
    a simple page-stack pattern (only one page visible at a time).
    """

    NAV_ITEMS = [
        ("dashboard", "AI Dashboard"),
        ("explorer", "Dataset Explorer"),
        ("training", "Model Training Center"),
        ("visualize", "Data Visualization"),
        ("predict", "AI Prediction Lab"),
        ("about", "About Project"),
    ]

    def __init__(self):
        self.engine = ClassificationEngine()
        self.dark_mode = True  # theme switcher state

        if TTKBOOTSTRAP_AVAILABLE:
            self.root = tb.Window(themename="cyborg")
        else:
            self.root = tk.Tk()
            style = ttk.Style(self.root)
            try:
                style.theme_use("clam")
            except Exception:
                pass

        self.root.title("AI Data Classification System  |  DecodeLabs Project 2")
        self.root.geometry("1380x860")
        self.root.minsize(1100, 700)
        self.root.configure(bg=Theme.BG)

        # Try to start maximized / fullscreen-ish dashboard for a premium feel
        try:
            self.root.state("zoomed")  # Windows
        except Exception:
            try:
                self.root.attributes("-zoomed", True)  # some Linux WMs
            except Exception:
                pass

        self._set_window_icon_safe()

        self.pages = {}
        self.nav_buttons = {}
        self.current_page = None

        self.selected_model_var = tk.StringVar(value="Decision Tree")
        self.status_var = tk.StringVar(value="Idle - load the dataset to begin")
        self.test_size_var = tk.DoubleVar(value=0.2)

        # Stat card references (updated dynamically as the user progresses)
        self.stat_cards = {}

        self._build_layout()
        self._show_page("dashboard")
        self._animate_startup()

    # ------------------------------------------------------------ window --
    def _set_window_icon_safe(self):
        """Best-effort window icon; silently ignore if unsupported."""
        try:
            self.root.iconbitmap(default="")
        except Exception:
            pass

    def _animate_startup(self):
        """Simple fade-in-like reveal on launch by animating window opacity."""
        try:
            self.root.attributes("-alpha", 0.0)
            steps = 14

            def step(i=0):
                if i > steps:
                    self.root.attributes("-alpha", 1.0)
                    return
                self.root.attributes("-alpha", i / steps)
                self.root.after(18, lambda: step(i + 1))

            step()
        except Exception:
            pass  # platform may not support -alpha; skip gracefully

    # ------------------------------------------------------------- layout --
    def _build_layout(self):
        root = self.root

        outer = tk.Frame(root, bg=Theme.BG)
        outer.pack(fill="both", expand=True)

        # ---- Sidebar -------------------------------------------------
        self.sidebar = tk.Frame(outer, bg=Theme.SIDEBAR_BG, width=240)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        self._build_sidebar(self.sidebar)

        # ---- Right side: header + page container ----------------------
        right = tk.Frame(outer, bg=Theme.BG)
        right.pack(side="left", fill="both", expand=True)

        self.header = tk.Frame(right, bg=Theme.BG, height=72)
        self.header.pack(side="top", fill="x")
        self.header.pack_propagate(False)
        self._build_header(self.header)

        self.page_container = tk.Frame(right, bg=Theme.BG)
        self.page_container.pack(side="top", fill="both", expand=True)

        self.footer = tk.Frame(right, bg=Theme.BG_SECONDARY, height=30)
        self.footer.pack(side="bottom", fill="x")
        self._build_footer(self.footer)

    def _build_sidebar(self, parent):
        logo_frame = tk.Frame(parent, bg=Theme.SIDEBAR_BG, height=90)
        logo_frame.pack(fill="x")
        tk.Label(logo_frame, text="\u2728", font=(Theme.FONT_FAMILY, 22),
                 bg=Theme.SIDEBAR_BG, fg=Theme.ACCENT).place(x=22, y=22)
        tk.Label(logo_frame, text="DECODE", font=(Theme.FONT_FAMILY, 15, "bold"),
                 bg=Theme.SIDEBAR_BG, fg=Theme.TEXT).place(x=58, y=18)
        tk.Label(logo_frame, text="LABS", font=(Theme.FONT_FAMILY, 15, "bold"),
                 bg=Theme.SIDEBAR_BG, fg=Theme.ACCENT).place(x=58, y=40)
        tk.Label(logo_frame, text="AI CLASSIFICATION SYSTEM",
                 font=(Theme.FONT_FAMILY, 8), bg=Theme.SIDEBAR_BG,
                 fg=Theme.TEXT_FAINT).place(x=22, y=66)

        sep = tk.Frame(parent, bg=Theme.CARD_BORDER, height=1)
        sep.pack(fill="x", padx=18, pady=(6, 14))

        nav_frame = tk.Frame(parent, bg=Theme.SIDEBAR_BG)
        nav_frame.pack(fill="x")

        icons = {
            "dashboard": "\u25A6", "explorer": "\u26B8", "training": "\u2699",
            "visualize": "\u25D4", "predict": "\u26A1", "about": "\u2139",
        }

        for key, label in self.NAV_ITEMS:
            btn = self._make_nav_button(nav_frame, key, label, icons.get(key, "\u2022"))
            btn.pack(fill="x", padx=14, pady=4)
            self.nav_buttons[key] = btn

        # Bottom-of-sidebar: theme switcher + reset
        bottom = tk.Frame(parent, bg=Theme.SIDEBAR_BG)
        bottom.pack(side="bottom", fill="x", pady=16, padx=14)

        self.theme_btn = GlowButton(bottom, text="Toggle Theme", icon="\u25D1",
                                     command=self.toggle_theme, width=210, height=40,
                                     color1=Theme.SECONDARY, color2=Theme.PRIMARY, font_size=10)
        self.theme_btn.pack(pady=(0, 8))

        reset_btn = GlowButton(bottom, text="Reset System", icon="\u21BB",
                                command=self.reset_system, width=210, height=40,
                                color1=Theme.DANGER, color2="#B91C1C", font_size=10)
        reset_btn.pack()

    def _make_nav_button(self, parent, key, label, icon):
        is_active = False
        frame = tk.Frame(parent, bg=Theme.SIDEBAR_BG, cursor="hand2")

        bar = tk.Frame(frame, bg=Theme.PRIMARY if is_active else Theme.SIDEBAR_BG, width=4)
        bar.pack(side="left", fill="y")

        content = tk.Frame(frame, bg=Theme.SIDEBAR_BG)
        content.pack(side="left", fill="x", expand=True, padx=(10, 0), pady=10)

        icon_lbl = tk.Label(content, text=icon, font=(Theme.FONT_FAMILY, 12),
                             bg=Theme.SIDEBAR_BG, fg=Theme.TEXT_MUTED)
        icon_lbl.pack(side="left")

        text_lbl = tk.Label(content, text=label, font=(Theme.FONT_FAMILY, 10, "bold"),
                             bg=Theme.SIDEBAR_BG, fg=Theme.TEXT_MUTED)
        text_lbl.pack(side="left", padx=(10, 0))

        widgets = [frame, content, icon_lbl, text_lbl, bar]

        def on_click(event=None):
            self._show_page(key)

        def on_enter(event=None):
            if self.current_page != key:
                for w in (frame, content, icon_lbl, text_lbl):
                    w.configure(bg=Theme.CARD_BG)
                icon_lbl.configure(fg=Theme.ACCENT)
                text_lbl.configure(fg=Theme.TEXT)

        def on_leave(event=None):
            if self.current_page != key:
                for w in (frame, content, icon_lbl, text_lbl):
                    w.configure(bg=Theme.SIDEBAR_BG)
                icon_lbl.configure(fg=Theme.TEXT_MUTED)
                text_lbl.configure(fg=Theme.TEXT_MUTED)

        for w in widgets:
            w.bind("<Button-1>", on_click)
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)

        frame._key = key
        frame._bar = bar
        frame._content = content
        frame._icon_lbl = icon_lbl
        frame._text_lbl = text_lbl
        return frame

    def _refresh_nav_styles(self):
        for key, frame in self.nav_buttons.items():
            active = (key == self.current_page)
            bg = Theme.CARD_BG if active else Theme.SIDEBAR_BG
            bar_color = Theme.PRIMARY if active else Theme.SIDEBAR_BG
            fg_icon = Theme.ACCENT if active else Theme.TEXT_MUTED
            fg_text = Theme.TEXT if active else Theme.TEXT_MUTED
            frame.configure(bg=bg)
            frame._content.configure(bg=bg)
            frame._icon_lbl.configure(bg=bg, fg=fg_icon)
            frame._text_lbl.configure(bg=bg, fg=fg_text)
            frame._bar.configure(bg=bar_color)

    def _build_header(self, parent):
        title_map = dict(self.NAV_ITEMS)
        self.header_title_var = tk.StringVar(value="AI Dashboard")

        tk.Label(parent, textvariable=self.header_title_var,
                 font=(Theme.FONT_FAMILY, 18, "bold"),
                 bg=Theme.BG, fg=Theme.TEXT).place(x=28, y=18)

        tk.Label(parent, text="Supervised Learning \u2022 Iris Dataset \u2022 Real-Time Predictions",
                 font=(Theme.FONT_FAMILY, 9), bg=Theme.BG,
                 fg=Theme.TEXT_FAINT).place(x=28, y=46)

        # Status pill on the right
        self.status_pill = RoundedCard(parent, width=360, height=40, radius=20,
                                        bg=Theme.CARD_BG)
        self.status_pill.place(relx=1.0, x=-28, y=16, anchor="ne")
        dot = tk.Label(self.status_pill.inner, text="\u25CF", font=(Theme.FONT_FAMILY, 9),
                        bg=Theme.CARD_BG, fg=Theme.SUCCESS)
        dot.pack(side="left", padx=(14, 6))
        tk.Label(self.status_pill.inner, textvariable=self.status_var,
                 font=(Theme.FONT_FAMILY, 9), bg=Theme.CARD_BG,
                 fg=Theme.TEXT_MUTED, anchor="w").pack(side="left", fill="x", expand=True)
        self._status_dot = dot

        sep = tk.Frame(parent, bg=Theme.CARD_BORDER, height=1)
        sep.place(relx=0, rely=1.0, relwidth=1.0, y=-1)

    def _build_footer(self, parent):
        tk.Label(parent, text="\u00A9 2026 DecodeLabs  \u2022  AI Data Classification System  \u2022  Project 2",
                 font=(Theme.FONT_FAMILY, 8), bg=Theme.BG_SECONDARY,
                 fg=Theme.TEXT_FAINT).pack(side="left", padx=16)
        tk.Label(parent, text="Built with Python \u2022 Scikit-Learn \u2022 Tkinter \u2022 Matplotlib",
                 font=(Theme.FONT_FAMILY, 8), bg=Theme.BG_SECONDARY,
                 fg=Theme.TEXT_FAINT).pack(side="right", padx=16)

    def set_status(self, text, color=Theme.SUCCESS):
        self.status_var.set(text)
        self._status_dot.configure(fg=color)

    # --------------------------------------------------------- navigation --
    def _show_page(self, key):
        """Show the requested page, building it lazily on first visit."""
        title_map = dict(self.NAV_ITEMS)
        if key not in self.pages:
            builder = {
                "dashboard": self._build_dashboard_page,
                "explorer": self._build_explorer_page,
                "training": self._build_training_page,
                "visualize": self._build_visualize_page,
                "predict": self._build_predict_page,
                "about": self._build_about_page,
            }[key]
            page = tk.Frame(self.page_container, bg=Theme.BG)
            builder(page)
            self.pages[key] = page

        for k, p in self.pages.items():
            if k == key:
                p.place(x=0, y=0, relwidth=1, relheight=1)
            else:
                p.place_forget()

        self.current_page = key
        self.header_title_var.set(title_map.get(key, key))
        self._refresh_nav_styles()

        if key == "explorer" and self.engine.dataframe is not None:
            self._refresh_explorer_table()
        if key == "predict":
            self._refresh_predict_model_choices()

    def toggle_theme(self):
        """
        Theme switcher. Full light/dark re-skinning of every widget is out of
        scope for a single in-memory ttk app without a restart, so we toggle
        a 'high contrast accent' variant of the dark theme to give visible,
        functional feedback - while keeping the app fully usable.
        """
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self.set_status("Theme: Premium Dark", Theme.SUCCESS)
        else:
            self.set_status("Theme: Midnight Accent", Theme.ACCENT)
        messagebox.showinfo(
            "Theme Switcher",
            "Theme preference updated.\n\n"
            "This build ships with a premium dark theme tuned to the "
            "DecodeLabs color palette. A full light-mode re-skin can be "
            "added as a future enhancement."
        )

    def reset_system(self):
        """Reset all engine state and rebuild every page from scratch."""
        if not messagebox.askyesno("Reset System",
                                    "This will clear the loaded dataset, trained models, "
                                    "and all results. Continue?"):
            return
        self.engine = ClassificationEngine()
        for page in self.pages.values():
            page.destroy()
        self.pages.clear()
        self.set_status("System reset - load the dataset to begin", Theme.WARNING)
        self._show_page("dashboard")

    # ============================================================ PAGE 1 ==
    # AI DASHBOARD
    # =========================================================================
    def _build_dashboard_page(self, page):
        scroll = self._make_scrollable(page)

        header_row = tk.Frame(scroll, bg=Theme.BG)
        header_row.pack(fill="x", padx=28, pady=(22, 10))
        tk.Label(header_row, text="Welcome to your AI Dashboard",
                 font=(Theme.FONT_FAMILY, 16, "bold"), bg=Theme.BG,
                 fg=Theme.TEXT).pack(side="left")

        load_btn = GlowButton(header_row, text="Load Iris Dataset", icon="\u2B07",
                               command=self.action_load_dataset, width=200, height=42,
                               color1=Theme.PRIMARY, color2=Theme.ACCENT)
        load_btn.pack(side="right")
        self.dashboard_load_btn = load_btn

        # ---- Stat cards row -------------------------------------------
        cards_row = tk.Frame(scroll, bg=Theme.BG)
        cards_row.pack(fill="x", padx=28, pady=10)

        specs = [
            ("total_samples", "Total Samples", "0", "\u25A6", Theme.PRIMARY),
            ("total_features", "Total Features", "0", "\u2699", Theme.ACCENT),
            ("accuracy", "Accuracy Score", "--", "\u2713", Theme.SUCCESS),
            ("model_status", "Model Status", "Not Trained", "\u26A1", Theme.SECONDARY),
        ]
        for i, (key, title, val, icon, color) in enumerate(specs):
            card = StatCard(cards_row, title, val, icon=icon, color=color,
                             width=280, height=120)
            card.grid(row=0, column=i, padx=10, pady=6, sticky="nsew")
            cards_row.grid_columnconfigure(i, weight=1)
            self.stat_cards[key] = card

        # ---- Dataset information panel ---------------------------------
        info_card = RoundedCard(scroll, width=1280, height=300, radius=18)
        info_card.pack(fill="x", padx=28, pady=16)
        tk.Label(info_card.inner, text="Dataset Information Panel",
                 font=(Theme.FONT_FAMILY, 13, "bold"), bg=Theme.CARD_BG,
                 fg=Theme.TEXT).pack(anchor="w", padx=20, pady=(16, 6))

        self.dashboard_info_text = tk.Text(
            info_card.inner, height=11, bg=Theme.BG_SECONDARY, fg=Theme.TEXT_MUTED,
            font=(Theme.FONT_FAMILY_MONO, 10), relief="flat", wrap="word",
            highlightthickness=1, highlightbackground=Theme.CARD_BORDER, padx=14, pady=10
        )
        self.dashboard_info_text.pack(fill="both", expand=True, padx=20, pady=(0, 18))
        self.dashboard_info_text.insert(
            "1.0",
            "No dataset loaded yet.\n\n"
            "Click 'Load Iris Dataset' above to fetch the classic Iris "
            "flower dataset (150 samples, 4 features, 3 species classes) "
            "and populate this dashboard, the Dataset Explorer, and the "
            "Model Training Center."
        )
        self.dashboard_info_text.configure(state="disabled")

        # ---- Quick-start guidance row ------------------------------------
        tips_card = RoundedCard(scroll, width=1280, height=120, radius=18)
        tips_card.pack(fill="x", padx=28, pady=(0, 24))
        tk.Label(tips_card.inner, text="\U0001F9ED  Quick Start",
                 font=(Theme.FONT_FAMILY, 11, "bold"), bg=Theme.CARD_BG,
                 fg=Theme.ACCENT).pack(anchor="w", padx=20, pady=(14, 4))
        tk.Label(tips_card.inner,
                 text="1. Load Dataset  \u2192  2. Explore Data  \u2192  3. Train a Model  "
                      "\u2192  4. Visualize Results  \u2192  5. Make Predictions",
                 font=(Theme.FONT_FAMILY, 10), bg=Theme.CARD_BG,
                 fg=Theme.TEXT_MUTED).pack(anchor="w", padx=20)

    def _make_scrollable(self, parent):
        """Helper: wrap content in a vertically scrollable canvas+frame."""
        canvas = tk.Canvas(parent, bg=Theme.BG, highlightthickness=0)
        vscroll = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vscroll.set)
        canvas.pack(side="left", fill="both", expand=True)
        vscroll.pack(side="right", fill="y")

        inner = tk.Frame(canvas, bg=Theme.BG)
        inner_id = canvas.create_window((0, 0), window=inner, anchor="nw")

        def on_inner_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def on_canvas_configure(event):
            canvas.itemconfig(inner_id, width=event.width)

        inner.bind("<Configure>", on_inner_configure)
        canvas.bind("<Configure>", on_canvas_configure)

        def on_mousewheel(event):
            delta = -1 * (event.delta // 120) if event.delta else 0
            canvas.yview_scroll(int(delta), "units")

        def bind_wheel(event):
            canvas.bind_all("<MouseWheel>", on_mousewheel)

        def unbind_wheel(event):
            canvas.unbind_all("<MouseWheel>")

        # Only capture the mouse wheel while the cursor is over THIS canvas,
        # so multiple scrollable pages don't fight over the global binding.
        canvas.bind("<Enter>", bind_wheel)
        canvas.bind("<Leave>", unbind_wheel)
        return inner

    # -------------------------------------------------------- dashboard actions --
    def action_load_dataset(self):
        """Load the Iris dataset and refresh the dashboard + explorer."""
        try:
            self.dashboard_load_btn.set_disabled(True)
            self.set_status("Loading Iris dataset...", Theme.WARNING)
            self.root.update_idletasks()

            df = self.engine.load_iris_dataset()
            summary = self.engine.dataset_summary()

            self.stat_cards["total_samples"].set_value(summary["total_samples"])
            self.stat_cards["total_features"].set_value(summary["total_features"])
            self.stat_cards["model_status"].set_value("Ready to Train")

            info_lines = [
                f"Dataset: Iris Flower Dataset (scikit-learn built-in)",
                f"Total Samples: {summary['total_samples']}",
                f"Total Features: {summary['total_features']} -> {', '.join(self.engine.feature_names)}",
                f"Target Classes ({summary['num_classes']}): {', '.join(self.engine.target_names)}",
                f"Class Distribution: " + ", ".join(
                    f"{k} = {v}" for k, v in summary["class_distribution"].items()
                ),
                f"Missing Values: {summary['missing_values']}",
                "",
                "Dataset loaded successfully. Head over to 'Dataset Explorer' to "
                "browse the raw samples, or 'Model Training Center' to train a "
                "classifier.",
            ]
            self.dashboard_info_text.configure(state="normal")
            self.dashboard_info_text.delete("1.0", "end")
            self.dashboard_info_text.insert("1.0", "\n".join(info_lines))
            self.dashboard_info_text.configure(state="disabled")

            self.set_status("Dataset loaded - 150 samples ready", Theme.SUCCESS)
            messagebox.showinfo("Dataset Loaded",
                                 "Iris dataset loaded successfully!\n\n"
                                 f"{summary['total_samples']} samples \u00d7 "
                                 f"{summary['total_features']} features, "
                                 f"{summary['num_classes']} classes.")
        except Exception as e:
            self.set_status("Error loading dataset", Theme.DANGER)
            messagebox.showerror("Error", f"Failed to load dataset:\n\n{e}\n\n{traceback.format_exc()[-400:]}")
        finally:
            self.dashboard_load_btn.set_disabled(False)

    # ============================================================ PAGE 2 ==
    # DATASET EXPLORER
    # =========================================================================
    def _build_explorer_page(self, page):
        top = tk.Frame(page, bg=Theme.BG)
        top.pack(fill="x", padx=28, pady=(22, 10))

        tk.Label(top, text="Dataset Explorer", font=(Theme.FONT_FAMILY, 16, "bold"),
                 bg=Theme.BG, fg=Theme.TEXT).pack(side="left")

        search_card = RoundedCard(top, width=320, height=40, radius=20)
        search_card.pack(side="right")
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_card.inner, textvariable=self.search_var,
                                 bg=Theme.CARD_BG, fg=Theme.TEXT, relief="flat",
                                 insertbackground=Theme.TEXT,
                                 font=(Theme.FONT_FAMILY, 10))
        search_entry.pack(fill="both", expand=True, padx=(16, 8), pady=6)
        self.search_entry = search_entry
        self._search_placeholder = "Search by species (e.g. setosa)..."
        self._add_placeholder(search_entry, self._search_placeholder)
        self.search_var.trace_add("write", lambda *a: self._refresh_explorer_table())

        body = tk.Frame(page, bg=Theme.BG)
        body.pack(fill="both", expand=True, padx=28, pady=(0, 20))

        # ---- Left: table -------------------------------------------------
        table_card = RoundedCard(body, width=880, height=560, radius=18)
        table_card.pack(side="left", fill="both", expand=True, padx=(0, 14))

        tk.Label(table_card.inner, text="Scrollable Dataset Viewer",
                 font=(Theme.FONT_FAMILY, 11, "bold"), bg=Theme.CARD_BG,
                 fg=Theme.TEXT).pack(anchor="w", padx=16, pady=(14, 6))

        table_wrap = tk.Frame(table_card.inner, bg=Theme.CARD_BG)
        table_wrap.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        columns = ("idx", "sl", "sw", "pl", "pw", "species")
        headers = {"idx": "#", "sl": "Sepal L", "sw": "Sepal W",
                   "pl": "Petal L", "pw": "Petal W", "species": "Species"}

        style = ttk.Style()
        style.configure("Explorer.Treeview",
                         background=Theme.BG_SECONDARY,
                         fieldbackground=Theme.BG_SECONDARY,
                         foreground=Theme.TEXT,
                         rowheight=26, borderwidth=0, font=(Theme.FONT_FAMILY, 9))
        style.configure("Explorer.Treeview.Heading",
                         background=Theme.CARD_BORDER, foreground=Theme.TEXT,
                         font=(Theme.FONT_FAMILY, 9, "bold"), relief="flat")
        style.map("Explorer.Treeview", background=[("selected", Theme.PRIMARY)])

        self.explorer_tree = ttk.Treeview(table_wrap, columns=columns, show="headings",
                                           style="Explorer.Treeview", height=18)
        for c in columns:
            self.explorer_tree.heading(c, text=headers[c])
            width = 50 if c == "idx" else (110 if c != "species" else 130)
            self.explorer_tree.column(c, width=width, anchor="center")

        vs = ttk.Scrollbar(table_wrap, orient="vertical", command=self.explorer_tree.yview)
        self.explorer_tree.configure(yscrollcommand=vs.set)
        self.explorer_tree.pack(side="left", fill="both", expand=True)
        vs.pack(side="right", fill="y")

        # ---- Right: feature statistics ------------------------------------
        stats_card = RoundedCard(body, width=380, height=560, radius=18)
        stats_card.pack(side="left", fill="y")

        tk.Label(stats_card.inner, text="Feature Statistics",
                 font=(Theme.FONT_FAMILY, 11, "bold"), bg=Theme.CARD_BG,
                 fg=Theme.TEXT).pack(anchor="w", padx=16, pady=(14, 6))

        self.stats_text = tk.Text(stats_card.inner, bg=Theme.BG_SECONDARY, fg=Theme.TEXT_MUTED,
                                   font=(Theme.FONT_FAMILY_MONO, 9), relief="flat", wrap="none",
                                   highlightthickness=1, highlightbackground=Theme.CARD_BORDER,
                                   padx=10, pady=10)
        self.stats_text.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        self.stats_text.insert("1.0", "Load the dataset to view feature statistics.")
        self.stats_text.configure(state="disabled")

    def _add_placeholder(self, entry, placeholder_text):
        entry.configure(fg=Theme.TEXT_FAINT)
        entry.insert(0, placeholder_text)

        def on_focus_in(event):
            if entry.get() == placeholder_text:
                entry.delete(0, "end")
                entry.configure(fg=Theme.TEXT)

        def on_focus_out(event):
            if not entry.get():
                entry.configure(fg=Theme.TEXT_FAINT)
                entry.insert(0, placeholder_text)

        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)
        entry._placeholder = placeholder_text

    def _refresh_explorer_table(self):
        if not hasattr(self, "explorer_tree") or self.engine.dataframe is None:
            return
        df = self.engine.dataframe
        query = self.search_var.get().strip().lower()
        if query == self._search_placeholder.lower():
            query = ""

        if query:
            filtered = df[df["species"].str.lower().str.contains(query)]
        else:
            filtered = df

        self.explorer_tree.delete(*self.explorer_tree.get_children())
        for idx, row in filtered.iterrows():
            self.explorer_tree.insert("", "end", values=(
                idx,
                round(row[self.engine.feature_names[0]], 2),
                round(row[self.engine.feature_names[1]], 2),
                round(row[self.engine.feature_names[2]], 2),
                round(row[self.engine.feature_names[3]], 2),
                row["species"],
            ))

        # refresh feature statistics
        stats_df = self.engine.feature_statistics()
        self.stats_text.configure(state="normal")
        self.stats_text.delete("1.0", "end")
        if not stats_df.empty:
            self.stats_text.insert("1.0", stats_df.to_string())
        self.stats_text.configure(state="disabled")

    # ============================================================ PAGE 3 ==
    # MODEL TRAINING CENTER
    # =========================================================================
    def _build_training_page(self, page):
        scroll = self._make_scrollable(page)

        tk.Label(scroll, text="Model Training Center", font=(Theme.FONT_FAMILY, 16, "bold"),
                 bg=Theme.BG, fg=Theme.TEXT).pack(anchor="w", padx=28, pady=(22, 10))

        body = tk.Frame(scroll, bg=Theme.BG)
        body.pack(fill="x", padx=28)

        # ---- Left: configuration card --------------------------------
        config_card = RoundedCard(body, width=420, height=420, radius=18)
        config_card.pack(side="left", fill="y", padx=(0, 14))

        tk.Label(config_card.inner, text="Training Configuration",
                 font=(Theme.FONT_FAMILY, 12, "bold"), bg=Theme.CARD_BG,
                 fg=Theme.TEXT).pack(anchor="w", padx=18, pady=(16, 12))

        tk.Label(config_card.inner, text="SELECT CLASSIFICATION ALGORITHM",
                 font=(Theme.FONT_FAMILY, 8, "bold"), bg=Theme.CARD_BG,
                 fg=Theme.TEXT_MUTED).pack(anchor="w", padx=18, pady=(0, 6))

        radio_frame = tk.Frame(config_card.inner, bg=Theme.CARD_BG)
        radio_frame.pack(fill="x", padx=18, pady=(0, 16))

        for model_name in ClassificationEngine.MODEL_REGISTRY.keys():
            rb = tk.Radiobutton(
                radio_frame, text=model_name, variable=self.selected_model_var,
                value=model_name, bg=Theme.CARD_BG, fg=Theme.TEXT,
                activebackground=Theme.CARD_BG, activeforeground=Theme.ACCENT,
                selectcolor=Theme.BG_SECONDARY, font=(Theme.FONT_FAMILY, 10),
                highlightthickness=0, bd=0, anchor="w", cursor="hand2"
            )
            rb.pack(anchor="w", pady=4)

        tk.Label(config_card.inner, text="TEST SET SIZE",
                 font=(Theme.FONT_FAMILY, 8, "bold"), bg=Theme.CARD_BG,
                 fg=Theme.TEXT_MUTED).pack(anchor="w", padx=18, pady=(8, 4))

        slider_row = tk.Frame(config_card.inner, bg=Theme.CARD_BG)
        slider_row.pack(fill="x", padx=18, pady=(0, 16))

        self.test_size_label = tk.Label(slider_row, text="20%",
                                         font=(Theme.FONT_FAMILY, 10, "bold"),
                                         bg=Theme.CARD_BG, fg=Theme.ACCENT, width=5)
        self.test_size_label.pack(side="right")

        test_size_scale = ttk.Scale(slider_row, from_=0.1, to=0.5,
                                     variable=self.test_size_var, orient="horizontal",
                                     command=self._on_test_size_change)
        test_size_scale.pack(side="left", fill="x", expand=True, padx=(0, 10))

        tk.Frame(config_card.inner, bg=Theme.CARD_BORDER, height=1).pack(
            fill="x", padx=18, pady=(4, 16))

        self.train_btn = GlowButton(config_card.inner, text="Train Model", icon="\u25B6",
                                     command=self.action_train_model, width=200, height=46,
                                     color1=Theme.PRIMARY, color2=Theme.SECONDARY)
        self.train_btn.pack(padx=18, pady=(0, 10))

        tk.Label(config_card.inner, text="Training uses an 80/20 (default) "
                                          "stratified split with feature scaling applied.",
                 font=(Theme.FONT_FAMILY, 8), bg=Theme.CARD_BG, fg=Theme.TEXT_FAINT,
                 wraplength=360, justify="left").pack(anchor="w", padx=18)

        # ---- Right: progress + live status --------------------------------
        progress_card = RoundedCard(body, width=820, height=420, radius=18)
        progress_card.pack(side="left", fill="both", expand=True)

        tk.Label(progress_card.inner, text="Training Status",
                 font=(Theme.FONT_FAMILY, 12, "bold"), bg=Theme.CARD_BG,
                 fg=Theme.TEXT).pack(anchor="w", padx=20, pady=(16, 10))

        self.training_progress = AnimatedProgressBar(progress_card.inner, width=760, height=14)
        self.training_progress.pack(padx=20, pady=(0, 10), anchor="w")

        self.training_status_var = tk.StringVar(value="Awaiting training run...")
        tk.Label(progress_card.inner, textvariable=self.training_status_var,
                 font=(Theme.FONT_FAMILY, 9), bg=Theme.CARD_BG,
                 fg=Theme.TEXT_MUTED).pack(anchor="w", padx=20, pady=(0, 16))

        results_row = tk.Frame(progress_card.inner, bg=Theme.CARD_BG)
        results_row.pack(fill="x", padx=20, pady=(0, 10))

        self.live_accuracy_card = StatCard(results_row, "Live Accuracy", "--",
                                            icon="\u2713", color=Theme.SUCCESS,
                                            width=240, height=100)
        self.live_accuracy_card.pack(side="left", padx=(0, 12))

        self.live_model_card = StatCard(results_row, "Active Model", "None",
                                         icon="\u26A1", color=Theme.SECONDARY,
                                         width=240, height=100)
        self.live_model_card.pack(side="left")

        tk.Label(progress_card.inner, text="Classification Report",
                 font=(Theme.FONT_FAMILY, 11, "bold"), bg=Theme.CARD_BG,
                 fg=Theme.TEXT).pack(anchor="w", padx=20, pady=(10, 4))

        self.report_text = tk.Text(progress_card.inner, height=10, bg=Theme.BG_SECONDARY,
                                    fg=Theme.TEXT_MUTED, font=(Theme.FONT_FAMILY_MONO, 9),
                                    relief="flat", highlightthickness=1,
                                    highlightbackground=Theme.CARD_BORDER, padx=12, pady=8)
        self.report_text.pack(fill="both", expand=True, padx=20, pady=(0, 16))
        self.report_text.insert("1.0", "Train a model to see its classification report here.")
        self.report_text.configure(state="disabled")

        # ---- Model comparison section --------------------------------
        compare_card = RoundedCard(scroll, width=1260, height=160, radius=18)
        compare_card.pack(fill="x", padx=28, pady=20)

        header_row = tk.Frame(compare_card.inner, bg=Theme.CARD_BG)
        header_row.pack(fill="x", padx=20, pady=(14, 6))
        tk.Label(header_row, text="Model Performance Comparison",
                 font=(Theme.FONT_FAMILY, 12, "bold"), bg=Theme.CARD_BG,
                 fg=Theme.TEXT).pack(side="left")

        export_btn = GlowButton(header_row, text="Export Results CSV", icon="\u2B07",
                                 command=self.action_export_csv, width=200, height=36,
                                 color1=Theme.ACCENT, color2=Theme.SUCCESS, font_size=9)
        export_btn.pack(side="right", padx=(8, 0))

        save_btn = GlowButton(header_row, text="Save Model (.pkl)", icon="\U0001F4BE",
                               command=self.action_save_model, width=200, height=36,
                               color1=Theme.SECONDARY, color2=Theme.PRIMARY, font_size=9)
        save_btn.pack(side="right")

        self.comparison_frame = tk.Frame(compare_card.inner, bg=Theme.CARD_BG)
        self.comparison_frame.pack(fill="x", padx=20, pady=(0, 16))
        self.comparison_labels = {}
        self._rebuild_comparison_row()

    def _on_test_size_change(self, value):
        pct = int(float(value) * 100)
        self.test_size_label.configure(text=f"{pct}%")

    def _rebuild_comparison_row(self):
        for w in self.comparison_frame.winfo_children():
            w.destroy()
        self.comparison_labels = {}

        if not self.engine.results:
            tk.Label(self.comparison_frame, text="No models trained yet. Train at least "
                                                   "one model above to populate this comparison.",
                     font=(Theme.FONT_FAMILY, 9), bg=Theme.CARD_BG,
                     fg=Theme.TEXT_FAINT).pack(anchor="w")
            return

        for i, (name, res) in enumerate(self.engine.results.items()):
            row = tk.Frame(self.comparison_frame, bg=Theme.CARD_BG)
            row.pack(fill="x", pady=4)
            tk.Label(row, text=name, font=(Theme.FONT_FAMILY, 10, "bold"),
                     bg=Theme.CARD_BG, fg=Theme.TEXT, width=18, anchor="w").pack(side="left")

            bar_bg = tk.Canvas(row, width=600, height=18, bg=Theme.BG_SECONDARY,
                                highlightthickness=0)
            bar_bg.pack(side="left", padx=10)
            acc = res["accuracy"]
            bar_bg.create_rectangle(0, 0, 600 * acc, 18,
                                     fill=Theme.SUCCESS if acc >= 0.9 else Theme.WARNING,
                                     outline="")
            tk.Label(row, text=f"{acc*100:.2f}%", font=(Theme.FONT_FAMILY, 10, "bold"),
                     bg=Theme.CARD_BG, fg=Theme.ACCENT).pack(side="left")

    # -------------------------------------------------------- training actions --
    def action_train_model(self):
        if self.engine.dataframe is None:
            messagebox.showwarning("No Dataset", "Please load the Iris dataset first "
                                                   "from the AI Dashboard.")
            return

        model_name = self.selected_model_var.get()
        test_size = round(self.test_size_var.get(), 2)

        self.train_btn.set_disabled(True)
        self.training_status_var.set(f"Splitting data ({int((1-test_size)*100)}/"
                                      f"{int(test_size*100)} train/test)...")
        self.training_progress.set_progress(0)
        self.set_status(f"Training {model_name}...", Theme.WARNING)
        self.root.update_idletasks()

        def worker():
            try:
                self.engine.split_data(test_size=test_size)
                # animate progress while the (very fast) actual fit happens
                self.root.after(0, lambda: self.training_status_var.set(
                    f"Training {model_name} classifier..."))

                model, results = self.engine.train_model(model_name)

                def finish():
                    self.training_progress.animate_to(1.0, duration_ms=900,
                                                        on_complete=lambda: self._on_training_complete(model_name, results))

                self.root.after(0, finish)
            except Exception as e:
                err = traceback.format_exc()
                self.root.after(0, lambda: self._on_training_error(e, err))

        threading.Thread(target=worker, daemon=True).start()

    def _on_training_complete(self, model_name, results):
        acc = results["accuracy"]
        self.live_accuracy_card.set_value(f"{acc*100:.2f}%")
        self.live_model_card.set_value(model_name)
        self.stat_cards["accuracy"].set_value(f"{acc*100:.1f}%")
        self.stat_cards["model_status"].set_value("Trained")

        self.training_status_var.set(
            f"\u2713 {model_name} trained successfully at "
            f"{results['trained_at']} - Accuracy: {acc*100:.2f}%"
        )

        self.report_text.configure(state="normal")
        self.report_text.delete("1.0", "end")
        self.report_text.insert("1.0", results["report_text"])
        self.report_text.configure(state="disabled")

        self._rebuild_comparison_row()
        self.train_btn.set_disabled(False)
        self.set_status(f"{model_name} trained - {acc*100:.2f}% accuracy", Theme.SUCCESS)

        # Refresh visualization page if it has already been built
        if "visualize" in self.pages:
            self._refresh_visualizations()
        if "predict" in self.pages:
            self._refresh_predict_model_choices()

    def _on_training_error(self, exception, tb_text):
        self.train_btn.set_disabled(False)
        self.training_status_var.set("Training failed - see error dialog.")
        self.set_status("Training error", Theme.DANGER)
        messagebox.showerror("Training Error", f"{exception}\n\n{tb_text[-500:]}")

    def action_export_csv(self):
        if not self.engine.results:
            messagebox.showwarning("No Results", "Train a model before exporting results.")
            return
        model_name = self.engine.active_model_name or self.selected_model_var.get()
        if model_name not in self.engine.results:
            model_name = list(self.engine.results.keys())[-1]

        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=f"{model_name.replace(' ', '_').lower()}_results.csv",
            title="Export Results to CSV"
        )
        if not filepath:
            return
        try:
            self.engine.export_results_csv(model_name, filepath)
            self.set_status(f"Results exported: {os.path.basename(filepath)}", Theme.SUCCESS)
            messagebox.showinfo("Export Complete", f"Results exported successfully to:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    def action_save_model(self):
        if not self.engine.models:
            messagebox.showwarning("No Trained Model", "Train a model before saving it.")
            return
        model_name = self.engine.active_model_name or self.selected_model_var.get()
        if model_name not in self.engine.models:
            model_name = list(self.engine.models.keys())[-1]

        filepath = filedialog.asksaveasfilename(
            defaultextension=".pkl",
            filetypes=[("Pickle files", "*.pkl")],
            initialfile=f"{model_name.replace(' ', '_').lower()}_model.pkl",
            title="Save Trained Model"
        )
        if not filepath:
            return
        try:
            self.engine.save_model(model_name, filepath)
            self.set_status(f"Model saved: {os.path.basename(filepath)}", Theme.SUCCESS)
            messagebox.showinfo("Model Saved", f"'{model_name}' saved successfully to:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Save Error", str(e))

    # ============================================================ PAGE 4 ==
    # DATA VISUALIZATION CENTER
    # =========================================================================
    def _build_visualize_page(self, page):
        scroll = self._make_scrollable(page)

        top = tk.Frame(scroll, bg=Theme.BG)
        top.pack(fill="x", padx=28, pady=(22, 10))
        tk.Label(top, text="Data Visualization Center", font=(Theme.FONT_FAMILY, 16, "bold"),
                 bg=Theme.BG, fg=Theme.TEXT).pack(side="left")

        refresh_btn = GlowButton(top, text="Refresh Charts", icon="\u21BB",
                                  command=self._refresh_visualizations, width=180, height=40,
                                  color1=Theme.ACCENT, color2=Theme.PRIMARY, font_size=10)
        refresh_btn.pack(side="right")

        grid = tk.Frame(scroll, bg=Theme.BG)
        grid.pack(fill="both", expand=True, padx=28, pady=(0, 24))

        # Feature Distribution chart
        self.chart_card_dist = RoundedCard(grid, width=610, height=420, radius=18)
        self.chart_card_dist.grid(row=0, column=0, padx=8, pady=8, sticky="nsew")
        tk.Label(self.chart_card_dist.inner, text="Feature Distribution",
                 font=(Theme.FONT_FAMILY, 11, "bold"), bg=Theme.CARD_BG,
                 fg=Theme.TEXT).pack(anchor="w", padx=14, pady=(12, 0))
        self.dist_chart_holder = tk.Frame(self.chart_card_dist.inner, bg=Theme.CARD_BG)
        self.dist_chart_holder.pack(fill="both", expand=True, padx=10, pady=8)

        # Accuracy Comparison chart
        self.chart_card_acc = RoundedCard(grid, width=610, height=420, radius=18)
        self.chart_card_acc.grid(row=0, column=1, padx=8, pady=8, sticky="nsew")
        tk.Label(self.chart_card_acc.inner, text="Accuracy Comparison",
                 font=(Theme.FONT_FAMILY, 11, "bold"), bg=Theme.CARD_BG,
                 fg=Theme.TEXT).pack(anchor="w", padx=14, pady=(12, 0))
        self.acc_chart_holder = tk.Frame(self.chart_card_acc.inner, bg=Theme.CARD_BG)
        self.acc_chart_holder.pack(fill="both", expand=True, padx=10, pady=8)

        # Confusion Matrix heatmap
        self.chart_card_cm = RoundedCard(grid, width=610, height=420, radius=18)
        self.chart_card_cm.grid(row=1, column=0, padx=8, pady=8, sticky="nsew")
        tk.Label(self.chart_card_cm.inner, text="Confusion Matrix Heatmap",
                 font=(Theme.FONT_FAMILY, 11, "bold"), bg=Theme.CARD_BG,
                 fg=Theme.TEXT).pack(anchor="w", padx=14, pady=(12, 0))
        self.cm_chart_holder = tk.Frame(self.chart_card_cm.inner, bg=Theme.CARD_BG)
        self.cm_chart_holder.pack(fill="both", expand=True, padx=10, pady=8)

        # Prediction Analytics (feature importance)
        self.chart_card_fi = RoundedCard(grid, width=610, height=420, radius=18)
        self.chart_card_fi.grid(row=1, column=1, padx=8, pady=8, sticky="nsew")
        tk.Label(self.chart_card_fi.inner, text="Prediction Analytics (Feature Importance)",
                 font=(Theme.FONT_FAMILY, 11, "bold"), bg=Theme.CARD_BG,
                 fg=Theme.TEXT).pack(anchor="w", padx=14, pady=(12, 0))
        self.fi_chart_holder = tk.Frame(self.chart_card_fi.inner, bg=Theme.CARD_BG)
        self.fi_chart_holder.pack(fill="both", expand=True, padx=10, pady=8)

        grid.grid_columnconfigure(0, weight=1)
        grid.grid_columnconfigure(1, weight=1)

        self._refresh_visualizations()

    def _embed_figure(self, holder, fig):
        """Clear a holder frame and embed a fresh matplotlib figure into it."""
        for w in holder.winfo_children():
            w.destroy()
        canvas = FigureCanvasTkAgg(fig, master=holder)
        canvas.draw()
        canvas.get_tk_widget().configure(bg=Theme.CARD_BG, highlightthickness=0)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        plt.close(fig)

    def _empty_chart_message(self, holder, message):
        for w in holder.winfo_children():
            w.destroy()
        tk.Label(holder, text=message, font=(Theme.FONT_FAMILY, 9),
                 bg=Theme.CARD_BG, fg=Theme.TEXT_FAINT, wraplength=520,
                 justify="center").pack(expand=True)

    def _refresh_visualizations(self):
        if not hasattr(self, "dist_chart_holder"):
            return  # page not built yet

        # ---- Feature Distribution ----------------------------------------
        if self.engine.dataframe is not None:
            df = self.engine.dataframe
            fig = Figure(figsize=(5.6, 3.6), dpi=100)
            ax = fig.add_subplot(111)
            colors = [Theme.PRIMARY, Theme.ACCENT, Theme.SECONDARY, Theme.SUCCESS]
            for i, feat in enumerate(self.engine.feature_names):
                ax.hist(df[feat], bins=12, alpha=0.55, label=feat, color=colors[i % len(colors)])
            ax.legend(fontsize=6, facecolor=Theme.CARD_BG, edgecolor=Theme.CARD_BORDER,
                      labelcolor=Theme.TEXT_MUTED)
            ax.set_xlabel("Value (cm)", fontsize=8)
            ax.set_ylabel("Frequency", fontsize=8)
            ax.tick_params(labelsize=7)
            fig.tight_layout()
            self._embed_figure(self.dist_chart_holder, fig)
        else:
            self._empty_chart_message(self.dist_chart_holder, "Load the dataset to view feature distributions.")

        # ---- Accuracy Comparison ------------------------------------------
        if self.engine.results:
            fig = Figure(figsize=(5.6, 3.6), dpi=100)
            ax = fig.add_subplot(111)
            names = list(self.engine.results.keys())
            accs = [self.engine.results[n]["accuracy"] * 100 for n in names]
            bar_colors = [Theme.PRIMARY, Theme.SECONDARY][:len(names)] or [Theme.PRIMARY]
            bars = ax.bar(names, accs, color=bar_colors[:len(names)] if len(bar_colors) == len(names)
                           else [Theme.PRIMARY, Theme.ACCENT][:len(names)])
            for b, a in zip(bars, accs):
                ax.text(b.get_x() + b.get_width() / 2, a + 1, f"{a:.1f}%",
                        ha="center", fontsize=8, color=Theme.TEXT)
            ax.set_ylim(0, 110)
            ax.set_ylabel("Accuracy (%)", fontsize=8)
            ax.tick_params(labelsize=8)
            fig.tight_layout()
            self._embed_figure(self.acc_chart_holder, fig)
        else:
            self._empty_chart_message(self.acc_chart_holder, "Train one or more models to compare accuracy here.")

        # ---- Confusion Matrix Heatmap --------------------------------------
        active = self.engine.active_model_name
        if active and active in self.engine.results:
            cm = self.engine.results[active]["confusion_matrix"]
            fig = Figure(figsize=(5.6, 3.6), dpi=100)
            ax = fig.add_subplot(111)
            im = ax.imshow(cm, cmap="Blues")
            ax.set_xticks(range(len(self.engine.target_names)))
            ax.set_yticks(range(len(self.engine.target_names)))
            ax.set_xticklabels(self.engine.target_names, fontsize=7, rotation=20)
            ax.set_yticklabels(self.engine.target_names, fontsize=7)
            ax.set_xlabel("Predicted", fontsize=8)
            ax.set_ylabel("Actual", fontsize=8)
            for i in range(cm.shape[0]):
                for j in range(cm.shape[1]):
                    ax.text(j, i, str(cm[i, j]), ha="center", va="center",
                            color="white" if cm[i, j] > cm.max() / 2 else Theme.TEXT,
                            fontsize=9, fontweight="bold")
            ax.set_title(f"{active}", fontsize=9)
            fig.tight_layout()
            self._embed_figure(self.cm_chart_holder, fig)
        else:
            self._empty_chart_message(self.cm_chart_holder, "Train a model to view its confusion matrix.")

        # ---- Feature Importance --------------------------------------------
        if active:
            importance = self.engine.get_feature_importance(active)
            fig = Figure(figsize=(5.6, 3.6), dpi=100)
            ax = fig.add_subplot(111)
            if importance:
                feats = list(importance.keys())
                vals = list(importance.values())
                ax.barh(feats, vals, color=Theme.ACCENT)
                ax.set_xlabel("Importance", fontsize=8)
                ax.tick_params(labelsize=7)
            else:
                ax.text(0.5, 0.5, f"{active} does not expose\nfeature importances.",
                        ha="center", va="center", fontsize=9, color=Theme.TEXT_MUTED)
                ax.axis("off")
            fig.tight_layout()
            self._embed_figure(self.fi_chart_holder, fig)
        else:
            self._empty_chart_message(self.fi_chart_holder, "Train a model to view prediction analytics.")

    # ============================================================ PAGE 5 ==
    # AI PREDICTION LAB
    # =========================================================================
    CLASS_EXPLANATIONS = {
        "setosa": "Iris Setosa is easily distinguished by its notably small "
                   "petals and short, broad sepals - it is almost always "
                   "linearly separable from the other two species.",
        "versicolor": "Iris Versicolor sits in the middle range of petal and "
                       "sepal measurements, making it the species most often "
                       "confused with Virginica near decision boundaries.",
        "virginica": "Iris Virginica generally has the largest petals and "
                      "sepals among the three species, typically yielding "
                      "the highest measurement values in the dataset.",
    }

    def _build_predict_page(self, page):
        scroll = self._make_scrollable(page)

        tk.Label(scroll, text="AI Prediction Lab", font=(Theme.FONT_FAMILY, 16, "bold"),
                 bg=Theme.BG, fg=Theme.TEXT).pack(anchor="w", padx=28, pady=(22, 10))

        body = tk.Frame(scroll, bg=Theme.BG)
        body.pack(fill="both", expand=True, padx=28, pady=(0, 24))

        # ---- Left: input form ----------------------------------------
        form_card = RoundedCard(body, width=460, height=520, radius=18)
        form_card.pack(side="left", fill="y", padx=(0, 14))

        tk.Label(form_card.inner, text="Sample Input", font=(Theme.FONT_FAMILY, 12, "bold"),
                 bg=Theme.CARD_BG, fg=Theme.TEXT).pack(anchor="w", padx=20, pady=(18, 4))
        tk.Label(form_card.inner, text="Enter flower measurements (in centimeters)",
                 font=(Theme.FONT_FAMILY, 9), bg=Theme.CARD_BG,
                 fg=Theme.TEXT_FAINT).pack(anchor="w", padx=20, pady=(0, 14))

        self.predict_inputs = {}
        defaults = [5.1, 3.5, 1.4, 0.2]  # a real setosa sample, sensible default
        feature_labels = ["Sepal Length", "Sepal Width", "Petal Length", "Petal Width"]

        for i, label in enumerate(feature_labels):
            row = tk.Frame(form_card.inner, bg=Theme.CARD_BG)
            row.pack(fill="x", padx=20, pady=8)
            tk.Label(row, text=label, font=(Theme.FONT_FAMILY, 10), bg=Theme.CARD_BG,
                     fg=Theme.TEXT_MUTED, width=14, anchor="w").pack(side="left")

            var = tk.DoubleVar(value=defaults[i])
            entry_card = RoundedCard(row, width=180, height=34, radius=10)
            entry_card.pack(side="left")
            entry = tk.Entry(entry_card.inner, textvariable=var, bg=Theme.CARD_BG,
                              fg=Theme.TEXT, relief="flat", insertbackground=Theme.TEXT,
                              font=(Theme.FONT_FAMILY, 10), justify="center")
            entry.pack(fill="both", expand=True, padx=8, pady=4)
            self.predict_inputs[label] = var

        tk.Label(form_card.inner, text="MODEL TO USE",
                 font=(Theme.FONT_FAMILY, 8, "bold"), bg=Theme.CARD_BG,
                 fg=Theme.TEXT_MUTED).pack(anchor="w", padx=20, pady=(14, 4))

        self.predict_model_var = tk.StringVar(value="")
        self.predict_model_dropdown = ttk.Combobox(
            form_card.inner, textvariable=self.predict_model_var, state="readonly",
            values=[], font=(Theme.FONT_FAMILY, 10)
        )
        self.predict_model_dropdown.pack(fill="x", padx=20, pady=(0, 16))

        self.predict_btn = GlowButton(form_card.inner, text="Predict", icon="\u26A1",
                                       command=self.action_predict, width=200, height=46,
                                       color1=Theme.PRIMARY, color2=Theme.ACCENT)
        self.predict_btn.pack(padx=20, pady=(4, 8))

        sample_btn = GlowButton(form_card.inner, text="Random Sample", icon="\U0001F3B2",
                                 command=self.action_fill_random_sample, width=200, height=38,
                                 color1=Theme.SECONDARY, color2=Theme.PRIMARY, font_size=9)
        sample_btn.pack(padx=20)

        # ---- Right: result card -----------------------------------------
        result_card = RoundedCard(body, width=700, height=520, radius=18)
        result_card.pack(side="left", fill="both", expand=True)

        tk.Label(result_card.inner, text="Prediction Result",
                 font=(Theme.FONT_FAMILY, 12, "bold"), bg=Theme.CARD_BG,
                 fg=Theme.TEXT).pack(anchor="w", padx=20, pady=(18, 10))

        self.result_inner = RoundedCard(result_card.inner, width=640, height=190, radius=16,
                                         bg=Theme.BG_SECONDARY)
        self.result_inner.pack(padx=20, fill="x")

        self.predicted_class_var = tk.StringVar(value="Awaiting prediction...")
        tk.Label(self.result_inner.inner, text="PREDICTED CLASS",
                 font=(Theme.FONT_FAMILY, 8, "bold"), bg=Theme.BG_SECONDARY,
                 fg=Theme.TEXT_MUTED).pack(anchor="w", padx=20, pady=(18, 2))
        self.predicted_class_lbl = tk.Label(self.result_inner.inner, textvariable=self.predicted_class_var,
                                             font=(Theme.FONT_FAMILY, 24, "bold"),
                                             bg=Theme.BG_SECONDARY, fg=Theme.ACCENT)
        self.predicted_class_lbl.pack(anchor="w", padx=20)

        conf_row = tk.Frame(self.result_inner.inner, bg=Theme.BG_SECONDARY)
        conf_row.pack(fill="x", padx=20, pady=(10, 16))
        tk.Label(conf_row, text="Confidence Score:", font=(Theme.FONT_FAMILY, 9),
                 bg=Theme.BG_SECONDARY, fg=Theme.TEXT_MUTED).pack(side="left")
        self.confidence_bar = AnimatedProgressBar(conf_row, width=300, height=12)
        self.confidence_bar.pack(side="left", padx=10)
        self.confidence_label = tk.Label(conf_row, text="--", font=(Theme.FONT_FAMILY, 9, "bold"),
                                          bg=Theme.BG_SECONDARY, fg=Theme.SUCCESS)
        self.confidence_label.pack(side="left")

        tk.Label(result_card.inner, text="Class Probabilities",
                 font=(Theme.FONT_FAMILY, 10, "bold"), bg=Theme.CARD_BG,
                 fg=Theme.TEXT).pack(anchor="w", padx=20, pady=(16, 6))

        self.proba_frame = tk.Frame(result_card.inner, bg=Theme.CARD_BG)
        self.proba_frame.pack(fill="x", padx=20)
        self.proba_bars = {}
        for cls in ["setosa", "versicolor", "virginica"]:
            row = tk.Frame(self.proba_frame, bg=Theme.CARD_BG)
            row.pack(fill="x", pady=3)
            tk.Label(row, text=cls, font=(Theme.FONT_FAMILY, 9), bg=Theme.CARD_BG,
                     fg=Theme.TEXT_MUTED, width=12, anchor="w").pack(side="left")
            bar = AnimatedProgressBar(row, width=380, height=10)
            bar.pack(side="left", padx=8)
            val_lbl = tk.Label(row, text="0%", font=(Theme.FONT_FAMILY, 9),
                                bg=Theme.CARD_BG, fg=Theme.TEXT_MUTED, width=6)
            val_lbl.pack(side="left")
            self.proba_bars[cls] = (bar, val_lbl)

        tk.Label(result_card.inner, text="Class Explanation",
                 font=(Theme.FONT_FAMILY, 10, "bold"), bg=Theme.CARD_BG,
                 fg=Theme.TEXT).pack(anchor="w", padx=20, pady=(16, 4))
        self.explanation_var = tk.StringVar(
            value="Run a prediction to see a short explanation of the predicted species.")
        tk.Label(result_card.inner, textvariable=self.explanation_var,
                 font=(Theme.FONT_FAMILY, 9), bg=Theme.CARD_BG, fg=Theme.TEXT_MUTED,
                 wraplength=620, justify="left").pack(anchor="w", padx=20, pady=(0, 16))

    def _refresh_predict_model_choices(self):
        if not hasattr(self, "predict_model_dropdown"):
            return
        trained = list(self.engine.models.keys())
        self.predict_model_dropdown.configure(values=trained)
        if trained:
            if self.predict_model_var.get() not in trained:
                self.predict_model_var.set(self.engine.active_model_name or trained[-1])
            self.predict_btn.set_disabled(False)
        else:
            self.predict_model_var.set("")
            self.predict_btn.set_disabled(True)

    def action_fill_random_sample(self):
        if self.engine.dataframe is None:
            messagebox.showwarning("No Dataset", "Load the dataset first to draw a random sample.")
            return
        row = self.engine.dataframe.sample(1).iloc[0]
        labels = ["Sepal Length", "Sepal Width", "Petal Length", "Petal Width"]
        for label, feat in zip(labels, self.engine.feature_names):
            self.predict_inputs[label].set(round(float(row[feat]), 2))
        self.set_status(f"Loaded a random '{row['species']}' sample", Theme.ACCENT)

    def action_predict(self):
        model_name = self.predict_model_var.get()
        if not model_name:
            messagebox.showwarning("No Model", "Train a model first from the Training Center.")
            return
        try:
            values = [self.predict_inputs[l].get() for l in
                      ["Sepal Length", "Sepal Width", "Petal Length", "Petal Width"]]
        except tk.TclError:
            messagebox.showerror("Invalid Input", "Please enter valid numeric measurements.")
            return

        try:
            pred_class, confidence, proba = self.engine.predict_single(model_name, values)
        except Exception as e:
            messagebox.showerror("Prediction Error", str(e))
            return

        self.predicted_class_var.set(pred_class.capitalize())
        if confidence is not None:
            self.confidence_bar.animate_to(confidence, duration_ms=600)
            self.confidence_label.configure(text=f"{confidence*100:.1f}%")
        else:
            self.confidence_bar.set_progress(0)
            self.confidence_label.configure(text="N/A")

        for cls, (bar, val_lbl) in self.proba_bars.items():
            p = proba.get(cls, 0.0)
            bar.animate_to(p, duration_ms=500)
            val_lbl.configure(text=f"{p*100:.1f}%")

        self.explanation_var.set(self.CLASS_EXPLANATIONS.get(
            pred_class, "No explanation available for this class."))

        self.set_status(f"Prediction: {pred_class} ({(confidence or 0)*100:.1f}% confidence)",
                         Theme.SUCCESS)

    # ============================================================ PAGE 6 ==
    # ABOUT PROJECT
    # =========================================================================
    def _build_about_page(self, page):
        scroll = self._make_scrollable(page)

        card = RoundedCard(scroll, width=1280, height=560, radius=18)
        card.pack(padx=28, pady=24, fill="both", expand=True)

        tk.Label(card.inner, text="\u2728 About This Project", font=(Theme.FONT_FAMILY, 16, "bold"),
                 bg=Theme.CARD_BG, fg=Theme.TEXT).pack(anchor="w", padx=24, pady=(22, 6))

        about_text = (
            "AI Data Classification System - DecodeLabs Project 2\n\n"
            "This application is a full, working demonstration of a supervised "
            "machine learning pipeline wrapped in a modern, premium desktop "
            "interface. It showcases the complete workflow expected in a "
            "professional AI/ML project:\n\n"
            "  1. Data Loading - the classic Iris flower dataset (150 samples, "
            "4 numeric features, 3 balanced species classes) is loaded directly "
            "from scikit-learn.\n\n"
            "  2. Preprocessing - features are standardized using "
            "StandardScaler before being passed to the models.\n\n"
            "  3. Train/Test Split - an 80/20 (configurable) stratified split "
            "ensures fair class representation in both partitions.\n\n"
            "  4. Model Training - both a Decision Tree and a Random Forest "
            "classifier can be trained and compared side-by-side.\n\n"
            "  5. Evaluation - accuracy score, a full classification report "
            "(precision/recall/F1), and a confusion matrix heatmap are "
            "generated for every trained model.\n\n"
            "  6. Real-Time Prediction - users can enter custom flower "
            "measurements (or draw a random sample) and get an instant "
            "prediction with a confidence score and a plain-language "
            "explanation of the predicted class.\n\n"
            "  7. Export & Persistence - results can be exported to CSV and "
            "trained models can be serialized to .pkl files for reuse.\n\n"
            "Tech Stack: Python \u2022 Tkinter \u2022 ttkbootstrap \u2022 Scikit-Learn \u2022 "
            "Pandas \u2022 NumPy \u2022 Matplotlib\n\n"
            "Design Language: Premium dark theme, glass-style rounded cards, "
            "gradient accent buttons with hover glow, animated progress "
            "indicators, and a persistent sidebar dashboard navigation - all "
            "built using native Tkinter drawing primitives."
        )

        text_widget = tk.Text(card.inner, bg=Theme.CARD_BG, fg=Theme.TEXT_MUTED,
                               font=(Theme.FONT_FAMILY, 10), relief="flat", wrap="word",
                               highlightthickness=0, padx=24, pady=4)
        text_widget.pack(fill="both", expand=True, padx=4, pady=(0, 20))
        text_widget.insert("1.0", about_text)
        text_widget.configure(state="disabled")

    # ------------------------------------------------------------------ run --
    def run(self):
        self.root.mainloop()


# ==============================================================================
# ENTRY POINT
# ==============================================================================
def main():
    """Application entry point with top-level error handling."""
    try:
        app = AIClassificationApp()
        app.run()
    except Exception as exc:
        # Last-resort error surface in case the GUI itself fails to init
        print("Fatal error while starting the AI Classification System:", file=sys.stderr)
        traceback.print_exc()
        try:
            import tkinter.messagebox as mb
            mb.showerror("Fatal Error", f"The application failed to start:\n\n{exc}")
        except Exception:
            pass
        sys.exit(1)


if __name__ == "__main__":
    main()