import { defineConfig } from "astro/config";
import starlight from "@astrojs/starlight";
import starlightLinksValidator from "starlight-links-validator";

// The link validator fails the build on any broken internal link.
export default defineConfig({
  site: "https://telschow.github.io",
  base: "/mosaic-perception",
  integrations: [
    starlight({
      title: "Mosaic Perception",
      social: [
        { icon: "github", label: "GitHub", href: "https://github.com/Telschow/mosaic-perception" },
      ],
      plugins: [starlightLinksValidator({ errorOnRelativeLinks: true })],
      sidebar: [
        { label: "Home", link: "/" },
        { label: "Architecture", slug: "architecture" },
        { label: "Scenarios", slug: "scenarios" },
        { label: "Metrics", slug: "metrics" },
        { label: "Evaluation protocol", slug: "evaluation-protocol" },
        { label: "Limitations", slug: "limitations" },
        { label: "Roadmap", slug: "roadmap" },
        { label: "Implementation status", slug: "implementation-status" },
        { label: "Demos", slug: "demos" },
        { label: "Audit", slug: "audit" },
        { label: "Citation", slug: "citation" },
      ],
    }),
  ],
});
