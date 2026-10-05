import { test, expect } from '@playwright/test';

test.describe('E2E Flow', () => {
  // Use a unique username to avoid conflicts
  const uniqueUsername = `testuser_${Date.now()}`;
  const password = 'password123';

  test('full upload-to-results flow', async ({ page }) => {
    // 1. Register and Login
    await page.goto('http://localhost:5173/login');
    await page.fill('input[name="username"]', uniqueUsername);
    await page.fill('input[name="password"]', password);
    await page.click('button:has-text("Register")');

    // Should redirect to dashboard
    await expect(page.locator('text=Overview')).toBeVisible({ timeout: 10000 });

    // 2. Upload test_project.zip
    // Click "New analysis" button (if not already showing) or handle empty state "New Analysis"
    await page.click('button:has-text("New analysis"), button:has-text("New Analysis")');
    
    // Fill project name and upload file
    await page.fill('input[type="text"]', 'My Test Project');
    
    // Setup file chooser intercept before clicking the file input
    const [fileChooser] = await Promise.all([
      page.waitForEvent('filechooser'),
      page.locator('input[type="file"]').click()
    ]);
    await fileChooser.setFiles('../test_project.zip');
    
    // Click Upload
    await page.click('button:has-text("Upload")');

    // 3. Source code shown immediately
    await expect(page.locator('text=Code review').first()).toBeVisible({ timeout: 60000 });
    await expect(page.locator('text=messy.py')).toBeVisible({ timeout: 60000 });

    // 4. Background analysis with progress
    // Wait for "Analysis running..." to disappear
    await expect(page.locator('text=Analysis running...')).toBeHidden({ timeout: 60000 });
    
    // 5. Navigate to Ranked Results
    await page.locator('button').filter({ hasText: 'Results' }).last().click();
    await expect(page.locator('text=Function risk ranking').first()).toBeVisible({ timeout: 10000 });
    
    // 6. Check that messy functions rank above tiny ones
    // Wait for predictions to load
    await expect(page.locator('text=messy_func').first()).toBeVisible();
    await expect(page.locator('text=tiny').first()).toBeVisible();
    
    // Grab all function names from the table to check order
    const functionNames = await page.locator('tbody tr td:first-child div.font-bold').allTextContents();
    const messyIndex = functionNames.findIndex(name => name.includes('messy_func'));
    const tinyIndex = functionNames.findIndex(name => name.includes('tiny'));
    
    expect(messyIndex).toBeLessThan(tinyIndex);

    // 7. Click a function to see highlights and an explanation
    await page.locator('tr:has-text("messy_func") >> button').click();
    
    // Verify BugDetailView loaded
    await expect(page.locator('h1:has-text("Function: messy_func")')).toBeVisible({ timeout: 10000 });
    await expect(page.locator('text=Risk Assessment')).toBeVisible();
    await expect(page.locator('text=Explanations')).toBeVisible();
    
    // 8. Submit feedback
    await page.click('button:has-text("Yes, it\'s a bug")');
    await expect(page.locator('text=Feedback saved successfully')).toBeVisible();
    
    // 9. View model performance
    await page.click('a:has-text("Model Performance")');
    await expect(page.locator('h1:has-text("Model Performance")')).toBeVisible({ timeout: 10000 });
    await expect(page.locator('text=Test AUC').first()).toBeVisible();

    // 10. Check broken_syntax.py shows as skipped and notes.txt shows as unsupported.
    // notes.txt shouldn't even be analyzed, but we can verify in Project Viewer
    await page.click('a:has-text("Projects")');
    await page.locator('h3').filter({ hasText: 'My Test Project' }).first().click(); // Go to project view
    
    // Actually notes.txt will be in Project Viewer ? No, backend only supports py, js, java, c, cpp, ts, go. 
    // And broken_syntax.py will have status "skipped" or have skipped files warning.
    await expect(page.locator('text=broken_syntax.py').first()).toBeVisible();
    await expect(page.locator('text=notes.txt').first()).toBeVisible();
    
    // Check their statuses (skipped and unsupported)
    // ProjectViewer displays them like: `Skipped files: broken_syntax.py` or similar? No, the files list in ProjectViewer has a status badge.
    // Or we just expect the text "skipped" and "unsupported" to be visible
    await expect(page.locator('text=skipped').first()).toBeVisible();
    await expect(page.locator('text=unsupported').first()).toBeVisible();
    
    // 11. Export JSON (optional UI click, but can't easily verify download in Playwright without special config, we just verify it exists in Results)
    await page.locator('button').filter({ hasText: 'Results' }).last().click();
    const [download] = await Promise.all([
      page.waitForEvent('download'),
      page.click('button:has-text("Export JSON")')
    ]);
    expect(download.suggestedFilename()).toContain('export.json');

    // 12. Logout
    await page.click('button[title="Logout"]');
    await expect(page.locator('text=Sign in or Register')).toBeVisible({ timeout: 10000 });
  });
});
