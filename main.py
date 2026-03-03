#!/usr/bin/env python3
"""
AI Presentation Generator — CLI

Usage:
  python main.py extract  --input brand_guide.pdf --name "Acme Corp"
  python main.py generate --profile <id> --content outline.md --output deck.pptx
  python main.py profiles list
  python main.py profiles show <id>
  python main.py profiles export <id> --output profile.json
  python main.py profiles import profile.json
  python main.py profiles merge <id1> <id2> --types brand_guide_pdf website --name "Merged"
  python main.py profiles duplicate <id> --name "Sub-brand"
  python main.py profiles archive <id>
  python main.py slide regenerate <pptx> <index> --content slide.json --output new.pptx
"""

import os
import sys
import json
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

from src.brand_extractor import BrandExtractor
from src.brand_profile import BrandProfile
from src.profile_manager import ProfileManager
from src.content_input import ContentInputProcessor, DeckSpec
from src.slide_generator import SlideGenerator

console = Console()


def _get_extractor() -> BrandExtractor:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        console.print("[red]Error:[/red] ANTHROPIC_API_KEY environment variable not set.")
        sys.exit(1)
    return BrandExtractor(api_key=api_key)


def _get_processor() -> ContentInputProcessor:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        console.print("[red]Error:[/red] ANTHROPIC_API_KEY environment variable not set.")
        sys.exit(1)
    return ContentInputProcessor(api_key=api_key)


def _print_profile_summary(profile: BrandProfile) -> None:
    table = Table(title=f"Brand Profile: {profile.name}", show_header=True)
    table.add_column("Field", style="bold cyan")
    table.add_column("Value")

    table.add_row("ID", profile.id)
    table.add_row("Name", profile.name)
    table.add_row("Sources", ", ".join(profile.source_materials) or "—")
    table.add_row("Created", profile.created_at[:10])
    table.add_row("Updated", profile.updated_at[:10])
    table.add_row("Archived", str(profile.archived))

    if profile.colors.primary:
        table.add_row("Primary Color", profile.colors.primary.hex)
    if profile.colors.secondary:
        table.add_row("Secondary Colors", ", ".join(c.hex for c in profile.colors.secondary))
    if profile.typography.heading_font:
        table.add_row("Heading Font", profile.typography.heading_font.name)
    if profile.typography.body_font:
        table.add_row("Body Font", profile.typography.body_font.name)
    table.add_row("Aspect Ratio", profile.layout.aspect_ratio.value)
    table.add_row("Writing Tone", profile.content_style.writing_tone.value)

    if profile.review_flags:
        table.add_row("[yellow]Review Flags[/yellow]",
                      "[yellow]" + ", ".join(profile.review_flags) + "[/yellow]")

    console.print(table)


# ------------------------------------------------------------------
# CLI groups
# ------------------------------------------------------------------

@click.group()
def cli():
    """AI Presentation Generator — create branded decks from content."""
    pass


# ------------------------------------------------------------------
# extract command
# ------------------------------------------------------------------

@cli.command()
@click.option("--input", "-i", "input_path", required=True,
              help="Path to brand reference file or URL")
@click.option("--name", "-n", default="Brand", help="Brand name")
@click.option("--type", "-t", "source_type",
              type=click.Choice(["pdf", "pptx", "image", "logo", "website", "manual"]),
              help="Input type (auto-detected from extension if omitted)")
@click.option("--save/--no-save", default=True, help="Save profile to disk")
def extract(input_path, name, source_type, save):
    """Extract a brand profile from reference materials."""
    extractor = _get_extractor()
    manager = ProfileManager()

    # Auto-detect type
    if not source_type:
        ext = Path(input_path).suffix.lower()
        if input_path.startswith("http"):
            source_type = "website"
        elif ext == ".pdf":
            source_type = "pdf"
        elif ext == ".pptx":
            source_type = "pptx"
        elif ext in (".png", ".jpg", ".jpeg", ".webp"):
            source_type = "image"
        elif ext == ".svg":
            source_type = "logo"
        else:
            source_type = "pdf"

    with console.status(f"[bold green]Extracting brand profile from {source_type}..."):
        try:
            if source_type == "pdf":
                profile = extractor.from_pdf(input_path, brand_name=name)
            elif source_type == "pptx":
                profile = extractor.from_presentation(input_path, brand_name=name)
            elif source_type == "image":
                profile = extractor.from_image(input_path, brand_name=name, source_type="screenshot")
            elif source_type == "logo":
                profile = extractor.from_logo(input_path, brand_name=name)
            elif source_type == "website":
                profile = extractor.from_website(input_path, brand_name=name)
            else:
                console.print("[red]Unknown source type[/red]")
                sys.exit(1)
        except Exception as e:
            console.print(f"[red]Extraction failed:[/red] {e}")
            sys.exit(1)

    _print_profile_summary(profile)

    if save:
        manager.save(profile)
        console.print(f"\n[green]✓[/green] Profile saved with ID: [bold]{profile.id}[/bold]")

    if profile.review_flags:
        console.print("\n[yellow]⚠ Some fields have low confidence and need review:[/yellow]")
        for flag in profile.review_flags:
            console.print(f"  • {flag}")


# ------------------------------------------------------------------
# generate command
# ------------------------------------------------------------------

@cli.command()
@click.option("--profile", "-p", "profile_id", required=True,
              help="Brand profile ID to use")
@click.option("--content", "-c", "content_path",
              help="Path to content file (.md, .txt, .docx, .pdf, .csv) or URL")
@click.option("--text", help="Inline content text (alternative to --content)")
@click.option("--output", "-o", default="output.pptx", help="Output .pptx path")
@click.option("--purpose", default="General",
              type=click.Choice(["General", "Pitch", "Report", "Training",
                                 "Proposal", "Strategy", "Board", "Sales",
                                 "Event", "Investor"]),
              help="Presentation purpose")
@click.option("--audience", default="General", help="Target audience description")
@click.option("--slides", "target_slides", type=int, default=None,
              help="Target number of slides (auto if omitted)")
@click.option("--density",
              type=click.Choice(["Low", "Medium", "High"]), default="Medium",
              help="Content density per slide")
@click.option("--no-notes", is_flag=True, default=False,
              help="Omit speaker notes")
@click.option("--language", default="English", help="Output language")
def generate(profile_id, content_path, text, output, purpose, audience,
             target_slides, density, no_notes, language):
    """Generate a branded .pptx presentation."""
    manager = ProfileManager()

    try:
        profile = manager.get(profile_id)
    except FileNotFoundError:
        console.print(f"[red]Profile not found:[/red] {profile_id}")
        sys.exit(1)

    processor = _get_processor()
    params = {
        "purpose": purpose,
        "audience": audience,
        "target_slide_count": target_slides or "Auto",
        "content_density": density,
        "include_speaker_notes": not no_notes,
        "language": language,
    }

    with console.status("[bold green]Processing content..."):
        try:
            if text:
                deck = processor.from_freeform(text, params)
            elif content_path:
                if content_path.startswith("http"):
                    deck = processor.from_url(content_path, params)
                else:
                    ext = Path(content_path).suffix.lower()
                    if ext == ".csv" or ext == ".xlsx":
                        deck = processor.from_csv(content_path, params)
                    elif ext in (".md", ".txt") and _looks_like_outline(content_path):
                        outline_text = Path(content_path).read_text(encoding="utf-8")
                        deck = processor.from_outline(outline_text, params)
                    else:
                        deck = processor.from_document(content_path, params)
            else:
                console.print("[red]Provide --content or --text[/red]")
                sys.exit(1)
        except Exception as e:
            console.print(f"[red]Content processing failed:[/red] {e}")
            sys.exit(1)

    console.print(f"[green]✓[/green] Structured {len(deck.slides)} slides")

    with console.status(f"[bold green]Generating {output}..."):
        try:
            gen = SlideGenerator(profile)
            gen.generate(deck, output)
        except Exception as e:
            console.print(f"[red]Generation failed:[/red] {e}")
            sys.exit(1)

    console.print(f"\n[green]✓[/green] Presentation saved: [bold]{output}[/bold]")
    console.print(f"  Slides: {len(deck.slides)}")
    console.print(f"  Brand: {profile.name}")
    console.print(f"  Purpose: {purpose}")


def _looks_like_outline(path: str) -> bool:
    """Heuristic: if file starts with # headings, treat as outline."""
    try:
        first_lines = Path(path).read_text(encoding="utf-8")[:500]
        return first_lines.strip().startswith("#")
    except Exception:
        return False


# ------------------------------------------------------------------
# profiles group
# ------------------------------------------------------------------

@cli.group()
def profiles():
    """Manage brand profiles."""
    pass


@profiles.command("list")
@click.option("--all", "show_all", is_flag=True, default=False,
              help="Include archived profiles")
def profiles_list(show_all):
    """List all saved brand profiles."""
    manager = ProfileManager()
    all_profiles = manager.list_profiles(include_archived=show_all)

    if not all_profiles:
        console.print("No profiles found.")
        return

    table = Table(title="Brand Profiles", show_header=True)
    table.add_column("ID", style="dim", width=36)
    table.add_column("Name", style="bold")
    table.add_column("Primary Color")
    table.add_column("Sources")
    table.add_column("Updated")
    table.add_column("Status")

    for p in all_profiles:
        status = "[dim]archived[/dim]" if p.archived else "[green]active[/green]"
        primary = p.colors.primary.hex if p.colors.primary else "—"
        sources = ", ".join(p.source_materials[:2]) or "—"
        table.add_row(p.id, p.name, primary, sources, p.updated_at[:10], status)

    console.print(table)


@profiles.command("show")
@click.argument("profile_id")
def profiles_show(profile_id):
    """Show details for a brand profile."""
    manager = ProfileManager()
    try:
        profile = manager.get(profile_id)
    except FileNotFoundError:
        console.print(f"[red]Profile not found:[/red] {profile_id}")
        sys.exit(1)
    _print_profile_summary(profile)


@profiles.command("edit")
@click.argument("profile_id")
@click.argument("field")
@click.argument("value")
def profiles_edit(profile_id, field, value):
    """
    Edit a field in a brand profile.

    Example: profiles edit <id> colors.primary "#FF5500"
    """
    manager = ProfileManager()
    try:
        profile = manager.update_field(profile_id, field, value)
        console.print(f"[green]✓[/green] Updated {field} for profile {profile.name}")
    except FileNotFoundError:
        console.print(f"[red]Profile not found:[/red] {profile_id}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@profiles.command("export")
@click.argument("profile_id")
@click.option("--output", "-o", default=None, help="Output file path")
@click.option("--format", "fmt", type=click.Choice(["json", "summary"]),
              default="json")
def profiles_export(profile_id, output, fmt):
    """Export a brand profile to JSON or text summary."""
    manager = ProfileManager()
    try:
        profile = manager.get(profile_id)
    except FileNotFoundError:
        console.print(f"[red]Profile not found:[/red] {profile_id}")
        sys.exit(1)

    default_ext = ".json" if fmt == "json" else ".txt"
    out = output or f"{profile.name.replace(' ', '_')}_profile{default_ext}"

    if fmt == "json":
        manager.export_json(profile_id, out)
    else:
        manager.export_summary(profile_id, out)

    console.print(f"[green]✓[/green] Exported to {out}")


@profiles.command("import")
@click.argument("json_path")
def profiles_import(json_path):
    """Import a brand profile from a JSON file."""
    manager = ProfileManager()
    try:
        profile = manager.import_json(json_path)
        console.print(f"[green]✓[/green] Imported profile: {profile.name} (ID: {profile.id})")
    except Exception as e:
        console.print(f"[red]Import failed:[/red] {e}")
        sys.exit(1)


@profiles.command("merge")
@click.argument("profile_ids", nargs=-1, required=True)
@click.option("--types", required=True, multiple=True,
              help="Source types for each profile (in order), e.g. --types brand_guide_pdf --types website")
@click.option("--name", required=True, help="Name for the merged profile")
def profiles_merge(profile_ids, types, name):
    """Merge multiple profiles into one, following priority rules."""
    if len(profile_ids) != len(types):
        console.print("[red]Error:[/red] Number of profile IDs must match number of --types")
        sys.exit(1)

    manager = ProfileManager()
    try:
        merged, conflicts = manager.merge_profiles(list(profile_ids), list(types), name)
    except Exception as e:
        console.print(f"[red]Merge failed:[/red] {e}")
        sys.exit(1)

    console.print(f"[green]✓[/green] Merged profile saved: {merged.name} (ID: {merged.id})")

    if conflicts:
        console.print(f"\n[yellow]⚠ {len(conflicts)} conflict(s) detected:[/yellow]")
        for c in conflicts:
            console.print(f"\n  Field: [bold]{c.field}[/bold]")
            console.print(f"    {c.source_a}: {c.value_a}")
            console.print(f"    {c.source_b}: {c.value_b}")
            console.print(f"    [green]Recommended ({c.recommended}):[/green] {c.recommended_value}")


@profiles.command("duplicate")
@click.argument("profile_id")
@click.option("--name", required=True, help="Name for the duplicate")
def profiles_duplicate(profile_id, name):
    """Duplicate a profile as a starting point for a variant."""
    manager = ProfileManager()
    try:
        copy = manager.duplicate(profile_id, name)
        console.print(f"[green]✓[/green] Duplicated as: {copy.name} (ID: {copy.id})")
    except FileNotFoundError:
        console.print(f"[red]Profile not found:[/red] {profile_id}")
        sys.exit(1)


@profiles.command("archive")
@click.argument("profile_id")
def profiles_archive(profile_id):
    """Archive (soft-delete) a brand profile."""
    manager = ProfileManager()
    try:
        profile = manager.archive(profile_id)
        console.print(f"[green]✓[/green] Archived: {profile.name}")
    except FileNotFoundError:
        console.print(f"[red]Profile not found:[/red] {profile_id}")
        sys.exit(1)


# ------------------------------------------------------------------
# slide group
# ------------------------------------------------------------------

@cli.group()
def slide():
    """Individual slide operations."""
    pass


@slide.command("regenerate")
@click.argument("pptx_path")
@click.argument("slide_index", type=int)
@click.option("--profile", "-p", "profile_id", required=True, help="Brand profile ID")
@click.option("--content", "-c", "content_json",
              help="JSON file with new slide content")
@click.option("--output", "-o", default=None, help="Output path (overwrites input if omitted)")
@click.option("--layout", default="default", help="Layout variant override")
def slide_regenerate(pptx_path, slide_index, profile_id, content_json, output, layout):
    """Regenerate a single slide in an existing presentation."""
    from src.content_input import SlideContent, SlideType

    manager = ProfileManager()
    try:
        profile = manager.get(profile_id)
    except FileNotFoundError:
        console.print(f"[red]Profile not found:[/red] {profile_id}")
        sys.exit(1)

    if content_json:
        data = json.loads(Path(content_json).read_text(encoding="utf-8"))
        try:
            slide_type = SlideType(data.get("slide_type", "content_text"))
        except ValueError:
            slide_type = SlideType.CONTENT_TEXT
        new_content = SlideContent(
            slide_type=slide_type,
            title=data.get("title", ""),
            subtitle=data.get("subtitle", ""),
            body_bullets=data.get("body_bullets", []),
            body_text=data.get("body_text", ""),
            speaker_notes=data.get("speaker_notes", ""),
            layout_variant=layout,
        )
    else:
        console.print("[red]Provide --content with a JSON file[/red]")
        sys.exit(1)

    out = output or pptx_path
    gen = SlideGenerator(profile)

    # Create a minimal DeckSpec for context
    from src.content_input import DeckSpec
    deck = DeckSpec(slides=[new_content])

    try:
        gen.regenerate_slide(pptx_path, slide_index, new_content, deck, out)
        console.print(f"[green]✓[/green] Slide {slide_index} regenerated in {out}")
    except Exception as e:
        console.print(f"[red]Regeneration failed:[/red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    cli()
