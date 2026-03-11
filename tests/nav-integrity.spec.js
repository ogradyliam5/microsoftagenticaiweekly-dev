const { test, expect } = require('@playwright/test');

const corePages = ['/', '/archive', '/about', '/subscribe'];

function normalizeToLocalPath(href) {
  if (!href || href.startsWith('mailto:') || href.startsWith('javascript:') || href.startsWith('#')) {
    return null;
  }
  const url = new URL(href, 'http://127.0.0.1:4321');
  return `${url.pathname}${url.search}`;
}

test.describe('nav and route integrity', () => {
  for (const path of corePages) {
    test(`core page loads and header nav links resolve: ${path}`, async ({ page, request }) => {
      const response = await page.goto(path);
      expect(response, `missing response for ${path}`).not.toBeNull();
      expect(response.status(), `unexpected status for ${path}`).toBeLessThan(400);

      await expect(page.locator('[data-theme-toggle]').first()).toBeVisible();
      await expect(page.locator('h1, h2').first()).toBeVisible();

      const navLinks = page.locator('header nav a[href]');
      const hrefs = await navLinks.evaluateAll((anchors) => anchors.map((a) => a.getAttribute('href') || ''));
      const uniquePaths = [...new Set(hrefs.map(normalizeToLocalPath).filter(Boolean))];

      for (const linkPath of uniquePaths) {
        const linkResponse = await request.get(linkPath);
        expect(linkResponse.status(), `broken nav link from ${path}: ${linkPath}`).toBeLessThan(400);
      }
    });
  }

  test('latest issue path matches across home, archive, and feed', async ({ page, request }) => {
    await page.goto('/');
    const homeLatest = await page.locator('a[href^="/posts/issue-"]').first().getAttribute('href');
    expect(homeLatest).toBeTruthy();

    await page.goto('/archive');
    const archiveLatest = await page.locator('a[href^="/posts/issue-"]').first().getAttribute('href');
    expect(archiveLatest).toBeTruthy();

    const feedResponse = await request.get('/feed.xml');
    expect(feedResponse.status()).toBeLessThan(400);
    const feedText = await feedResponse.text();
    const match = feedText.match(/<link>([^<]*\/posts\/issue-[^<]+)<\/link>/);
    expect(match, 'feed must include issue link').toBeTruthy();
    const feedLatestPath = new URL(match[1]).pathname;

    expect(homeLatest).toBe(archiveLatest);
    expect(homeLatest).toBe(feedLatestPath);

    const latestIssueResponse = await request.get(homeLatest);
    expect(latestIssueResponse.status()).toBeLessThan(400);
  });
});
