"""
IATRO Design System
Palantir-inspired component library with coherent design patterns
"""

import customtkinter as ctk
from typing import Optional, Callable, List, Tuple


# ==================== Color Palette ====================
# Centralized color dictionary matching main.py design
COLORS = {
    # Background layers
    "bg_primary": "#0d1117",      # Main app background
    "bg_medium": "#161b22",       # Cards, panels
    "bg_light": "#21262d",        # Subtle sections
    "bg_hover": "#30363d",        # Interactive hover state
    
    # Text hierarchy
    "text_primary": "#f0f6fc",    # Main text (brightest white)
    "text_secondary": "#c9d1d9",  # Secondary text
    "text_muted": "#8b949e",      # Tertiary/muted text
    "text_dim": "#6e7681",        # Disabled/dim text
    
    # Accent colors
    "accent": "#58a6ff",          # Main accent (blue)
    "accent_hover": "#79c0ff",    # Hover state
    "selected": "#1f6feb",        # Selected/active
    "selected_subtle": "#0d47a1", # Subtle background
    
    # Status colors
    "success": "#3fb950",         # Success/positive
    "warning": "#d29922",         # Warning
    "danger": "#f85149",          # Error/danger
    "info": "#58a6ff",            # Information
    
    # Structural
    "border": "#30363d",          # Borders
    "divider": "#21262d",         # Dividers
    "card_bg": "#21262d",         # Card background
}


class Colors:
    """Centralized color management - Palantir-inspired dark theme"""
    
    # Background layers
    BG_PRIMARY = "#0d1117"      # Deepest - main app background
    BG_SECONDARY = "#161b22"    # Cards, panels
    BG_TERTIARY = "#21262d"     # Subtle sections
    BG_HOVER = "#30363d"        # Interactive hover state
    
    # Text hierarchy
    TEXT_PRIMARY = "#f0f6fc"    # Main text (brightest white)
    TEXT_SECONDARY = "#c9d1d9"  # Secondary text
    TEXT_TERTIARY = "#8b949e"   # Tertiary/muted text
    TEXT_DISABLED = "#6e7681"   # Disabled/dim text
    
    # Accent colors
    ACCENT_PRIMARY = "#58a6ff"  # Main accent (blue)
    ACCENT_HOVER = "#79c0ff"    # Hover state
    ACCENT_ACTIVE = "#1f6feb"   # Active/selected
    ACCENT_SUBTLE = "#0d47a1"   # Subtle background
    
    # Status colors
    SUCCESS = "#3fb950"         # Success/positive
    WARNING = "#d29922"         # Warning
    DANGER = "#f85149"          # Error/danger
    INFO = "#58a6ff"            # Information
    
    # Structural
    BORDER = "#30363d"          # Borders
    DIVIDER = "#21262d"         # Dividers
    SHADOW = "#000000"          # Shadow base


# ==================== Typography ====================
class Typography:
    """Font system with hierarchy - lazy loaded to avoid early font initialization"""
    
    _fonts = {}
    
    @classmethod
    def _get_font(cls, family, size, weight):
        """Lazily create and cache fonts"""
        key = (family, size, weight)
        if key not in cls._fonts:
            cls._fonts[key] = ctk.CTkFont(family=family, size=size, weight=weight)
        return cls._fonts[key]
    
    @property
    def DISPLAY_LARGE(self):
        return self._get_font("Helvetica", 28, "normal")
    
    @property
    def DISPLAY_MEDIUM(self):
        return self._get_font("Helvetica", 22, "normal")
    
    @property
    def HEADING_1(self):
        return self._get_font("Helvetica", 18, "normal")
    
    @property
    def HEADING_2(self):
        return self._get_font("Helvetica", 15, "normal")
    
    @property
    def HEADING_3(self):
        return self._get_font("Helvetica", 13, "normal")
    
    @property
    def BODY_LARGE(self):
        return self._get_font("Helvetica", 12, "normal")
    
    @property
    def BODY_MEDIUM(self):
        return self._get_font("Helvetica", 11, "normal")
    
    @property
    def BODY_SMALL(self):
        return self._get_font("Helvetica", 10, "normal")
    
    @property
    def LABEL_LARGE(self):
        return self._get_font("Helvetica", 11, "normal")
    
    @property
    def LABEL_MEDIUM(self):
        return self._get_font("Helvetica", 10, "normal")
    
    @property
    def LABEL_SMALL(self):
        return self._get_font("Helvetica", 9, "normal")
    
    @property
    def MONO_MEDIUM(self):
        return self._get_font("Courier", 11, "normal")
    
    @property
    def MONO_SMALL(self):
        return self._get_font("Courier", 10, "normal")


# ==================== Spacing System ====================
class Spacing:
    """Consistent spacing scale (4px base)"""
    XS = 4
    SM = 8
    MD = 12
    LG = 16
    XL = 20
    XXL = 24
    XXXL = 32


# ==================== Radius System ====================
class Radius:
    """Consistent corner radius (sharp modern look)"""
    NONE = 0
    SM = 2
    MD = 4
    LG = 6
    XL = 8


# ==================== Base Components ====================

class BaseFrame(ctk.CTkFrame):
    """Base frame with design system defaults"""
    
    def __init__(self, parent, bg_color: str = Colors.BG_SECONDARY, 
                 corner_radius: int = Radius.MD, padding: int = 0, **kwargs):
        super().__init__(
            parent,
            fg_color=bg_color,
            corner_radius=corner_radius,
            **kwargs
        )
        if padding > 0:
            self.grid_rowconfigure(0, pad=padding)
            self.grid_columnconfigure(0, pad=padding)


class Card(BaseFrame):
    """Card component - elevated container with border"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            bg_color=Colors.BG_SECONDARY,
            corner_radius=Radius.MD,
            **kwargs
        )
        self.configure(border_width=1, border_color=Colors.BORDER)


class Button(ctk.CTkButton):
    """Unified button component with sharp edges and smooth animations"""
    
    def __init__(self, parent, text: str = "", variant: str = "primary",
                 size: str = "md", width: int = None, **kwargs):
        """
        Args:
            variant: "primary", "secondary", "success", "danger", "ghost"
            size: "sm", "md", "lg"
        """
        
        # Size mappings
        sizes = {
            "sm": {"height": 28, "font": Typography().LABEL_SMALL},
            "md": {"height": 36, "font": Typography().LABEL_LARGE},
            "lg": {"height": 44, "font": Typography().BODY_LARGE},
        }
        size_config = sizes.get(size, sizes["md"])
        
        # Variant mappings
        variants = {
            "primary": {
                "fg_color": Colors.ACCENT_PRIMARY,
                "hover_color": Colors.ACCENT_HOVER,
                "text_color": Colors.TEXT_PRIMARY,
                "border_width": 0,
            },
            "secondary": {
                "fg_color": Colors.BG_TERTIARY,
                "hover_color": Colors.BG_HOVER,
                "text_color": Colors.TEXT_PRIMARY,
                "border_width": 1,
                "border_color": Colors.BORDER,
            },
            "white": {
                "fg_color": "#ffffff",
                "hover_color": "#f5f5f5",
                "text_color": "#000000",
                "border_width": 0,
            },
            "grey": {
                "fg_color": Colors.BG_TERTIARY,
                "hover_color": Colors.BG_HOVER,
                "text_color": Colors.TEXT_PRIMARY,
                "border_width": 0,
            },
            "success": {
                "fg_color": Colors.SUCCESS,
                "hover_color": "#4ac960",
                "text_color": Colors.TEXT_PRIMARY,
                "border_width": 0,
            },
            "danger": {
                "fg_color": Colors.DANGER,
                "hover_color": "#f97a6c",
                "text_color": Colors.TEXT_PRIMARY,
                "border_width": 0,
            },
            "ghost": {
                "fg_color": "transparent",
                "hover_color": Colors.BG_HOVER,
                "text_color": Colors.ACCENT_PRIMARY,
                "border_width": 1,
                "border_color": Colors.ACCENT_PRIMARY,
            },
        }
        variant_config = variants.get(variant, variants["primary"])
        
        # Handle width - if not specified, let CTkButton auto-size
        init_kwargs = {
            "text": text,
            "font": size_config["font"],
            "height": size_config["height"],
            "corner_radius": Radius.SM,
            "cursor": "hand2",
        }
        
        if width is not None:
            init_kwargs["width"] = width
        
        init_kwargs.update(variant_config)
        init_kwargs.update(kwargs)
        
        super().__init__(parent, **init_kwargs)


class Label(ctk.CTkLabel):
    """Unified label component with design system fonts"""
    
    def __init__(self, parent, text: str = "", variant: str = "body_medium", **kwargs):
        """
        Args:
            variant: "display_large", "display_medium", "heading_1", "heading_2", "heading_3",
                    "body_large", "body_medium", "body_small", "label_large", "label_medium",
                    "label_small"
        """
        
        typo = Typography()
        font_map = {
            "display_large": typo.DISPLAY_LARGE,
            "display_medium": typo.DISPLAY_MEDIUM,
            "heading_1": typo.HEADING_1,
            "heading_2": typo.HEADING_2,
            "heading_3": typo.HEADING_3,
            "body_large": typo.BODY_LARGE,
            "body_medium": typo.BODY_MEDIUM,
            "body_small": typo.BODY_SMALL,
            "label_large": typo.LABEL_LARGE,
            "label_medium": typo.LABEL_MEDIUM,
            "label_small": typo.LABEL_SMALL,
        }
        
        font = font_map.get(variant, Typography.BODY_MEDIUM)
        text_color = kwargs.pop("text_color", Colors.TEXT_PRIMARY)
        
        super().__init__(
            parent,
            text=text,
            font=font,
            text_color=text_color,
            **kwargs
        )


class SectionHeader(BaseFrame):
    """Section header with title and optional action button"""
    
    def __init__(self, parent, title: str = "", action_text: str = None, 
                 action_command: Callable = None, **kwargs):
        super().__init__(parent, bg_color="transparent", corner_radius=0, **kwargs)
        
        self.pack(fill="x", pady=(Spacing.LG, Spacing.MD))
        
        # Title
        title_label = Label(self, text=title, variant="heading_2", text_color=Colors.TEXT_PRIMARY)
        title_label.pack(side="left", padx=(Spacing.LG, Spacing.MD))
        
        # Action button if provided
        self.action_btn = None
        if action_text and action_command:
            self.action_btn = Button(
                self,
                text=action_text,
                variant="secondary",
                size="sm",
                command=action_command
            )
            self.action_btn.pack(side="right", padx=Spacing.LG)


class StatCard(Card):
    """Compact stat display card"""
    
    def __init__(self, parent, label: str = "", value: str = "", 
                 icon_text: str = "", status: str = "neutral", **kwargs):
        """
        Args:
            label: Stat label/description
            value: Stat value (main display)
            status: "neutral", "success", "warning", "danger"
        """
        super().__init__(parent, **kwargs)
        
        # Status colors
        status_colors = {
            "neutral": Colors.TEXT_PRIMARY,
            "success": Colors.SUCCESS,
            "warning": Colors.WARNING,
            "danger": Colors.DANGER,
        }
        color = status_colors.get(status, Colors.TEXT_PRIMARY)
        
        # Icon/label
        if icon_text:
            icon_label = Label(self, text=icon_text, variant="label_small", 
                             text_color=Colors.TEXT_TERTIARY)
            icon_label.pack(anchor="w", padx=Spacing.MD, pady=(Spacing.MD, Spacing.SM))
        
        # Value (large and prominent)
        value_label = Label(self, text=value, variant="heading_1", text_color=color)
        value_label.pack(anchor="w", padx=Spacing.MD, pady=Spacing.SM)
        
        # Description
        label_widget = Label(self, text=label, variant="body_small", 
                           text_color=Colors.TEXT_TERTIARY)
        label_widget.pack(anchor="w", padx=Spacing.MD, pady=(Spacing.SM, Spacing.MD))


class ProgressBar(ctk.CTkProgressBar):
    """Unified progress bar with design system styling"""
    
    def __init__(self, parent, width: int = 400, height: int = 6, **kwargs):
        super().__init__(
            parent,
            width=width,
            height=height,
            progress_color=Colors.ACCENT_PRIMARY,
            fg_color=Colors.BG_TERTIARY,
            corner_radius=height // 2,
            **kwargs
        )


class ScrollableFrame(ctk.CTkScrollableFrame):
    """Unified scrollable frame with design system styling"""
    
    def __init__(self, parent, bg_color: str = Colors.BG_TERTIARY, **kwargs):
        super().__init__(
            parent,
            fg_color=bg_color,
            corner_radius=Radius.MD,
            **kwargs
        )


class Divider(BaseFrame):
    """Visual divider/separator"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            bg_color=Colors.DIVIDER,
            corner_radius=0,
            height=1,
            **kwargs
        )
        self.pack(fill="x", pady=Spacing.MD)


class Badge(BaseFrame):
    """Small badge for status/tags"""
    
    def __init__(self, parent, text: str = "", status: str = "neutral", **kwargs):
        """
        Args:
            status: "neutral", "success", "warning", "danger", "info"
        """
        
        bg_colors = {
            "neutral": Colors.BG_TERTIARY,
            "success": "#1f4620",
            "warning": "#4a3700",
            "danger": "#5a1f1f",
            "info": "#0d47a1",
        }
        
        text_colors = {
            "neutral": Colors.TEXT_SECONDARY,
            "success": Colors.SUCCESS,
            "warning": Colors.WARNING,
            "danger": Colors.DANGER,
            "info": Colors.ACCENT_PRIMARY,
        }
        
        super().__init__(
            parent,
            bg_color=bg_colors.get(status, Colors.BG_TERTIARY),
            corner_radius=Radius.SM,
            **kwargs
        )
        
        label = Label(
            self,
            text=text,
            variant="label_small",
            text_color=text_colors.get(status, Colors.TEXT_SECONDARY)
        )
        label.pack(padx=Spacing.SM, pady=Spacing.XS)


class RankedListItem(Card):
    """List item with rank number and content"""
    
    def __init__(self, parent, rank: int = 0, title: str = "", 
                 subtitle: str = "", value: str = "", 
                 value_color: str = Colors.SUCCESS, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.pack(fill="x", padx=Spacing.MD, pady=Spacing.SM)
        
        # Header: rank + title + value
        header = BaseFrame(self, bg_color="transparent", corner_radius=0)
        header.pack(fill="x", padx=Spacing.MD, pady=(Spacing.MD, Spacing.SM))
        
        # Rank badge
        rank_badge = Badge(header, text=f"#{rank}", status="info")
        rank_badge.pack(side="left", padx=(0, Spacing.MD))
        
        # Title
        title_label = Label(header, text=title, variant="body_large", 
                          text_color=Colors.TEXT_PRIMARY)
        title_label.pack(side="left", padx=(0, Spacing.MD))
        
        # Value (right aligned)
        if value:
            value_label = Label(header, text=value, variant="label_large", 
                              text_color=value_color)
            value_label.pack(side="right")
        
        # Subtitle if provided
        if subtitle:
            subtitle_label = Label(self, text=subtitle, variant="body_small", 
                                 text_color=Colors.TEXT_TERTIARY)
            subtitle_label.pack(fill="x", padx=Spacing.MD, pady=(0, Spacing.MD))


class TabView(ctk.CTkTabview):
    """Unified tab view with design system styling"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            fg_color=Colors.BG_SECONDARY,
            segmented_button_fg_color=Colors.BG_TERTIARY,
            text_color=Colors.TEXT_PRIMARY,
            **kwargs
        )
        
        # Style segment buttons
        self._segmented_button.configure(
            font=Typography.LABEL_MEDIUM,
        )


class OptionButton(ctk.CTkButton):
    """Button for selectable options (cards that can be clicked)"""
    
    def __init__(self, parent, title: str = "", description: str = "", 
                 is_selected: bool = False, command: Callable = None, **kwargs):
        
        bg_color = Colors.BG_HOVER if is_selected else Colors.BG_TERTIARY
        border_color = Colors.ACCENT_PRIMARY if is_selected else Colors.BORDER
        border_width = 2 if is_selected else 1
        
        super().__init__(
            parent,
            text="",
            fg_color=bg_color,
            hover_color=Colors.BG_HOVER,
            border_width=border_width,
            border_color=border_color,
            corner_radius=Radius.MD,
            command=command,
            **kwargs
        )
        
        # Content frame
        content_frame = BaseFrame(self, bg_color="transparent", corner_radius=0)
        content_frame.pack(fill="both", expand=True, padx=Spacing.MD, pady=Spacing.MD)
        
        # Title
        title_label = Label(
            content_frame,
            text=title,
            variant="body_large",
            text_color=Colors.TEXT_PRIMARY
        )
        title_label.pack(anchor="w", padx=(0, Spacing.LG))
        
        # Description
        if description:
            desc_label = Label(
                content_frame,
                text=description,
                variant="body_small",
                text_color=Colors.TEXT_TERTIARY,
                wraplength=400,
                justify="left"
            )
            desc_label.pack(anchor="w", fill="x", pady=(Spacing.SM, 0))


class ConfirmationDialog(ctk.CTkToplevel):
    """Standard confirmation dialog"""
    
    def __init__(self, parent, title: str = "Confirm", 
                 message: str = "", callback: Callable = None,
                 button_text: str = "Confirm", button_variant: str = "primary"):
        super().__init__(parent)
        self.title(title)
        self.geometry("400x200")
        self.configure(fg_color=Colors.BG_PRIMARY)
        
        self.result = False
        self.callback = callback
        
        # Message
        msg_label = Label(
            self,
            text=message,
            variant="body_large",
            text_color=Colors.TEXT_PRIMARY,
            wraplength=350
        )
        msg_label.pack(pady=(Spacing.XL, Spacing.LG), padx=Spacing.LG)
        
        # Buttons frame
        btn_frame = BaseFrame(self, bg_color="transparent", corner_radius=0)
        btn_frame.pack(fill="x", padx=Spacing.LG, pady=Spacing.LG)
        
        # Cancel button
        cancel_btn = Button(
            btn_frame,
            text="Cancel",
            variant="secondary",
            command=self.cancel
        )
        cancel_btn.pack(side="left", padx=(0, Spacing.MD))
        
        # Confirm button
        confirm_btn = Button(
            btn_frame,
            text=button_text,
            variant=button_variant,
            command=self.confirm
        )
        confirm_btn.pack(side="left")
    
    def confirm(self):
        self.result = True
        if self.callback:
            self.callback(True)
        self.destroy()
    
    def cancel(self):
        self.result = False
        if self.callback:
            self.callback(False)
        self.destroy()


class EmptyState(BaseFrame):
    """Empty state placeholder with icon and message"""
    
    def __init__(self, parent, icon_text: str = "●", 
                 title: str = "", message: str = "", **kwargs):
        super().__init__(parent, bg_color="transparent", corner_radius=0, **kwargs)
        
        self.pack(fill="both", expand=True)
        
        # Icon
        icon_label = Label(self, text=icon_text, variant="display_large",
                         text_color=Colors.TEXT_TERTIARY)
        icon_label.pack(pady=(Spacing.XXL, Spacing.LG))
        
        # Title
        title_label = Label(self, text=title, variant="heading_2",
                          text_color=Colors.TEXT_PRIMARY)
        title_label.pack(pady=Spacing.SM)
        
        # Message
        msg_label = Label(self, text=message, variant="body_small",
                        text_color=Colors.TEXT_TERTIARY, wraplength=400)
        msg_label.pack(pady=Spacing.MD)


class StatusIndicator(BaseFrame):
    """Status indicator with color and label"""
    
    def __init__(self, parent, status: str = "neutral", label: str = "", **kwargs):
        """
        Args:
            status: "neutral", "success", "warning", "danger", "info"
        """
        super().__init__(parent, bg_color="transparent", corner_radius=0, **kwargs)
        
        status_colors = {
            "neutral": Colors.TEXT_TERTIARY,
            "success": Colors.SUCCESS,
            "warning": Colors.WARNING,
            "danger": Colors.DANGER,
            "info": Colors.ACCENT_PRIMARY,
        }
        
        color = status_colors.get(status, Colors.TEXT_TERTIARY)
        
        # Dot
        dot = Label(self, text="●", variant="body_small", text_color=color)
        dot.pack(side="left", padx=(0, Spacing.SM))
        
        # Label
        label_widget = Label(self, text=label, variant="body_small", text_color=color)
        label_widget.pack(side="left")


# ==================== Layout Components ====================

class Container(BaseFrame):
    """Main container with max width and padding"""
    
    def __init__(self, parent, max_width: int = None, **kwargs):
        super().__init__(parent, bg_color="transparent", corner_radius=0, **kwargs)
        if max_width:
            self.pack(fill="both", expand=True, padx=Spacing.XL, pady=Spacing.LG)


class SideBySide(BaseFrame):
    """Two-column layout with configurable split"""
    
    def __init__(self, parent, left_weight: int = 60, right_weight: int = 40, **kwargs):
        super().__init__(parent, bg_color="transparent", corner_radius=0, **kwargs)
        self.pack(fill="both", expand=True)
        
        # Left panel
        self.left = BaseFrame(self, bg_color="transparent", corner_radius=0)
        self.left.pack(side="left", fill="both", expand=True, padx=(0, Spacing.MD))
        
        # Right panel
        self.right = BaseFrame(self, bg_color="transparent", corner_radius=0)
        self.right.pack(side="right", fill="both", padx=(Spacing.MD, 0))


class Grid(BaseFrame):
    """Grid layout helper"""
    
    def __init__(self, parent, columns: int = 2, gap: int = Spacing.MD, **kwargs):
        super().__init__(parent, bg_color="transparent", corner_radius=0, **kwargs)
        self.pack(fill="both", expand=True)
        
        self.columns = columns
        self.gap = gap
        self.cell_count = 0
    
    def add_item(self, widget, **pack_kwargs):
        """Add item to grid"""
        row = self.cell_count // self.columns
        col = self.cell_count % self.columns
        
        padx = (self.gap if col > 0 else 0, 0)
        pady = (self.gap if row > 0 else 0, 0)
        
        widget.pack(fill="both", expand=True, padx=padx, pady=pady, **pack_kwargs)
        self.cell_count += 1


# ==================== New Components for main.py ====================

class TopBar(ctk.CTkFrame):
    """Top bar with title, subtitle, and new diagnosis button"""
    
    def __init__(self, parent, title="IATRO", subtitle="Pediatric Diagnostic Inference System", 
                 on_new_diagnosis=None, **kwargs):
        super().__init__(parent, fg_color=COLORS["bg_medium"], corner_radius=8, **kwargs)
        
        # Title section
        title_label = ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        title_label.pack(side="left", padx=20, pady=15)
        
        subtitle_label = ctk.CTkLabel(
            self,
            text=subtitle,
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_secondary"]
        )
        subtitle_label.pack(side="left", padx=(0, 20), pady=15)
        
        # New diagnosis button
        if on_new_diagnosis:
            new_btn = ctk.CTkButton(
                self,
                text="New Diagnosis",
                command=on_new_diagnosis,
                fg_color=COLORS["bg_light"],
                hover_color=COLORS["bg_hover"],
                font=ctk.CTkFont(size=13),
                width=140,
                height=32,
                text_color=COLORS["text_primary"],
                border_width=1,
                border_color=COLORS["border"]
            )
            new_btn.pack(side="right", padx=20, pady=15)


class SymptomCard(ctk.CTkFrame):
    """Card for a single symptom with optional confirmation"""
    
    def __init__(self, parent, symptom: str, explanation: str, is_selected: bool = False,
                 on_click: Callable = None, on_confirm: Callable = None, **kwargs):
        super().__init__(
            parent,
            fg_color=COLORS["bg_medium"] if not is_selected else COLORS["bg_hover"],
            corner_radius=6,
            border_width=1 if is_selected else 0,
            border_color=COLORS["selected"] if is_selected else None,
            **kwargs
        )
        
        # Make frame clickable
        self.bind("<Button-1>", lambda e: on_click() if on_click else None)
        
        # Content frame
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill="x", padx=15, pady=12)
        content_frame.bind("<Button-1>", lambda e: on_click() if on_click else None)
        
        # Symptom name
        name_label = ctk.CTkLabel(
            content_frame,
            text=symptom,
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_primary"],
            anchor="w"
        )
        name_label.pack(fill="x", pady=(0, 6))
        name_label.bind("<Button-1>", lambda e: on_click() if on_click else None)
        
        # Explanation
        explanation_label = ctk.CTkLabel(
            content_frame,
            text=explanation,
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_secondary"],
            anchor="w",
            wraplength=600
        )
        explanation_label.pack(fill="x")
        explanation_label.bind("<Button-1>", lambda e: on_click() if on_click else None)
        
        # Confirmation button (only shown if selected)
        if is_selected and on_confirm:
            confirm_frame = ctk.CTkFrame(self, fg_color="transparent")
            confirm_frame.pack(fill="x", padx=15, pady=(0, 12))
            
            confirm_btn = ctk.CTkButton(
                confirm_frame,
                text="Confirm Selection",
                command=on_confirm,
                fg_color="#ffffff",
                hover_color="#f0f0f0",
                font=ctk.CTkFont(size=12),
                height=32,
                text_color="#000000",
                width=200
            )
            confirm_btn.pack(side="left")


class DiagnosisCard(ctk.CTkFrame):
    """Card for a single diagnosis result"""
    
    def __init__(self, parent, rank: int, disease_name: str, probability: float,
                 severity: float = None, hits: int = None, req_hits: int = None,
                 description: str = None, **kwargs):
        
        is_top = (rank == 1)
        super().__init__(
            parent,
            fg_color=COLORS["card_bg"],
            corner_radius=6,
            border_width=1 if is_top else 0,
            border_color=COLORS["selected"] if is_top else None,
            **kwargs
        )
        
        # Header row with rank, name, and probability
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=(12, 5))
        
        rank_label = ctk.CTkLabel(
            header_frame,
            text=f"#{rank}",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["accent"]
        )
        rank_label.pack(side="left")
        
        name_label = ctk.CTkLabel(
            header_frame,
            text=disease_name,
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_primary"]
        )
        name_label.pack(side="left", padx=(10, 0))
        
        prob_label = ctk.CTkLabel(
            header_frame,
            text=f"{probability:.1%}",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["success"]
        )
        prob_label.pack(side="right")
        
        # Progress bar
        prob_bar = ctk.CTkProgressBar(
            self,
            width=400,
            height=8,
            progress_color=COLORS["accent"]
        )
        prob_bar.pack(fill="x", padx=15, pady=(0, 8))
        prob_bar.set(probability)
        
        # Details row
        details_frame = ctk.CTkFrame(self, fg_color="transparent")
        details_frame.pack(fill="x", padx=15, pady=(0, 8))
        
        if severity is not None:
            severity_label = ctk.CTkLabel(
                details_frame,
                text=f"Severity: {severity:.2f}",
                font=ctk.CTkFont(size=10),
                text_color=COLORS["text_muted"]
            )
            severity_label.pack(side="left", padx=(0, 15))
        
        if hits is not None and req_hits is not None:
            hits_label = ctk.CTkLabel(
                details_frame,
                text=f"Evidence: {hits}/{req_hits}",
                font=ctk.CTkFont(size=10),
                text_color=COLORS["text_dim"]
            )
            hits_label.pack(side="left")
        
        # Description if provided
        if description:
            desc_label = ctk.CTkLabel(
                self,
                text=description[:100] + ("..." if len(description) > 100 else ""),
                font=ctk.CTkFont(size=10),
                text_color=COLORS["text_secondary"],
                wraplength=400,
                justify="left"
            )
            desc_label.pack(fill="x", padx=15, pady=(0, 10))


class CompletionSummary(ctk.CTkFrame):
    """Summary display shown when diagnosis is complete"""
    
    def __init__(self, parent, stats_data: List[Tuple[str, str]], 
                 top_disease_name: str = "", top_diseases: List[Tuple[int, str, float, int, int]] = None,
                 symptom_path: List[str] = None, on_new_diagnosis: Callable = None, **kwargs):
        
        super().__init__(
            parent,
            fg_color=COLORS["bg_medium"],
            corner_radius=8,
            **kwargs
        )
        
        # Title section with "Patient suffers from:" label and disease name
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.pack(fill="x", padx=20, pady=(20, 15))
        
        # Disease name section
        disease_frame = ctk.CTkFrame(title_frame, fg_color="transparent")
        disease_frame.pack(fill="x", anchor="w")
        
        # Semi-transparent "Patient suffers from:" label
        patient_label = ctk.CTkLabel(
            disease_frame,
            text="Patient suffers from:",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_muted"]
        )
        patient_label.pack(anchor="w", pady=(0, 4))
        
        # Top disease name - bigger and left-aligned
        if top_disease_name:
            disease_label = ctk.CTkLabel(
                disease_frame,
                text=top_disease_name,
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color=COLORS["text_primary"],
                anchor="w"
            )
            disease_label.pack(anchor="w")
        
        # Stats section with improved table-like layout
        stats_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_light"], corner_radius=6)
        stats_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        stats_title = ctk.CTkLabel(
            stats_frame,
            text="Session Statistics",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        stats_title.pack(pady=(18, 8), padx=20, anchor="w")
        
        # Create a table-like structure for stats
        stats_table = ctk.CTkFrame(stats_frame, fg_color="transparent")
        stats_table.pack(fill="x", padx=20, pady=(0, 12))
        
        # Calculate column widths for proper alignment
        max_label_width = max(len(label) for label, _ in stats_data) if stats_data else 0
        
        # Display stats in a two-column grid with proper alignment
        for i, (label, value) in enumerate(stats_data):
            row_frame = ctk.CTkFrame(stats_table, fg_color="transparent", height=10)
            row_frame.pack(fill="x", pady=0)
            
            # Left column (label)
            label_frame = ctk.CTkFrame(row_frame, fg_color="transparent", width=200, height=10)
            label_frame.pack(side="left", fill="x", expand=False)
            label_frame.pack_propagate(False)
            
            label_widget = ctk.CTkLabel(
                label_frame,
                text=label,
                font=ctk.CTkFont(size=10),
                text_color=COLORS["text_secondary"],
                anchor="w",

            )
            label_widget.pack(side="left", padx=(0, 8), pady=0)
            
            # # Separator
            # separator = ctk.CTkLabel(
            #     row_frame,
            #     text=":",
            #     font=ctk.CTkFont(size=10),
            #     text_color=COLORS["text_muted"],
            #     height=16
            # )
            # separator.pack(side="left", padx=(0, 12), pady=0)
            
            # Right column (value)
            value_widget = ctk.CTkLabel(
                row_frame,
                text=value,
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color=COLORS["text_primary"],
                anchor="w",

            )
            value_widget.pack(side="left", fill="x", expand=True, pady=0)
        
            # Add subtle divider between rows (except last)
            if i < len(stats_data) - 1:
                divider = ctk.CTkFrame(
                    stats_table,
                    fg_color=COLORS["border"],
                    height=1
                )
                divider.pack(fill="x", padx=0, pady=0)
        
        # Top diagnoses section with improved layout
        if top_diseases:
            top_diseases_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_light"], corner_radius=6)
            top_diseases_frame.pack(fill="x", padx=20, pady=(0, 15))
            
            top_title = ctk.CTkLabel(
                top_diseases_frame,
                text="Top Diagnoses",
                font=ctk.CTkFont(size=15, weight="bold"),
                text_color=COLORS["text_primary"]
            )
            top_title.pack(pady=(18, 12), padx=20, anchor="w")
            
            # Header row for table
            header_frame = ctk.CTkFrame(top_diseases_frame, fg_color="transparent")
            header_frame.pack(fill="x", padx=20, pady=(0, 8))
            
            rank_header = ctk.CTkLabel(
                header_frame,
                text="Rank",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=COLORS["text_muted"],
                width=50
            )
            rank_header.pack(side="left", padx=(0, 15))
            
            name_header = ctk.CTkLabel(
                header_frame,
                text="Disease",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=COLORS["text_muted"],
                anchor="w"
            )
            name_header.pack(side="left", fill="x", expand=True, padx=(0, 15))
            
            prob_header = ctk.CTkLabel(
                header_frame,
                text="Probability",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=COLORS["text_muted"],
                width=100
            )
            prob_header.pack(side="left", padx=(0, 15))
            
            hits_header = ctk.CTkLabel(
                header_frame,
                text="Evidence",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=COLORS["text_muted"],
                width=80
            )
            hits_header.pack(side="right")
            
            # Divider after header
            header_divider = ctk.CTkFrame(
                top_diseases_frame,
                fg_color=COLORS["border"],
                height=1
            )
            header_divider.pack(fill="x", padx=20, pady=(0, 8))
            
            # Disease rows
            for i, (disease_id, disease_name, probability, hits, req_hits) in enumerate(top_diseases):
                disease_row = ctk.CTkFrame(top_diseases_frame, fg_color="transparent")
                disease_row.pack(fill="x", padx=20, pady=8)
                
                # Rank badge
                rank_badge = ctk.CTkLabel(
                    disease_row,
                    text=f"#{i+1}",
                    font=ctk.CTkFont(size=11, weight="bold"),
                    text_color=COLORS["accent"],
                    width=50
                )
                rank_badge.pack(side="left", padx=(0, 15))
                
                # Disease name
                name_label = ctk.CTkLabel(
                    disease_row,
                    text=disease_name,
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=COLORS["text_primary"],
                    anchor="w"
                )
                name_label.pack(side="left", fill="x", expand=True, padx=(0, 15))
                
                # Probability
                prob_label = ctk.CTkLabel(
                    disease_row,
                    text=f"{probability:.1%}",
                    font=ctk.CTkFont(size=11, weight="bold"),
                    text_color=COLORS["success"],
                    width=100
                )
                prob_label.pack(side="left", padx=(0, 15))
                
                # Evidence hits
                hits_label = ctk.CTkLabel(
                    disease_row,
                    text=f"{hits}/{req_hits}",
                    font=ctk.CTkFont(size=11),
                    text_color=COLORS["text_secondary"],
                    width=80
                )
                hits_label.pack(side="right")
        
                # Divider between rows (except last)
                if i < len(top_diseases) - 1:
                    row_divider = ctk.CTkFrame(
                        top_diseases_frame,
                        fg_color=COLORS["border"],
                        height=1
                    )
                    row_divider.pack(fill="x", padx=20, pady=2)
        
        # Symptom path section
        if symptom_path:
            symptom_path_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_light"], corner_radius=6)
            symptom_path_frame.pack(fill="x", padx=20, pady=(0, 15))
            
            path_title = ctk.CTkLabel(
                symptom_path_frame,
                text="Symptom Path",
                font=ctk.CTkFont(size=15, weight="bold"),
                text_color=COLORS["text_primary"]
            )
            path_title.pack(pady=(18, 12), padx=20, anchor="w")
            
            # Create scrollable path
            path_scroll = ctk.CTkScrollableFrame(
                symptom_path_frame,
                fg_color=COLORS["bg_light"],
                corner_radius=6,
                height=150
            )
            path_scroll.pack(fill="both", expand=True, padx=20, pady=(0, 18))
            
            # Display symptoms in order with numbers
            for i, symptom in enumerate(symptom_path, 1):
                symptom_row = ctk.CTkFrame(path_scroll, fg_color="transparent")
                symptom_row.pack(fill="x", pady=4)
                
                # Step number
                step_label = ctk.CTkLabel(
                    symptom_row,
                    text=f"{i}.",
                    font=ctk.CTkFont(size=11, weight="bold"),
                    text_color=COLORS["accent"],
                    width=30
                )
                step_label.pack(side="left", padx=(0, 10))
                
                # Symptom name
                symptom_label = ctk.CTkLabel(
                    symptom_row,
                    text=symptom,
                    font=ctk.CTkFont(size=12),
                    text_color=COLORS["text_primary"],
                    anchor="w"
                )
                symptom_label.pack(side="left", fill="x", expand=True)
        
        # New Diagnosis button - white with black text (keep same as before)
        if on_new_diagnosis:
            new_diag_btn = ctk.CTkButton(
                self,
                text="Start New Diagnosis",
                command=on_new_diagnosis,
                fg_color="#ffffff",
                hover_color="#f0f0f0",
                font=ctk.CTkFont(size=12),
                height=32,
                width=200,
                text_color="#000000",
                border_width=0
            )
            new_diag_btn.pack(pady=(5, 20))


class ConfidenceIndicator(ctk.CTkFrame):
    """Displays confidence level with progress bar"""
    
    def __init__(self, parent, confidence: float = 0.0, **kwargs):
        super().__init__(parent, fg_color=COLORS["bg_light"], corner_radius=8, **kwargs)
        
        self.confidence_label = ctk.CTkLabel(
            self,
            text=f"Confidence: {confidence:.1%}",
            font=ctk.CTkFont(size=14),
            text_color=COLORS["text_primary"]
        )
        self.confidence_label.pack(pady=15)
        
        self.confidence_progress = ctk.CTkProgressBar(
            self,
            width=400,
            height=20,
            progress_color=COLORS["accent"]
        )
        self.confidence_progress.pack(pady=(0, 15), padx=20)
        self.confidence_progress.set(confidence)
    
    def update_confidence(self, confidence: float):
        """Update confidence display"""
        self.confidence_label.configure(
            text=f"Confidence: {confidence:.1%}",
            text_color=COLORS["success"] if confidence >= 0.7 else COLORS["text_primary"]
        )
        self.confidence_progress.set(confidence)


class PanelHeader(ctk.CTkFrame):
    """Header for left/right panels with optional action button"""
    
    def __init__(self, parent, title: str = "", action_text: str = None, 
                 action_command: Callable = None, status_text: str = "", **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.pack(fill="x", padx=20, pady=(20, 10))
        
        # Title
        title_label = ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(size=16),
            text_color=COLORS["text_primary"]
        )
        title_label.pack(side="left")
        
        # Status text (optional)
        if status_text:
            self.status_label = ctk.CTkLabel(
                self,
                text=status_text,
                font=ctk.CTkFont(size=11),
                text_color=COLORS["text_muted"]
            )
            self.status_label.pack(side="right", padx=(0, 10))
        else:
            self.status_label = None
        
        # Action button (optional)
        if action_text and action_command:
            action_btn = ctk.CTkButton(
                self,
                text=action_text,
                command=action_command,
                fg_color=COLORS["bg_light"],
                hover_color=COLORS["bg_hover"],
                font=ctk.CTkFont(size=12),
                width=80,
                height=28,
                text_color=COLORS["text_secondary"],
                border_width=1,
                border_color=COLORS["border"]
            )
            action_btn.pack(side="right", padx=(10, 0))
            self.action_btn = action_btn
        else:
            self.action_btn = None
    
    def update_status(self, status_text: str):
        """Update status label"""
        if self.status_label:
            self.status_label.configure(text=status_text)


class Grid(BaseFrame):
    """Grid layout helper"""
    
    def __init__(self, parent, columns: int = 2, gap: int = Spacing.MD, **kwargs):
        super().__init__(parent, bg_color="transparent", corner_radius=0, **kwargs)
        self.pack(fill="both", expand=True)
        
        self.columns = columns
        self.gap = gap
        self.cell_count = 0
    
    def add_item(self, widget, **pack_kwargs):
        """Add item to grid"""
        row = self.cell_count // self.columns
        col = self.cell_count % self.columns
        
        padx = (self.gap if col > 0 else 0, 0)
        pady = (self.gap if row > 0 else 0, 0)
        
        widget.pack(fill="both", expand=True, padx=padx, pady=pady, **pack_kwargs)
        self.cell_count += 1
