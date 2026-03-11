const { test, expect } = require('@playwright/test');

const pages = [
  { name: 'home', path: '/' },
  { name: 'archive', path: '/archive' },
  { name: 'about', path: '/about' },
  { name: 'older-post', path: '/posts/issue-001' }
];

async function currentTheme(page) {
  return page.evaluate(() => document.documentElement.getAttribute('data-theme'));
}

async function clickToggle(page) {
  await page.locator('[data-theme-toggle]').first().click();
}

test.describe('theme toggle and persistence', () => {
  for (const entry of pages) {
    test(`${entry.name}: toggles both ways and persists after reload`, async ({ page }) => {
      await page.goto(entry.path);

      await expect(page.locator('[data-theme-toggle]').first()).toBeVisible();

      const initial = await currentTheme(page);
      expect(['light', 'dark']).toContain(initial);

      await clickToggle(page);
      const afterFirstToggle = await currentTheme(page);
      expect(afterFirstToggle).toBe(initial === 'dark' ? 'light' : 'dark');

      await page.reload();
      await expect.poll(() => currentTheme(page)).toBe(afterFirstToggle);

      await clickToggle(page);
      const afterSecondToggle = await currentTheme(page);
      expect(afterSecondToggle).toBe(initial);

      await page.reload();
      await expect.poll(() => currentTheme(page)).toBe(initial);
    });
  }
});

test('shared header visuals match between home and issue pages in both modes', async ({ page }) => {
  async function headerSnapshot(path, theme) {
    await page.goto(path);
    await page.evaluate((t) => {
      localStorage.setItem('maiw-theme', t);
      document.documentElement.setAttribute('data-theme', t);
      document.documentElement.classList.remove('theme-dark', 'theme-light');
      document.documentElement.classList.add(t === 'dark' ? 'theme-dark' : 'theme-light');
    }, theme);
    await page.reload();

    return page.evaluate(() => {
      const header = document.querySelector('header.sticky, header.site-header');
      const toggle = document.querySelector('[data-theme-toggle]');
      const navLink = document.querySelector('header nav a[href="/topics"]');
      const csHeader = getComputedStyle(header);
      const csToggle = getComputedStyle(toggle);
      const csNavLink = getComputedStyle(navLink);
      return {
        headerBorderColor: csHeader.borderBottomColor,
        headerBackgroundColor: csHeader.backgroundColor,
        toggleBorderColor: csToggle.borderColor,
        toggleColor: csToggle.color,
        navColor: csNavLink.color
      };
    });
  }

  for (const theme of ['light', 'dark']) {
    const home = await headerSnapshot('/', theme);
    const post = await headerSnapshot('/posts/issue-001', theme);

    expect(home).toEqual(post);
  }
});
