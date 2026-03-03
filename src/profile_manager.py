"""
Brand Profile Manager

Handles persistence and management of brand profiles:
- Create, edit, merge, duplicate, archive, export, import
- File-based storage (JSON files in a configurable directory)
- Multi-source reconciliation with conflict surfacing
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from .brand_profile import BrandProfile, ColorEntry, Confidence


DEFAULT_PROFILES_DIR = os.path.join(os.path.expanduser("~"), ".ppt_generator", "profiles")


class ConflictReport:
    """Represents a conflict between two brand profile extractions for one field."""

    def __init__(self, field: str, source_a: str, value_a, source_b: str, value_b,
                 recommended: str, recommended_value):
        self.field = field
        self.source_a = source_a
        self.value_a = value_a
        self.source_b = source_b
        self.value_b = value_b
        self.recommended = recommended
        self.recommended_value = recommended_value

    def __str__(self) -> str:
        return (
            f"CONFLICT: {self.field}\n"
            f"  {self.source_a}: {self.value_a}\n"
            f"  {self.source_b}: {self.value_b}\n"
            f"  Recommended ({self.recommended}): {self.recommended_value}"
        )


class ProfileManager:
    """
    Manages brand profiles stored as JSON files on disk.

    Profiles are stored in <profiles_dir>/<profile_id>.json
    """

    def __init__(self, profiles_dir: Optional[str] = None):
        self.profiles_dir = Path(profiles_dir or DEFAULT_PROFILES_DIR)
        self.profiles_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Core CRUD operations
    # ------------------------------------------------------------------

    def save(self, profile: BrandProfile) -> BrandProfile:
        """Save (create or update) a brand profile."""
        profile.updated_at = datetime.utcnow().isoformat()
        path = self._profile_path(profile.id)
        path.write_text(profile.to_json(), encoding="utf-8")
        return profile

    def get(self, profile_id: str) -> BrandProfile:
        """Load a brand profile by ID. Raises FileNotFoundError if not found."""
        path = self._profile_path(profile_id)
        if not path.exists():
            raise FileNotFoundError(f"Profile not found: {profile_id}")
        return BrandProfile.from_json(path.read_text(encoding="utf-8"))

    def list_profiles(self, include_archived: bool = False) -> list[BrandProfile]:
        """List all saved profiles, optionally including archived ones."""
        profiles = []
        for path in self.profiles_dir.glob("*.json"):
            try:
                p = BrandProfile.from_json(path.read_text(encoding="utf-8"))
                if not p.archived or include_archived:
                    profiles.append(p)
            except Exception:
                continue
        return sorted(profiles, key=lambda p: p.updated_at, reverse=True)

    def delete(self, profile_id: str) -> None:
        """Permanently delete a profile (use archive() for soft-delete)."""
        path = self._profile_path(profile_id)
        if path.exists():
            path.unlink()

    def archive(self, profile_id: str) -> BrandProfile:
        """Soft-delete: mark profile as archived without removing the file."""
        profile = self.get(profile_id)
        profile.archived = True
        return self.save(profile)

    def unarchive(self, profile_id: str) -> BrandProfile:
        """Restore an archived profile."""
        profile = self.get(profile_id)
        profile.archived = False
        return self.save(profile)

    def duplicate(self, profile_id: str, new_name: str) -> BrandProfile:
        """Clone a profile as a starting point for a variant."""
        original = self.get(profile_id)
        copy = original.duplicate(new_name)
        return self.save(copy)

    def update_field(self, profile_id: str, field_path: str, value) -> BrandProfile:
        """
        Update a specific field in a profile using dot notation.
        e.g. field_path="colors.primary.hex", value="#FF0000"

        Supported top-level sections: colors, typography, layout, visuals, content_style, name
        """
        profile = self.get(profile_id)
        parts = field_path.split(".")

        if parts[0] == "name":
            profile.name = str(value)
        elif parts[0] == "colors" and len(parts) >= 2:
            self._update_colors(profile, parts[1:], value)
        elif parts[0] == "typography" and len(parts) >= 2:
            self._update_typography(profile, parts[1:], value)
        elif parts[0] == "layout" and len(parts) >= 2:
            self._update_layout(profile, parts[1:], value)
        elif parts[0] == "visuals" and len(parts) >= 2:
            self._update_visuals(profile, parts[1:], value)
        elif parts[0] == "content_style" and len(parts) >= 2:
            self._update_content_style(profile, parts[1:], value)
        else:
            raise ValueError(f"Unknown field path: {field_path}")

        # Remove from review flags if manually corrected
        if field_path in profile.review_flags:
            profile.review_flags.remove(field_path)

        return self.save(profile)

    # ------------------------------------------------------------------
    # Multi-source merge with conflict detection
    # ------------------------------------------------------------------

    def merge_profiles(self, profile_ids: list[str],
                       source_types: list[str],
                       target_name: str) -> tuple[BrandProfile, list[ConflictReport]]:
        """
        Merge multiple profiles following the priority hierarchy.
        Returns the merged profile and a list of detected conflicts.

        Priority (lower index = higher priority):
          1. manual
          2. brand_guide_pdf
          3. existing_presentation
          4. website
          5. logo / screenshot
        """
        SOURCE_PRIORITY = {
            "manual": 1,
            "brand_guide_pdf": 2,
            "existing_presentation": 3,
            "website": 4,
            "logo": 5,
            "screenshot": 5,
        }

        profiles = [self.get(pid) for pid in profile_ids]
        paired = list(zip(profiles, source_types))
        paired.sort(key=lambda x: SOURCE_PRIORITY.get(x[1], 99))

        merged = BrandProfile()
        merged.name = target_name
        conflicts: list[ConflictReport] = []

        for profile, source_type in paired:
            # Colors
            if profile.colors.primary:
                if merged.colors.primary:
                    if merged.colors.primary.hex != profile.colors.primary.hex:
                        priority_src = paired[0][1]
                        conflicts.append(ConflictReport(
                            field="colors.primary",
                            source_a=priority_src,
                            value_a=merged.colors.primary.hex,
                            source_b=source_type,
                            value_b=profile.colors.primary.hex,
                            recommended=priority_src,
                            recommended_value=merged.colors.primary.hex,
                        ))
                else:
                    merged.colors.primary = profile.colors.primary

            if profile.colors.secondary and not merged.colors.secondary:
                merged.colors.secondary = profile.colors.secondary
            if profile.colors.accent and not merged.colors.accent:
                merged.colors.accent = profile.colors.accent

            # Typography
            if profile.typography.heading_font:
                if merged.typography.heading_font:
                    if merged.typography.heading_font.name != profile.typography.heading_font.name:
                        priority_src = paired[0][1]
                        conflicts.append(ConflictReport(
                            field="typography.heading_font",
                            source_a=priority_src,
                            value_a=merged.typography.heading_font.name,
                            source_b=source_type,
                            value_b=profile.typography.heading_font.name,
                            recommended=priority_src,
                            recommended_value=merged.typography.heading_font.name,
                        ))
                else:
                    merged.typography.heading_font = profile.typography.heading_font

            if profile.typography.body_font and not merged.typography.body_font:
                merged.typography.body_font = profile.typography.body_font

            merged.source_materials.extend(profile.source_materials)
            merged.review_flags.extend(profile.review_flags)

        merged.source_materials = list(set(merged.source_materials))
        merged.review_flags = list(set(merged.review_flags))

        return self.save(merged), conflicts

    # ------------------------------------------------------------------
    # Import / Export
    # ------------------------------------------------------------------

    def export_json(self, profile_id: str, output_path: str) -> str:
        """Export a profile as a JSON file."""
        profile = self.get(profile_id)
        output = Path(output_path)
        output.write_text(profile.to_json(), encoding="utf-8")
        return str(output)

    def export_summary(self, profile_id: str, output_path: str) -> str:
        """Export a human-readable text summary of the brand profile."""
        profile = self.get(profile_id)
        lines = [
            f"Brand Profile: {profile.name}",
            f"ID: {profile.id}",
            f"Created: {profile.created_at}",
            f"Sources: {', '.join(profile.source_materials)}",
            "",
            "=== COLOR PALETTE ===",
        ]
        if profile.colors.primary:
            lines.append(f"Primary: {profile.colors.primary.hex} {profile.colors.primary.rgb}")
        for i, c in enumerate(profile.colors.secondary, 1):
            lines.append(f"Secondary {i}: {c.hex}")
        for i, c in enumerate(profile.colors.accent, 1):
            lines.append(f"Accent {i}: {c.hex}")
        if profile.colors.background_light:
            lines.append(f"Background (light): {profile.colors.background_light.hex}")
        if profile.colors.background_dark:
            lines.append(f"Background (dark): {profile.colors.background_dark.hex}")

        lines.append("")
        lines.append("=== TYPOGRAPHY ===")
        if profile.typography.heading_font:
            lines.append(f"Heading font: {profile.typography.heading_font.name}")
        if profile.typography.body_font:
            lines.append(f"Body font: {profile.typography.body_font.name}")
        lines.append(f"Title size: {profile.typography.size_title}pt")
        lines.append(f"Body size: {profile.typography.size_body}pt")

        lines.append("")
        lines.append("=== LAYOUT ===")
        lines.append(f"Aspect ratio: {profile.layout.aspect_ratio.value}")
        lines.append(f"Alignment: {profile.layout.content_alignment}")
        lines.append(f"White space: {profile.layout.white_space.value}")
        lines.append(f"Max bullets/slide: {profile.layout.max_bullets_per_slide}")

        lines.append("")
        lines.append("=== CONTENT STYLE ===")
        lines.append(f"Writing tone: {profile.content_style.writing_tone.value}")
        lines.append(f"Headline style: {profile.content_style.headline_style.value}")
        lines.append(f"Bullet style: {profile.content_style.bullet_style}")

        if profile.review_flags:
            lines.append("")
            lines.append("=== REVIEW FLAGS (Low Confidence) ===")
            for flag in profile.review_flags:
                lines.append(f"  ! {flag}")

        text = "\n".join(lines)
        Path(output_path).write_text(text, encoding="utf-8")
        return output_path

    def import_json(self, json_path: str) -> BrandProfile:
        """Import a profile from a previously exported JSON file."""
        data = json.loads(Path(json_path).read_text(encoding="utf-8"))
        profile = BrandProfile.from_dict(data)
        # Assign new ID to avoid collision
        import uuid
        profile.id = str(uuid.uuid4())
        profile.updated_at = datetime.utcnow().isoformat()
        return self.save(profile)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _profile_path(self, profile_id: str) -> Path:
        return self.profiles_dir / f"{profile_id}.json"

    def _update_colors(self, profile: BrandProfile, parts: list[str], value) -> None:
        from .brand_profile import _make_color_entry  # local import to avoid circular
        field = parts[0]
        if field == "primary":
            profile.colors.primary = _make_color_entry(str(value), Confidence.HIGH, "manual override")
        elif field == "background_light":
            profile.colors.background_light = _make_color_entry(str(value), Confidence.HIGH)
        elif field == "background_dark":
            profile.colors.background_dark = _make_color_entry(str(value), Confidence.HIGH)
        elif field == "text_heading":
            profile.colors.text_heading = _make_color_entry(str(value), Confidence.HIGH)
        elif field == "text_body":
            profile.colors.text_body = _make_color_entry(str(value), Confidence.HIGH)
        elif field == "usage_rules":
            profile.colors.usage_rules = str(value)

    def _update_typography(self, profile: BrandProfile, parts: list[str], value) -> None:
        field = parts[0]
        if field == "heading_font":
            profile.typography.heading_font = FontSpec(name=str(value), confidence=Confidence.HIGH)
        elif field == "body_font":
            profile.typography.body_font = FontSpec(name=str(value), confidence=Confidence.HIGH)
        elif field in ("size_title", "size_h1", "size_h2", "size_h3",
                       "size_body", "size_caption", "size_footnote"):
            setattr(profile.typography, field, int(value))
        elif field in ("title_alignment", "body_alignment", "weight_bold_usage",
                       "weight_light_usage"):
            setattr(profile.typography, field, str(value))

    def _update_layout(self, profile: BrandProfile, parts: list[str], value) -> None:
        from .brand_profile import AspectRatio, WhiteSpacePhilosophy
        field = parts[0]
        if field == "aspect_ratio":
            profile.layout.aspect_ratio = AspectRatio(str(value))
        elif field == "white_space":
            profile.layout.white_space = WhiteSpacePhilosophy(str(value))
        elif field in ("margin_top", "margin_bottom", "margin_left", "margin_right",
                       "logo_clear_space"):
            setattr(profile.layout, field, float(value))
        elif field in ("max_bullets_per_slide", "max_words_per_bullet"):
            setattr(profile.layout, field, int(value))
        elif field in ("content_alignment", "image_placement"):
            setattr(profile.layout, field, str(value))

    def _update_visuals(self, profile: BrandProfile, parts: list[str], value) -> None:
        from .brand_profile import IconStyle, ShapeLanguage
        field = parts[0]
        if field == "icon_style":
            profile.visuals.icon_style = IconStyle(str(value))
        elif field == "shape_language":
            profile.visuals.shape_language = ShapeLanguage(str(value))
        elif field in ("logo_placement", "divider_style", "background_treatment",
                       "chart_style", "chart_labels"):
            setattr(profile.visuals, field, str(value))
        elif field in ("logo_min_size_px", "corner_radius"):
            setattr(profile.visuals, field, int(value))

    def _update_content_style(self, profile: BrandProfile, parts: list[str], value) -> None:
        from .brand_profile import WritingTone, HeadlineStyle
        field = parts[0]
        if field == "writing_tone":
            profile.content_style.writing_tone = WritingTone(str(value))
        elif field == "headline_style":
            profile.content_style.headline_style = HeadlineStyle(str(value))
        elif field in ("bullet_style", "currency_symbol"):
            setattr(profile.content_style, field, str(value))
        elif field in ("bullet_punctuation", "number_format_comma", "large_number_abbrev"):
            setattr(profile.content_style, field, bool(value))
        elif field == "number_format_decimals":
            profile.content_style.number_format_decimals = int(value)


# Fix missing import in _update_colors helper
from .brand_profile import FontSpec, _make_color_entry  # noqa: E402
