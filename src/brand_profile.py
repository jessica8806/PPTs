"""
Brand Profile Schema and Models

Defines the structured data model for brand profiles extracted from
reference materials (brand guides, existing presentations, logos, websites).
"""

from dataclasses import dataclass, field, asdict
from typing import Optional
from enum import Enum
import json
import uuid
from datetime import datetime


class Confidence(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class AspectRatio(str, Enum):
    WIDESCREEN = "16:9"
    STANDARD = "4:3"
    CUSTOM = "custom"


class WhiteSpacePhilosophy(str, Enum):
    MINIMAL = "minimal"
    GENEROUS = "generous"
    STRUCTURED = "structured"


class IconStyle(str, Enum):
    LINE = "line"
    FILLED = "filled"
    DUOTONE = "duotone"
    CUSTOM = "custom"


class ShapeLanguage(str, Enum):
    ROUNDED = "rounded"
    SHARP = "sharp"
    GEOMETRIC = "geometric"
    ORGANIC = "organic"


class WritingTone(str, Enum):
    FORMAL = "formal"
    CONVERSATIONAL = "conversational"
    TECHNICAL = "technical"
    INSPIRATIONAL = "inspirational"


class HeadlineStyle(str, Enum):
    STATEMENT = "statement"
    QUESTION = "question"
    METRIC_LED = "metric-led"


@dataclass
class ColorEntry:
    hex: str
    rgb: tuple[int, int, int]
    confidence: Confidence = Confidence.MEDIUM
    usage_rule: str = ""

    def to_dict(self) -> dict:
        return {
            "hex": self.hex,
            "rgb": list(self.rgb),
            "confidence": self.confidence.value,
            "usage_rule": self.usage_rule,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "ColorEntry":
        return cls(
            hex=d["hex"],
            rgb=tuple(d["rgb"]),
            confidence=Confidence(d.get("confidence", "Medium")),
            usage_rule=d.get("usage_rule", ""),
        )


def _make_color_entry(hex_color: str, confidence: "Confidence", usage_rule: str = "") -> "ColorEntry":
    """Create a ColorEntry from a hex string (e.g. '#7C6AF7')."""
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    rgb = (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
    return ColorEntry(hex=f"#{h.upper()}", rgb=rgb, confidence=confidence, usage_rule=usage_rule)


@dataclass
class ColorPalette:
    primary: Optional[ColorEntry] = None
    secondary: list[ColorEntry] = field(default_factory=list)       # up to 4
    accent: list[ColorEntry] = field(default_factory=list)          # up to 2
    background_light: Optional[ColorEntry] = None
    background_dark: Optional[ColorEntry] = None
    text_heading: Optional[ColorEntry] = None
    text_body: Optional[ColorEntry] = None
    text_caption: Optional[ColorEntry] = None
    chart_sequence: list[ColorEntry] = field(default_factory=list)
    usage_rules: str = ""

    def to_dict(self) -> dict:
        return {
            "primary": self.primary.to_dict() if self.primary else None,
            "secondary": [c.to_dict() for c in self.secondary],
            "accent": [c.to_dict() for c in self.accent],
            "background_light": self.background_light.to_dict() if self.background_light else None,
            "background_dark": self.background_dark.to_dict() if self.background_dark else None,
            "text_heading": self.text_heading.to_dict() if self.text_heading else None,
            "text_body": self.text_body.to_dict() if self.text_body else None,
            "text_caption": self.text_caption.to_dict() if self.text_caption else None,
            "chart_sequence": [c.to_dict() for c in self.chart_sequence],
            "usage_rules": self.usage_rules,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "ColorPalette":
        return cls(
            primary=ColorEntry.from_dict(d["primary"]) if d.get("primary") else None,
            secondary=[ColorEntry.from_dict(c) for c in d.get("secondary", [])],
            accent=[ColorEntry.from_dict(c) for c in d.get("accent", [])],
            background_light=ColorEntry.from_dict(d["background_light"]) if d.get("background_light") else None,
            background_dark=ColorEntry.from_dict(d["background_dark"]) if d.get("background_dark") else None,
            text_heading=ColorEntry.from_dict(d["text_heading"]) if d.get("text_heading") else None,
            text_body=ColorEntry.from_dict(d["text_body"]) if d.get("text_body") else None,
            text_caption=ColorEntry.from_dict(d["text_caption"]) if d.get("text_caption") else None,
            chart_sequence=[ColorEntry.from_dict(c) for c in d.get("chart_sequence", [])],
            usage_rules=d.get("usage_rules", ""),
        )


@dataclass
class FontSpec:
    name: str
    fallback: str = "Arial"
    confidence: Confidence = Confidence.MEDIUM

    def to_dict(self) -> dict:
        return {"name": self.name, "fallback": self.fallback, "confidence": self.confidence.value}

    @classmethod
    def from_dict(cls, d: dict) -> "FontSpec":
        return cls(
            name=d["name"],
            fallback=d.get("fallback", "Arial"),
            confidence=Confidence(d.get("confidence", "Medium")),
        )


@dataclass
class Typography:
    heading_font: Optional[FontSpec] = None
    body_font: Optional[FontSpec] = None
    # Font sizes in points
    size_title: int = 40
    size_h1: int = 32
    size_h2: int = 24
    size_h3: int = 20
    size_body: int = 16
    size_caption: int = 12
    size_footnote: int = 10
    # Weight rules
    weight_bold_usage: str = "headlines, key metrics"
    weight_light_usage: str = "subtitles, captions"
    # Spacing
    line_spacing: float = 1.15
    paragraph_spacing: int = 8  # points
    # Alignment: "left", "center", "right"
    title_alignment: str = "left"
    body_alignment: str = "left"

    def to_dict(self) -> dict:
        return {
            "heading_font": self.heading_font.to_dict() if self.heading_font else None,
            "body_font": self.body_font.to_dict() if self.body_font else None,
            "size_title": self.size_title,
            "size_h1": self.size_h1,
            "size_h2": self.size_h2,
            "size_h3": self.size_h3,
            "size_body": self.size_body,
            "size_caption": self.size_caption,
            "size_footnote": self.size_footnote,
            "weight_bold_usage": self.weight_bold_usage,
            "weight_light_usage": self.weight_light_usage,
            "line_spacing": self.line_spacing,
            "paragraph_spacing": self.paragraph_spacing,
            "title_alignment": self.title_alignment,
            "body_alignment": self.body_alignment,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Typography":
        return cls(
            heading_font=FontSpec.from_dict(d["heading_font"]) if d.get("heading_font") else None,
            body_font=FontSpec.from_dict(d["body_font"]) if d.get("body_font") else None,
            size_title=d.get("size_title", 40),
            size_h1=d.get("size_h1", 32),
            size_h2=d.get("size_h2", 24),
            size_h3=d.get("size_h3", 20),
            size_body=d.get("size_body", 16),
            size_caption=d.get("size_caption", 12),
            size_footnote=d.get("size_footnote", 10),
            weight_bold_usage=d.get("weight_bold_usage", "headlines, key metrics"),
            weight_light_usage=d.get("weight_light_usage", "subtitles, captions"),
            line_spacing=d.get("line_spacing", 1.15),
            paragraph_spacing=d.get("paragraph_spacing", 8),
            title_alignment=d.get("title_alignment", "left"),
            body_alignment=d.get("body_alignment", "left"),
        )


@dataclass
class LayoutSpacing:
    aspect_ratio: AspectRatio = AspectRatio.WIDESCREEN
    margin_top: float = 0.5      # inches
    margin_bottom: float = 0.5
    margin_left: float = 0.75
    margin_right: float = 0.75
    content_alignment: str = "left-heavy"  # "left-heavy", "centered", "grid-based"
    max_bullets_per_slide: int = 5
    max_words_per_bullet: int = 15
    image_placement: str = "side-by-side"  # "full-bleed", "inset", "side-by-side"
    white_space: WhiteSpacePhilosophy = WhiteSpacePhilosophy.STRUCTURED

    def to_dict(self) -> dict:
        return {
            "aspect_ratio": self.aspect_ratio.value,
            "margin_top": self.margin_top,
            "margin_bottom": self.margin_bottom,
            "margin_left": self.margin_left,
            "margin_right": self.margin_right,
            "content_alignment": self.content_alignment,
            "max_bullets_per_slide": self.max_bullets_per_slide,
            "max_words_per_bullet": self.max_words_per_bullet,
            "image_placement": self.image_placement,
            "white_space": self.white_space.value,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "LayoutSpacing":
        return cls(
            aspect_ratio=AspectRatio(d.get("aspect_ratio", "16:9")),
            margin_top=d.get("margin_top", 0.5),
            margin_bottom=d.get("margin_bottom", 0.5),
            margin_left=d.get("margin_left", 0.75),
            margin_right=d.get("margin_right", 0.75),
            content_alignment=d.get("content_alignment", "left-heavy"),
            max_bullets_per_slide=d.get("max_bullets_per_slide", 5),
            max_words_per_bullet=d.get("max_words_per_bullet", 15),
            image_placement=d.get("image_placement", "side-by-side"),
            white_space=WhiteSpacePhilosophy(d.get("white_space", "structured")),
        )


@dataclass
class VisualElements:
    logo_placement: str = "top-left"   # "top-left", "top-right", "bottom-left", "bottom-right"
    logo_min_size_px: int = 60
    logo_clear_space: float = 0.25     # inches
    icon_style: IconStyle = IconStyle.LINE
    shape_language: ShapeLanguage = ShapeLanguage.ROUNDED
    corner_radius: int = 4             # points
    divider_style: str = "thin-line"   # "thin-line", "thick-bar", "none"
    background_treatment: str = "solid"  # "solid", "gradient", "textured", "image-based"
    chart_style: str = "bar"           # "bar", "line", "donut"
    chart_labels: str = "inside"       # "inside", "outside", "legend"

    def to_dict(self) -> dict:
        return {
            "logo_placement": self.logo_placement,
            "logo_min_size_px": self.logo_min_size_px,
            "logo_clear_space": self.logo_clear_space,
            "icon_style": self.icon_style.value,
            "shape_language": self.shape_language.value,
            "corner_radius": self.corner_radius,
            "divider_style": self.divider_style,
            "background_treatment": self.background_treatment,
            "chart_style": self.chart_style,
            "chart_labels": self.chart_labels,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "VisualElements":
        return cls(
            logo_placement=d.get("logo_placement", "top-left"),
            logo_min_size_px=d.get("logo_min_size_px", 60),
            logo_clear_space=d.get("logo_clear_space", 0.25),
            icon_style=IconStyle(d.get("icon_style", "line")),
            shape_language=ShapeLanguage(d.get("shape_language", "rounded")),
            corner_radius=d.get("corner_radius", 4),
            divider_style=d.get("divider_style", "thin-line"),
            background_treatment=d.get("background_treatment", "solid"),
            chart_style=d.get("chart_style", "bar"),
            chart_labels=d.get("chart_labels", "inside"),
        )


@dataclass
class ContentStyle:
    writing_tone: WritingTone = WritingTone.FORMAL
    headline_style: HeadlineStyle = HeadlineStyle.STATEMENT
    bullet_style: str = "fragments"    # "full-sentences", "fragments"
    bullet_punctuation: bool = False
    number_format_comma: bool = True
    number_format_decimals: int = 1
    currency_symbol: str = "$"
    large_number_abbrev: bool = True   # 1M instead of 1,000,000

    def to_dict(self) -> dict:
        return {
            "writing_tone": self.writing_tone.value,
            "headline_style": self.headline_style.value,
            "bullet_style": self.bullet_style,
            "bullet_punctuation": self.bullet_punctuation,
            "number_format_comma": self.number_format_comma,
            "number_format_decimals": self.number_format_decimals,
            "currency_symbol": self.currency_symbol,
            "large_number_abbrev": self.large_number_abbrev,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "ContentStyle":
        return cls(
            writing_tone=WritingTone(d.get("writing_tone", "formal")),
            headline_style=HeadlineStyle(d.get("headline_style", "statement")),
            bullet_style=d.get("bullet_style", "fragments"),
            bullet_punctuation=d.get("bullet_punctuation", False),
            number_format_comma=d.get("number_format_comma", True),
            number_format_decimals=d.get("number_format_decimals", 1),
            currency_symbol=d.get("currency_symbol", "$"),
            large_number_abbrev=d.get("large_number_abbrev", True),
        )


@dataclass
class BrandProfile:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "Untitled Brand"
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    source_materials: list[str] = field(default_factory=list)
    colors: ColorPalette = field(default_factory=ColorPalette)
    typography: Typography = field(default_factory=Typography)
    layout: LayoutSpacing = field(default_factory=LayoutSpacing)
    visuals: VisualElements = field(default_factory=VisualElements)
    content_style: ContentStyle = field(default_factory=ContentStyle)
    # Low-confidence fields flagged for review
    review_flags: list[str] = field(default_factory=list)
    archived: bool = False

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "source_materials": self.source_materials,
            "colors": self.colors.to_dict(),
            "typography": self.typography.to_dict(),
            "layout": self.layout.to_dict(),
            "visuals": self.visuals.to_dict(),
            "content_style": self.content_style.to_dict(),
            "review_flags": self.review_flags,
            "archived": self.archived,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_dict(cls, d: dict) -> "BrandProfile":
        return cls(
            id=d.get("id", str(uuid.uuid4())),
            name=d.get("name", "Untitled Brand"),
            created_at=d.get("created_at", datetime.utcnow().isoformat()),
            updated_at=d.get("updated_at", datetime.utcnow().isoformat()),
            source_materials=d.get("source_materials", []),
            colors=ColorPalette.from_dict(d.get("colors", {})),
            typography=Typography.from_dict(d.get("typography", {})),
            layout=LayoutSpacing.from_dict(d.get("layout", {})),
            visuals=VisualElements.from_dict(d.get("visuals", {})),
            content_style=ContentStyle.from_dict(d.get("content_style", {})),
            review_flags=d.get("review_flags", []),
            archived=d.get("archived", False),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "BrandProfile":
        return cls.from_dict(json.loads(json_str))

    def merge(self, other: "BrandProfile", priority: str = "other") -> "BrandProfile":
        """Merge another profile into this one. 'priority' controls which wins conflicts."""
        merged = BrandProfile.from_dict(self.to_dict())
        merged.updated_at = datetime.utcnow().isoformat()
        merged.source_materials = list(set(self.source_materials + other.source_materials))

        if priority == "other":
            source = other
        else:
            source = self

        # Merge colors — prefer source with higher confidence on primary
        if source.colors.primary:
            merged.colors.primary = source.colors.primary
        if source.colors.secondary:
            merged.colors.secondary = source.colors.secondary
        if source.colors.accent:
            merged.colors.accent = source.colors.accent

        # Merge typography
        if source.typography.heading_font:
            merged.typography.heading_font = source.typography.heading_font
        if source.typography.body_font:
            merged.typography.body_font = source.typography.body_font

        # Accumulate review flags
        merged.review_flags = list(set(self.review_flags + other.review_flags))
        return merged

    def duplicate(self, new_name: str) -> "BrandProfile":
        copy = BrandProfile.from_dict(self.to_dict())
        copy.id = str(uuid.uuid4())
        copy.name = new_name
        copy.created_at = datetime.utcnow().isoformat()
        copy.updated_at = datetime.utcnow().isoformat()
        return copy
