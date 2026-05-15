---
version: alpha
name: AI Learning Cockpit Minimal Tech
description: A clean, OpenAI-developer-inspired Chinese AI learning workspace with subtle motion and restrained technical atmosphere.
colors:
  canvas: "#06070A"
  surface: "#FFFFFF"
  panel: "#111318"
  primary: "#10A37F"
  secondary: "#6AA8FF"
  warning: "#F59E0B"
  danger: "#EF4444"
  text: "#F4F7FB"
  text-muted: "#8F9AAA"
  border: "#2A2F38"
typography:
  display:
    fontFamily: Inter
    fontSize: 48px
    fontWeight: 650
    lineHeight: 1.08
    letterSpacing: -0.03em
  headline:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: 650
    lineHeight: 1.18
    letterSpacing: -0.02em
  title:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: 650
    lineHeight: 1.3
    letterSpacing: -0.02em
  body:
    fontFamily: Noto Sans SC
    fontSize: 14px
    fontWeight: 400
    lineHeight: 1.7
    letterSpacing: 0em
  label:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: 600
    lineHeight: 1.2
    letterSpacing: 0em
rounded:
  sm: 10px
  md: 16px
  full: 999px
spacing:
  xs: 6px
  sm: 10px
  md: 14px
  lg: 20px
  xl: 32px
components:
  button-primary:
    backgroundColor: "{colors.text}"
    textColor: "{colors.canvas}"
    rounded: "{rounded.full}"
    padding: 10px
  card:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.text}"
    rounded: "{rounded.md}"
    padding: 18px
---

# AI Learning Cockpit Design System

## Overview

The interface should feel like a clean developer product, closer to OpenAI Developers than a cyberpunk dashboard. It should be quiet, precise, and modern: dark canvas, subtle animated grid, thin borders, small typography, and restrained green highlights.

The background may move, but only softly. Motion should create atmosphere, not spectacle.

## Colors

Use near-black canvas, translucent dark panels, white text, muted gray metadata, and one primary green accent. Blue is allowed for secondary highlights. Avoid large purple/orange gradients and heavy glass effects.

## Typography

Use Inter for headings, labels, and numeric UI. Use Noto Sans SC for Chinese body text. Keep body text around 14px and line height around 1.7.

## Layout

Information density should be moderate and calm. Use thin panels and compact rows. The dashboard and route pages should scan like documentation/product tools rather than landing pages.

## Elevation & Depth

Use thin borders and very soft shadows. Avoid thick neon glow, heavy blur, and oversized radii.

## Shapes

Use 10px radius for rows and controls, 16px for panels, and full radius for chips.

## Components

Resources can be checked off and should visibly show completion. Status chips should be compact. Buttons should be small, clear, and predictable.

## Do's and Don'ts

Do keep background motion subtle. Do keep text readable. Do make progress and check-ins obvious.

Don't overuse gradients, oversized type, thick glass cards, or decorative HUD elements.
