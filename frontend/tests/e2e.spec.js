import { test, expect } from '@playwright/test';
import fs from 'fs';
import path from 'path';

test.describe('Intelligent Static Bug Prediction E2E', () => {
  const username = `testuser_${Date.now()}`;
  const password = 'password123';
  const username2 = `testuser2_${Date.now()}`;

  test.beforeEach(async ({ page }) => {
    // Go to login page
    await page.goto('http://localhost:5173/login');
  });

  test('full verification flow', async ({ page, context }) => {
    // 1. Register and Login
    await page.fill('input[name="username"]', username);
    await page.fill('input[name="password"]', password);
    await page.click('button:has-text("Register")');
    await expect(page.locator('text=Your projects')).toBeVisible({ timeout: 10000 });

    // Dark mode toggle test
    const html = page.locator('html');
    await page.click('button[title="Toggle dark mode"]');
    await expect(html).toHaveClass(/dark/);
    await page.click('button[title="Toggle dark mode"]');
    await expect(html).not.toHaveClass(/dark/);

    // 2. Upload real_bugs_sample.py
    await page.click('button:has-text("New analysis"), button:has-text("New Analysis")');
    await page.fill('input[type="text"]', 'Real Bugs Project');
    
    await page.locator('input[type="file"]').setInputFiles('../real_bugs_sample.py');
    await page.click('button:has-text("Upload")');

    // 3. Instant code display & analysis progress
    await expect(page.locator('text=Code review').first()).toBeVisible({ timeout: 60000 });
    await expect(page.locator('text=real_bugs_sample.py').first()).toBeVisible({ timeout: 60000 });
    await expect(page.locator('text=Analysis running...')).toBeHidden({ timeout: 60000 });

    // 4. Navigate to Ranked Results
    await page.locator('button').filter({ hasText: 'Results' }).last().click();
    await expect(page.locator('text=Function risk ranking').first()).toBeVisible({ timeout: 10000 });
    
    await expect(page.locator('tbody tr td:first-child div.font-bold').first()).toBeVisible({ timeout: 10000 });

    // 5. Verify real_bugs_sample.py pattern findings & ML risks
    const functionNames = await page.locator('tbody tr td:first-child div.font-bold').allTextContents();
    
    // ship_order ranks higher than tiny functions
    const shipOrderIdx = functionNames.findIndex(n => n.includes('ship_order'));
    const addIdx = functionNames.findIndex(n => n.includes('add'));
    expect(shipOrderIdx).toBeLessThan(addIdx);
    
    // Check pattern findings by clicking on functions
    const verifyFindings = async (funcName, patterns) => {
      await page.locator(`tr:has-text("${funcName}") >> button`).first().click();
      await expect(page.locator(`h1:has-text("${funcName}")`)).toBeVisible({ timeout: 10000 });
      for (const pattern of patterns) {
        await expect(page.locator(`text=${pattern}`).first()).toBeVisible();
      }
      await page.click('button:has-text("Back to results")');
    };

    await verifyFindings('loop_example', ['Possible off-by-one error']);
    await verifyFindings('process_data', ['Mutable default argument is shared']);
    await verifyFindings('handle_error', ['Bare except clause', 'Empty error handler']);
    await verifyFindings('auth_check', ['Condition with literal OR is always true']);
    await verifyFindings('calculate', ['Comparison used as a statement has no effect']);
    await verifyFindings('read_file', ['Resource opened but not closed']);

    // Tiny functions should not be High
    await page.locator('tr:has-text("add") >> button').first().click();
    await expect(page.locator('h1:has-text("add")')).toBeVisible();
    await expect(page.locator('text=High')).toBeHidden();
    
    // Feedback
    await page.click('button:has-text("Yes, it\'s a bug")');
    await expect(page.locator('text=Feedback saved')).toBeVisible();
    await page.click('button:has-text("Back to results")');

    // Filters (filter out clean functions)
    await page.selectOption('select:has-text("All Levels")', { label: 'High' });
    await expect(page.locator('text=add')).toBeHidden();
    await page.selectOption('select:has-text("High")', { label: 'All Levels' });

    // 6. Upload sample_buggy_code.py
    await page.click('a:has-text("Projects")');
    await page.click('button:has-text("New analysis"), button:has-text("New Analysis")');
    await page.fill('input[type="text"]', 'Sample Buggy Project');
    
    await page.locator('input[type="file"]').setInputFiles('../sample_buggy_code.py');
    await page.click('button:has-text("Upload")');
    await expect(page.locator('text=Analysis running...')).toBeHidden({ timeout: 60000 });

    await page.locator('button').filter({ hasText: 'Results' }).last().click();
    await verifyFindings('authenticate_user', ['SQL injection']);
    await verifyFindings('execute_system_command', ['command execution']);
    await verifyFindings('evaluate_math_expression', ['Insecure use of eval']);
    await verifyFindings('process_data', ['Possible off-by-one error']);
    await verifyFindings('run_background_task', ['shell=True']);

    // Hardcoded secret is file-level, check if it's assigned to any function (likely module-level/first function)
    // Or just look for the text in the results or code viewer
    await page.click('button:has-text("Files")');
    await page.locator('tr:has-text("sample_buggy_code.py") >> button').first().click();
    await expect(page.locator('text=Hardcoded secret')).toBeVisible();

    // 7. Upload test_project.zip
    await page.click('a:has-text("Projects")');
    await page.click('button:has-text("New analysis"), button:has-text("New Analysis")');
    await page.fill('input[type="text"]', 'Zip Project');
    
    await page.locator('input[type="file"]').setInputFiles('../test_project.zip');
    await page.click('button:has-text("Upload")');
    await expect(page.locator('text=Analysis running...')).toBeHidden({ timeout: 60000 });
    
    // Check broken file and unsupported file
    await expect(page.locator('text=broken_syntax.py')).toBeVisible();
    await expect(page.locator('text=notes.txt')).toBeVisible();
    await expect(page.locator('text=skipped').first()).toBeVisible();
    await expect(page.locator('text=unsupported').first()).toBeVisible();

    // 8. Model performance removed as per requirements

    // 9. Export
    await page.click('a:has-text("Projects")');
    await page.locator('h3').filter({ hasText: 'Zip Project' }).first().click();
    await page.locator('button').filter({ hasText: 'Results' }).last().click();
    const [download] = await Promise.all([
      page.waitForEvent('download'),
      page.click('button:has-text("Export JSON")')
    ]);
    expect(download.suggestedFilename()).toContain('export.json');

    // Get current URL for cross-user test
    const projectUrl = page.url();

    // 10. Logout and Cross-user access denied
    await page.click('button[title="Logout"], button:has-text("Logout"), a:has-text("Logout")');
    await expect(page.locator('text=Sign in or Register')).toBeVisible({ timeout: 10000 });

    // Register user 2
    await page.fill('input[name="username"]', username2);
    await page.fill('input[name="password"]', password);
    await page.click('button:has-text("Register")');
    await expect(page.locator('text=Your projects')).toBeVisible({ timeout: 10000 });

    // Try to access user 1's project
    const response = await page.goto(projectUrl);
    // Should be redirected or show 404/Error
    await expect(page.locator('text=Not Found').or(page.locator('text=Error')).or(page.locator('text=not found', { exact: false }))).toBeVisible();
  });
});
