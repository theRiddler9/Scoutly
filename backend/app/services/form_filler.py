"""
Scoutly — Form Filler Service (Playwright-based form auto-fill agent)

SAFETY: This service NEVER auto-submits forms.
It fills all fields and takes a screenshot for human review.
Submission only happens after explicit approval via the /approve endpoint.
"""

import json
import logging
import asyncio
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright
from app.config import SCREENSHOTS_DIR
from app.database import fetch_one, execute_insert, execute_update, get_db
from app.services.llm_client import llm_client
from app.prompts.fill_form import FILL_FORM_PROMPT

logger = logging.getLogger(__name__)


async def _extract_form_fields(page) -> list[dict]:
    """Extract all form fields from the page with their labels, types, and attributes."""
    fields = await page.evaluate("""
        () => {
            const fields = [];
            const inputs = document.querySelectorAll(
                'input, textarea, select, [contenteditable="true"]'
            );

            inputs.forEach((el, index) => {
                // Skip hidden and submit/button inputs
                const type = el.getAttribute('type') || el.tagName.toLowerCase();
                if (type === 'hidden' || type === 'submit' || type === 'button') return;

                // Find associated label
                let label = '';
                const id = el.getAttribute('id');
                if (id) {
                    const labelEl = document.querySelector(`label[for="${id}"]`);
                    if (labelEl) label = labelEl.innerText.trim();
                }
                if (!label) {
                    // Check parent label
                    const parentLabel = el.closest('label');
                    if (parentLabel) label = parentLabel.innerText.trim();
                }
                if (!label) {
                    // Use aria-label or placeholder
                    label = el.getAttribute('aria-label') ||
                            el.getAttribute('placeholder') ||
                            el.getAttribute('name') || '';
                }

                // Get options for select elements
                let options = [];
                if (el.tagName.toLowerCase() === 'select') {
                    Array.from(el.options).forEach(opt => {
                        if (opt.value) options.push({value: opt.value, text: opt.text});
                    });
                }

                fields.push({
                    index: index,
                    dom_index: index,
                    field_id: id || el.getAttribute('name') || `field_${index}`,
                    tag: el.tagName.toLowerCase(),
                    type: type,
                    label: label,
                    placeholder: el.getAttribute('placeholder') || '',
                    required: el.hasAttribute('required'),
                    options: options,
                    name: el.getAttribute('name') || '',
                });
            });

            return fields;
        }
    """)
    return fields


async def _fill_field(page, field: dict, value: str, action: str):
    """Fill a single form field using Playwright."""
    try:
        # Use the DOM position from the same selector used during extraction.
        # This handles duplicated names and IDs containing CSS-special chars.
        element = page.locator(
            'input, textarea, select, [contenteditable="true"]'
        ).nth(field.get("dom_index", field.get("index", 0)))

        if action == "fill":
            if field["tag"] == "select":
                try:
                    await element.select_option(value=str(value))
                except Exception:
                    await element.select_option(label=str(value))
            elif field["type"] in ("checkbox", "radio"):
                if str(value).lower() in ("true", "yes", "1"):
                    await element.check()
            else:
                await element.fill(value)

        elif action == "select":
            try:
                await element.select_option(value=str(value))
            except Exception:
                await element.select_option(label=str(value))

        elif action == "check":
            if value.lower() in ("true", "yes", "1"):
                await element.check()

        elif action == "upload":
            # value should be a file path
            if Path(value).exists():
                await element.set_input_files(value)
            else:
                logger.warning(f"File not found for upload: {value}")

        logger.info(f"Filled field '{field.get('label', field.get('field_id'))}' with action={action}")

    except Exception as e:
        logger.error(f"Failed to fill field {field.get('field_id')}: {e}")


async def fill_application(opportunity_id: int, profile_id: int = 1) -> dict:
    """
    Auto-fill an application form for a given opportunity.

    Process:
    1. Look up the opportunity and profile
    2. Open the application URL with Playwright
    3. Extract form fields
    4. Use LLM to map fields to profile data
    5. Fill each field
    6. Take a screenshot
    7. STOP — do NOT submit

    Returns:
        Dict with application_id, screenshot_path, and field details
    """
    # Get opportunity and match
    opportunity = await fetch_one(
        "SELECT * FROM opportunities WHERE id = ?", (opportunity_id,)
    )
    if not opportunity:
        return {"status": "error", "message": f"Opportunity {opportunity_id} not found"}

    # Get profile
    profile = await fetch_one("SELECT * FROM profiles WHERE id = ?", (profile_id,))
    if not profile:
        return {"status": "error", "message": f"Profile {profile_id} not found"}

    # Parse profile JSON fields
    profile_data = {
        "name": profile["name"],
        "email": profile["email"],
        "github_url": profile["github_url"],
        "skills": json.loads(profile.get("skills", "[]")),
        "projects": json.loads(profile.get("projects", "[]")),
        "resume_text": profile.get("resume_text", ""),
        "social_handles": json.loads(profile.get("social_handles", "{}")),
    }

    # Get or create match
    match = await fetch_one(
        "SELECT * FROM matches WHERE profile_id = ? AND opportunity_id = ?",
        (profile_id, opportunity_id)
    )
    if not match:
        match_id = await execute_insert(
            "INSERT INTO matches (profile_id, opportunity_id, score, reasoning) VALUES (?, ?, 0, 'Auto-created for form fill')",
            (profile_id, opportunity_id)
        )
    else:
        match_id = match["id"]

    # Create application record
    application_id = await execute_insert(
        "INSERT INTO applications (match_id, status) VALUES (?, 'filling')",
        (match_id,)
    )

    apply_url = opportunity["apply_url"]
    if not apply_url:
        await execute_update(
            "UPDATE applications SET status = 'failed', error_message = 'No application URL' WHERE id = ?",
            (application_id,)
        )
        return {"status": "error", "message": "No application URL for this opportunity"}

    logger.info(f"Starting form fill for opportunity: {opportunity['name']} at {apply_url}")

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                           "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = await context.new_page()

            # Navigate to application form
            # Analytics and websocket requests can keep networkidle open
            # forever even when the form is ready.
            await page.goto(apply_url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(1500)

            # Extract form fields
            form_fields = await _extract_form_fields(page)
            logger.info(f"Found {len(form_fields)} form fields")

            if not form_fields:
                # Take screenshot anyway — might be a non-standard form
                screenshot_path = str(
                    Path(SCREENSHOTS_DIR) / f"app_{application_id}_nofields.png"
                )
                await page.screenshot(path=screenshot_path, full_page=True)

                await execute_update(
                    "UPDATE applications SET status = 'failed', error_message = 'No form fields detected', screenshot_path = ? WHERE id = ?",
                    (screenshot_path, application_id)
                )
                await browser.close()
                return {
                    "status": "warning",
                    "message": "No form fields detected on the page",
                    "application_id": application_id,
                    "screenshot_path": screenshot_path,
                }

            # Ask LLM to map fields to profile data
            llm_payload = {
                "form_fields": form_fields,
                "profile": profile_data,
                "opportunity": {
                    "name": opportunity["name"],
                    "description": opportunity.get("description", ""),
                },
            }

            llm_result = await llm_client.call(
                system_prompt=FILL_FORM_PROMPT,
                user_payload=llm_payload,
                json_mode=True,
            )

            field_mappings = llm_result.get("fields", []) if isinstance(llm_result, dict) else []
            if not isinstance(field_mappings, list):
                field_mappings = []
            filled_fields = []

            # Fill each field
            for mapping in field_mappings:
                action = mapping.get("action", "skip")
                if action == "skip":
                    logger.info(f"Skipping field: {mapping.get('field_label', 'unknown')}")
                    continue

                # Find the original field info
                field_id = mapping.get("field_id", "")
                original_field = next(
                    (f for f in form_fields if f.get("field_id") == field_id),
                    None
                )

                if original_field:
                    await _fill_field(page, original_field, mapping.get("value", ""), action)
                    filled_fields.append(mapping)

                    # Log the field fill
                    await execute_insert(
                        """INSERT INTO field_logs
                           (application_id, field_label, field_type, filled_value, reasoning)
                           VALUES (?, ?, ?, ?, ?)""",
                        (
                            application_id,
                            mapping.get("field_label", ""),
                            mapping.get("action", ""),
                            mapping.get("value", ""),
                            mapping.get("reasoning", ""),
                        )
                    )

            # Take screenshot of filled form
            await page.wait_for_timeout(1000)  # Let any animations settle
            screenshot_filename = f"app_{application_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            screenshot_path = str(Path(SCREENSHOTS_DIR) / screenshot_filename)
            await page.screenshot(path=screenshot_path, full_page=True)

            logger.info(f"Screenshot saved: {screenshot_path}")

            # Update application record
            await execute_update(
                """UPDATE applications
                   SET status = 'awaiting_approval',
                       form_data = ?,
                       screenshot_path = ?,
                       filled_at = datetime('now')
                   WHERE id = ?""",
                (json.dumps(filled_fields), screenshot_path, application_id)
            )

            await browser.close()

        return {
            "status": "filled",
            "application_id": application_id,
            "screenshot_path": screenshot_path,
            "fields_filled": len(filled_fields),
            "fields_total": len(form_fields),
            "message": "Form filled successfully. Awaiting human approval before submission.",
        }

    except Exception as e:
        logger.error(f"Form fill failed: {e}")
        await execute_update(
            "UPDATE applications SET status = 'failed', error_message = ? WHERE id = ?",
            (str(e), application_id)
        )
        return {"status": "error", "message": str(e), "application_id": application_id}


async def submit_application(application_id: int) -> dict:
    """
    Submit a previously filled application after human approval.

    SAFETY: This only runs after explicit human approval via the API.
    """
    application = await fetch_one(
        "SELECT * FROM applications WHERE id = ?", (application_id,)
    )
    if not application:
        return {"status": "error", "message": "Application not found"}

    if application["status"] != "approved":
        return {"status": "error", "message": f"Application must be approved before submission. Current status: {application['status']}"}

    # Get the opportunity URL
    match = await fetch_one(
        "SELECT * FROM matches WHERE id = ?", (application["match_id"],)
    )
    if not match:
        return {"status": "error", "message": "Match record not found"}

    opportunity = await fetch_one(
        "SELECT * FROM opportunities WHERE id = ?", (match["opportunity_id"],)
    )
    if not opportunity:
        return {"status": "error", "message": "Opportunity not found"}

    form_data = json.loads(application.get("form_data", "[]"))

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                           "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = await context.new_page()

            await page.goto(opportunity["apply_url"], wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(2000)

            # Re-extract and re-fill fields
            form_fields = await _extract_form_fields(page)
            for mapping in form_data:
                action = mapping.get("action", "skip")
                if action == "skip":
                    continue
                field_id = mapping.get("field_id", "")
                original_field = next(
                    (f for f in form_fields if f.get("field_id") == field_id),
                    None
                )
                if original_field:
                    await _fill_field(page, original_field, mapping.get("value", ""), action)

            # Look for submit button and click it
            submit_selectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                'button:has-text("Submit")',
                'button:has-text("Apply")',
                'button:has-text("Send")',
            ]

            submitted = False
            for selector in submit_selectors:
                try:
                    submit_btn = page.locator(selector).first
                    if await submit_btn.is_visible():
                        await submit_btn.click()
                        submitted = True
                        break
                except Exception:
                    continue

            if submitted:
                await page.wait_for_timeout(3000)

                # Take post-submit screenshot
                post_screenshot = str(
                    Path(SCREENSHOTS_DIR) / f"app_{application_id}_submitted.png"
                )
                await page.screenshot(path=post_screenshot, full_page=True)

                await execute_update(
                    """UPDATE applications
                       SET status = 'submitted', submitted_at = datetime('now')
                       WHERE id = ?""",
                    (application_id,)
                )

                await browser.close()
                return {
                    "status": "submitted",
                    "message": "Application submitted successfully!",
                    "screenshot_path": post_screenshot,
                }
            else:
                await browser.close()
                return {
                    "status": "error",
                    "message": "Could not find submit button on the page",
                }

    except Exception as e:
        logger.error(f"Submission failed: {e}")
        await execute_update(
            "UPDATE applications SET status = 'failed', error_message = ? WHERE id = ?",
            (str(e), application_id)
        )
        return {"status": "error", "message": str(e)}
