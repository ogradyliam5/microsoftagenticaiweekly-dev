const { test, expect } = require('@playwright/test');
const AxeBuilder = require('@axe-core/playwright').default;

test.setTimeout(180000);

const pages = [
  '/',
  '/archive',
  '/about',
  '/subscribe',
  '/posts/issue-2026-10'
];

test('a11y smoke: core Astro routes', async ({ page }) => {
  for (const path of pages) {
    await page.goto(path);

    const results = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa'])
      .analyze();

    const violations = results.violations.map((violation) => ({
      id: violation.id,
      impact: violation.impact,
      description: violation.description,
      nodes: violation.nodes.length,
      path
    }));

    expect(violations).toEqual([]);
  }
});
