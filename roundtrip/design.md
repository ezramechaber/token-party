# Photo review workspace

Preserve the existing roundtrip wordmark and peach arrow. The photograph is the main content; collection navigation sits to its left and the edit conversation to its right. Earlier exports sit directly below the photograph. On small screens the collection becomes a horizontal strip and feedback follows the photo and versions.

Show the current export by default. Comparison is deliberate: a button reveals the existing in-image slider and the earlier-version selector. Detailed activity, edit settings, and product explanation use disclosure controls. Keep copy direct and labels in sentence case.

Palette: charcoal background #17191b, image stage #111315, panel #202326, text #eeeef0, muted text #adb2b8, and existing peach accent #e7b28c. Typography uses Avenir Next/Avenir with system fallbacks; the logo retains its previous stack. No new fonts, images, dependencies, or animation.

Verified desktop rendering at 1440px and mobile rendering at390px. Page overflow checks passed at1440,390,and320px. Comparison toggle and keyboard Home operation passed. Broader interaction testing remains future work.

Sources applied through the requested apply-design-best-practices skill:
- [Anthropic Frontend Design](https://github.com/anthropics/skills/blob/main/skills/frontend-design/SKILL.md): deliberate visual hierarchy and subject-specific design.
- [Vercel Web Interface Guidelines](https://github.com/vercel-labs/web-interface-guidelines/blob/main/command.md): semantic controls, focus, responsive overflow, and draft preservation.
