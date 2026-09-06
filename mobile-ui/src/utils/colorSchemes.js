/**
 * V-LKG Cockpit Color Schemes & Bi/Tri Pattern Generators
 * Provides curated mixed color schemes (bi-color and tri-color) and dynamic pattern styling.
 */

export const BI_COLOR_PRESETS = [
  {
    id: "cyber-cyan",
    name: "Cyber Cyan & Emerald",
    type: "bi",
    colors: ["#0EA5E9", "#10B981"],
    description: "High-contrast technical cockpit aesthetic"
  },
  {
    id: "neon-sunset",
    name: "Solar Amber & Rose",
    type: "bi",
    colors: ["#F59E0B", "#F43F5E"],
    description: "Dynamic warm energy and velocity"
  },
  {
    id: "ultraviolet",
    name: "Electric Indigo & Fuchsia",
    type: "bi",
    colors: ["#6366F1", "#D946EF"],
    description: "Deep-space neon pulse"
  },
  {
    id: "quantum-flux",
    name: "Glacial Blue & Tech Violet",
    type: "bi",
    colors: ["#38BDF8", "#8B5CF6"],
    description: "Futuristic algorithmic clarity"
  },
  {
    id: "emerald-gold",
    name: "Imperial Emerald & Cyber Gold",
    type: "bi",
    colors: ["#059669", "#EAB308"],
    description: "Prestigious intelligence and revenue"
  },
  {
    id: "hyper-plasma",
    name: "Neon Coral & Electric Cyan",
    type: "bi",
    colors: ["#FB7185", "#06B6D4"],
    description: "Vibrant high-frequency telemetry"
  }
];

export const TRI_COLOR_PRESETS = [
  {
    id: "aurora-tri",
    name: "Aurora Chromatic (Cyan / Violet / Emerald)",
    type: "tri",
    colors: ["#0EA5E9", "#8B5CF6", "#10B981"],
    description: "Signature triple spectrum flow"
  },
  {
    id: "solar-flare-tri",
    name: "Solar Flare (Amber / Rose / Violet)",
    type: "tri",
    colors: ["#F59E0B", "#F43F5E", "#8B5CF6"],
    description: "High-temperature cognitive energy"
  },
  {
    id: "deep-matrix-tri",
    name: "Matrix Core (Emerald / Teal / Cobalt)",
    type: "tri",
    colors: ["#10B981", "#14B8A6", "#0284C7"],
    description: "Deep structured graph telemetry"
  },
  {
    id: "synthwave-tri",
    name: "Synthwave Pulse (Pink / Blue / Mint)",
    type: "tri",
    colors: ["#EC4899", "#3B82F6", "#34D399"],
    description: "Retro-futuristic precision pulse"
  },
  {
    id: "titanium-tri",
    name: "Titanium Cockpit (Slate / Sky / Amber)",
    type: "tri",
    colors: ["#94A3B8", "#38BDF8", "#FBBF24"],
    description: "Industrial aerospace instrumentation"
  }
];

export const SOLID_PRESETS = [
  { id: "cyan", name: "Electric Cyan", type: "solid", colors: ["#0EA5E9"] },
  { id: "emerald", name: "Emerald Matrix", type: "solid", colors: ["#10B981"] },
  { id: "amber", name: "Solar Amber", type: "solid", colors: ["#F59E0B"] },
  { id: "rose", name: "Crimson Rose", type: "solid", colors: ["#F43F5E"] },
  { id: "indigo", name: "Tech Indigo", type: "solid", colors: ["#6366F1"] },
  { id: "teal", name: "Deep Teal", type: "solid", colors: ["#14B8A6"] }
];

export const PATTERN_MODES = [
  {
    id: "gradient-bi",
    name: "Dual Gradient",
    description: "45° angled dual linear chromatic blend",
    supports: ["bi", "tri"]
  },
  {
    id: "gradient-tri",
    name: "Tri Gradient",
    description: "3-stop rich linear flow (0% - 50% - 100%)",
    supports: ["tri"]
  },
  {
    id: "split-bi",
    name: "Split Duotone",
    description: "Geometric half-and-half dual tone contrast",
    supports: ["bi"]
  },
  {
    id: "stripe-tri",
    name: "Tri-Stripe Telemetry",
    description: "Segmented precision accent tracks",
    supports: ["tri", "bi"]
  },
  {
    id: "radial-mesh",
    name: "Ambient Radial Mesh",
    description: "Multi-origin atmospheric glowing mesh",
    supports: ["bi", "tri"]
  },
  {
    id: "solid",
    name: "Solid Monotone",
    description: "Single primary technical accent",
    supports: ["solid", "bi", "tri"]
  }
];

/**
 * Returns CSS background string or style object for a given pattern and colors array
 */
export function getPatternBackground(pattern = "gradient-bi", colors = ["#0EA5E9", "#10B981"]) {
  if (!colors || colors.length === 0) colors = ["#0EA5E9", "#10B981"];
  const c1 = colors[0] || "#0EA5E9";
  const c2 = colors[1] || c1;
  const c3 = colors[2] || c2;

  switch (pattern) {
    case "gradient-tri":
      return `linear-gradient(135deg, ${c1} 0%, ${c2} 50%, ${c3} 100%)`;
    case "split-bi":
      return `linear-gradient(135deg, ${c1} 0%, ${c1} 50%, ${c2} 50%, ${c2} 100%)`;
    case "stripe-tri":
      return `linear-gradient(90deg, ${c1} 0%, ${c1} 33.3%, ${c2} 33.3%, ${c2} 66.6%, ${c3} 66.6%, ${c3} 100%)`;
    case "radial-mesh":
      return `radial-gradient(circle at 10% 20%, ${c1} 0%, transparent 60%), radial-gradient(circle at 90% 80%, ${c2} 0%, transparent 60%), ${c3}`;
    case "solid":
      return c1;
    case "gradient-bi":
    default:
      return `linear-gradient(135deg, ${c1} 0%, ${c2} 100%)`;
  }
}

/**
 * Returns a subtle dark card accent background with the pattern faded
 */
export function getCardAtmosphere(pattern = "gradient-bi", colors = ["#0EA5E9", "#10B981"]) {
  if (!colors || colors.length === 0) colors = ["#0EA5E9", "#10B981"];
  const c1 = colors[0] || "#0EA5E9";
  const c2 = colors[1] || c1;

  return `radial-gradient(ellipse at top left, ${c1}18, transparent 50%), radial-gradient(ellipse at bottom right, ${c2}15, transparent 50%)`;
}

/**
 * Resolves child app's pattern and colors with fallbacks
 */
export function resolveAppTheme(app) {
  if (!app) {
    return {
      pattern: "gradient-bi",
      colors: ["#0EA5E9", "#10B981"],
      primaryColor: "#0EA5E9",
      background: getPatternBackground("gradient-bi", ["#0EA5E9", "#10B981"])
    };
  }

  let pattern = app.pattern || "gradient-bi";
  let colors = app.pattern_colors;

  if (!colors || !Array.isArray(colors) || colors.length === 0) {
    const primary = app.theme_color || "#0EA5E9";
    colors = [primary, "#10B981"];
  }

  return {
    pattern,
    colors,
    primaryColor: colors[0] || app.theme_color || "#0EA5E9",
    background: getPatternBackground(pattern, colors),
    cardAtmosphere: getCardAtmosphere(pattern, colors)
  };
}
