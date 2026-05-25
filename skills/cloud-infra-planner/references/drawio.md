# draw.io Diagram Generation Reference

Generate architecture diagrams as `.drawio` files (native mxGraphModel XML) that open directly in draw.io desktop or app.diagrams.net.

---

## File Structure

Every `.drawio` file must follow this wrapper:

```xml
<mxfile>
  <diagram name="Architecture">
    <mxGraphModel adaptiveColors="auto">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        <!-- all diagram cells here, parent="1" -->
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

**Critical rules:**
- NEVER include XML comments (`<!-- -->`) — they cause parse errors
- Every edge `mxCell` must contain `<mxGeometry relative="1" as="geometry"/>` as a child — never self-close edge cells
- Escape special characters in attributes: `&amp;` `&lt;` `&gt;` `&quot;`
- All `id` values must be unique across the file
- Use `adaptiveColors="auto"` on `mxGraphModel` for dark mode support

---

## Standard Shapes for Infra Diagrams

```xml
<!-- Rounded box (server, service, app) -->
<mxCell id="n1" value="Laravel App" style="rounded=1;whiteSpace=wrap;fillColor=#dae8fc;strokeColor=#6c8ebf;" vertex="1" parent="1">
  <mxGeometry x="200" y="100" width="140" height="60" as="geometry"/>
</mxCell>

<!-- Cylinder (database) -->
<mxCell id="n2" value="MySQL DB" style="shape=cylinder3;whiteSpace=wrap;fillColor=#f8cecc;strokeColor=#b85450;" vertex="1" parent="1">
  <mxGeometry x="200" y="240" width="140" height="70" as="geometry"/>
</mxCell>

<!-- Hexagon (Redis / cache) -->
<mxCell id="n3" value="Redis" style="shape=hexagon;whiteSpace=wrap;fillColor=#fff2cc;strokeColor=#d6b656;" vertex="1" parent="1">
  <mxGeometry x="400" y="240" width="120" height="70" as="geometry"/>
</mxCell>

<!-- Internet / cloud -->
<mxCell id="n4" value="Internet" style="shape=cloud;whiteSpace=wrap;fillColor=#f5f5f5;strokeColor=#666666;" vertex="1" parent="1">
  <mxGeometry x="200" y="20" width="140" height="60" as="geometry"/>
</mxCell>

<!-- Load balancer (rhombus) -->
<mxCell id="n5" value="Load Balancer" style="rhombus;whiteSpace=wrap;fillColor=#d5e8d4;strokeColor=#82b366;" vertex="1" parent="1">
  <mxGeometry x="200" y="100" width="140" height="70" as="geometry"/>
</mxCell>

<!-- Storage bucket -->
<mxCell id="n6" value="Spaces / CDN" style="shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.s3;fillColor=#7AA116;strokeColor=none;fontColor=#ffffff;" vertex="1" parent="1">
  <mxGeometry x="400" y="100" width="60" height="60" as="geometry"/>
</mxCell>

<!-- Swimlane container (zone / environment) -->
<mxCell id="zone1" value="Production" style="swimlane;startSize=30;fillColor=#f0f7ff;strokeColor=#6c8ebf;fontStyle=1;" vertex="1" parent="1">
  <mxGeometry x="40" y="40" width="600" height="400" as="geometry"/>
</mxCell>
```

---

## Edges (Connectors)

```xml
<!-- Standard arrow -->
<mxCell id="e1" value="" style="edgeStyle=orthogonalEdgeStyle;rounded=1;" edge="1" source="n1" target="n2" parent="1">
  <mxGeometry relative="1" as="geometry"/>
</mxCell>

<!-- Labeled arrow -->
<mxCell id="e2" value="HTTPS" style="edgeStyle=orthogonalEdgeStyle;rounded=1;" edge="1" source="n4" target="n5" parent="1">
  <mxGeometry relative="1" as="geometry"/>
</mxCell>

<!-- Dashed arrow (optional/async) -->
<mxCell id="e3" value="queue" style="edgeStyle=orthogonalEdgeStyle;dashed=1;" edge="1" source="n1" target="n3" parent="1">
  <mxGeometry relative="1" as="geometry"/>
</mxCell>
```

---

## Colour Palette for Infra Diagrams

| Component type | fillColor | strokeColor |
|---|---|---|
| App server / Laravel | `#dae8fc` | `#6c8ebf` |
| Database | `#f8cecc` | `#b85450` |
| Redis / cache | `#fff2cc` | `#d6b656` |
| Storage / CDN | `#d5e8d4` | `#82b366` |
| Load balancer | `#e1d5e7` | `#9673a6` |
| Docker container | `#f0f0f0` | `#555555` |
| Internet / external | `#f5f5f5` | `#666666` |
| Zone / environment swimlane | `#f0f7ff` | `#6c8ebf` |

---

## Layout Guidelines

- Minimum 60px between nodes; prefer 160–200px horizontal, 100–120px vertical gaps
- Top-to-bottom flow: Internet → Load Balancer → App → DB / Redis / Storage
- Use swimlane containers for environment zones (Production, Dev/QA, UAT)
- Align all nodes to a 10px grid
- Space nodes generously — edges need at least 20px of straight segment before arrowhead
- Use `exitX/exitY/entryX/entryY` (0–1) to control which side edges connect to

---

## Standard Infra Diagram Template

For a typical Laravel + Next.js + Docker + Managed services setup on DigitalOcean, produce three pages (one per environment) or three swimlanes (if a single-page overview is requested):

**Page / swimlane structure:**
1. **Internet** (cloud shape at top)
2. **Load Balancer** (only in Production)
3. **App Droplet** (swimlane container holding: Nginx, PHP-FPM/Laravel, PM2/Next.js, Docker containers, Horizon)
4. **Managed Services** row: MySQL DB, Redis, Spaces CDN
5. Arrows labelled: HTTPS, SQL, Redis protocol, S3 API

---

## Generating the File

1. Write the XML to `/mnt/user-data/outputs/<project>-architecture.drawio`
2. Validate: ensure all edge cells have `<mxGeometry>` children, no self-closing edges, no XML comments, unique IDs
3. Present the file to the user via `present_files`
4. Optionally embed in the docx report as a screenshot (render via draw.io viewer if available)

---

## Opening the Diagram

Tell the user:
- Open at **app.diagrams.net** (drag and drop the `.drawio` file)
- Or install **draw.io desktop** app from [get.diagrams.net](https://get.diagrams.net)
- The file is fully editable after opening — layers, shapes, and labels can all be adjusted