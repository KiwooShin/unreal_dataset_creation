# Wrap-Up Instructions

When the user asks to "wrap up", follow these steps in order.

## 1. Move Output Files to Results

Move all files from `dataset_output/` to `results/{MMDDYYYY}/` where `{MMDDYYYY}` is today's date.

```bash
mkdir -p results/{MMDDYYYY}
mv dataset_output/* results/{MMDDYYYY}/
```

## 2. Create Progress Summary

Create `progress/{MMDDYYYY}_{short_description}.md` with:

```markdown
# Progress Report: {Month Day, Year}

## Summary
{1-2 sentence summary of what was done today}

## Completed Tasks
### 1. {Task name}
- {Details}

## Current Configuration
{Show current step1 config: objects, positions, colors, scales}

## Next Steps
- {What to do next}
```

Use short_description as 2-3 words describing the main work (e.g., `multi_object_scene`, `color_material_fix`).

## 3. Git Commit and Push

```bash
git add results/{MMDDYYYY}/ progress/{MMDDYYYY}_*.md step1_setup_scene.py step2_take_screenshot.py unreal_api_server_v2.py
git commit -m "{concise description of today's changes}"
git push
```

Only add files that were actually modified. Include result images and progress summary.
