import xml.etree.ElementTree as ET
from xml.dom import minidom
from awesome_media.exporters.base import BaseExporter, console


class OpmlExporter(BaseExporter):
    def export(self, sources):
        path = self.output_dir / "feeds.opml"
        opml = ET.Element("opml", version="1.0")
        body = ET.SubElement(opml, "body")

        # Group by category
        categories = {}
        for s in sources:
            if not s.rss_feeds:
                continue
            categories.setdefault(s.category, []).append(s)

        for cat_name, cat_sources in categories.items():
            cat_outline = ET.SubElement(body, "outline", text=cat_name, title=cat_name)
            for s in cat_sources:
                for feed in s.rss_feeds:
                    label = feed.get("label")
                    text = f"{s.title} - {label}" if label else s.title
                    ET.SubElement(
                        cat_outline,
                        "outline",
                        text=text,
                        title=text,
                        type="rss",
                        htmlUrl=s.website_url,
                        xmlUrl=feed["url"],
                    )

        xml_str = minidom.parseString(ET.tostring(opml)).toprettyxml(indent="  ")
        with open(path, "w", encoding="utf-8") as f:
            f.write(xml_str)
        console.print("[green]✓[/green] Exported OPML file")
