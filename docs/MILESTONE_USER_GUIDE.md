# Milestone Save System - User Guide

## What Are Milestones?

Milestones are **read-only snapshots** of your workbook at important points in time. Think of them as checkpoints you can return to if needed.

### Key Benefits
- **Save Progress**: Capture your work at important stages
- **Safe to Experiment**: Edit confidently knowing you can always revert
- **Track Changes**: See exactly what changed since a milestone was saved
- **Create Branches**: Copy a milestone to start a new version without affecting the original

## How to Use Milestones

### 1. Creating a Milestone

A milestone saves the **entire workbook** including:
- Schedule data
- Financials
- Hardware lists
- All workbook files

**Steps:**
1. Complete your work (add items to Schedule, calculate Financials, etc.)
2. Right-click on the workbook → **Create Milestone**
3. Enter a descriptive name
4. (Optional) Add a description explaining what's in this milestone
5. Click Create

**Example Names:**
- ✅ "Initial Takeoff - All Doors Scheduled"
- ✅ "Client Review Draft v1"
- ✅ "Financials Complete - Waiting Approval"
- ❌ "v2" or "temp" (too vague)

### 2. Viewing and Managing Milestones

To see all milestones for a workbook:

1. Right-click on the workbook → **Manage Milestones**
2. A dialog shows all milestones with:
   - Name and creation date
   - Description
   - Available actions

### 3. Revert to a Milestone

If you made changes and want to go back to a previous state:

1. Open **Manage Milestones** for the workbook
2. Select the milestone you want to restore
3. Click **Revert to This Milestone**
4. The workbook returns to that exact state

⚠️ **Important**: This replaces ALL current workbook contents. If you want to keep your current work:
- Create a milestone BEFORE reverting
- Or use "Copy to New Workbook" instead

### 4. Copy Milestone to New Workbook

Create a new workbook starting from a previous milestone:

1. Open **Manage Milestones**
2. Select the milestone to copy
3. Click **Copy to New Workbook**
4. Enter a name for the new workbook
5. The new workbook is ready to edit

**Use Case**: Your client approved the "Initial Review" version, but now wants you to create a revised quote. Instead of starting from scratch, copy the approved milestone.

### 5. Compare with Current

See exactly what changed since a milestone was saved:

1. Open **Manage Milestones**
2. Select a milestone
3. Click **Compare with Current**
4. A report shows:
   - **Modified**: Files that changed
   - **Added**: New files since the milestone
   - **Removed**: Files deleted since the milestone

**Use Case**: You've made many edits and want to review what changed before submitting to the client.

### 6. Delete a Milestone

Remove a milestone you no longer need:

1. Open **Manage Milestones**
2. Select the milestone
3. Click **Delete Milestone**
4. Confirm the deletion

⚠️ **WARNING**: Deletion cannot be undone. Make sure you don't need this milestone first.

## Recommended Workflow

### Basic Workflow
```
1. Create new workbook
   ↓
2. Add all doors to Schedule
   ↓
3. Create Milestone: "Schedule Complete"
   ↓
4. Calculate Financials
   ↓
5. Create Milestone: "Financials Complete"
   ↓
6. Review and polish
   ↓
7. Create Milestone: "Final Bid Ready"
   ↓
8. Submit to client
```

### Client Revision Workflow
```
Initial Bid Created
   ↓
Create Milestone: "Client Revision 1 - Initial Bid"
   ↓
Receive client feedback
   ↓
Make changes to workbook
   ↓
Create Milestone: "Client Revision 2 - Updates"
   ↓
Compare with previous milestone to show client what changed
   ↓
Submit revised bid
```

### Branch/Experiment Workflow
```
Approved Version (Milestone: "Approved - v1")
   ↓
Client asks: "What if we used different hardware?"
   ↓
Copy "Approved - v1" → New workbook "Approved - v1 - Alt Hardware"
   ↓
Edit new workbook with different hardware
   ↓
Create Milestone: "Alternative Hardware Option"
   ↓
Compare with original to show differences
   ↓
Client picks which version they prefer
```

## Tips and Best Practices

✅ **DO:**
- Create milestones after completing major sections
- Use descriptive names that explain what's changed
- Create a milestone before making major revisions
- Use descriptions to document important decisions
- Create milestones when client approves something

❌ **DON'T:**
- Create too many milestones (becomes hard to find the right one)
- Use vague names like "v2" or "temp"
- Forget to create a milestone before reverting
- Delete old milestones without checking if you need them

## Milestone Naming Convention

### Recommended Format
```
[Stage]: [Description] - [Status/Details]
```

### Examples

**By Stage:**
- Takeoff Stage Milestones:
  - "Takeoff: All Doors Scheduled"
  - "Takeoff: Hardware Groups Assigned"
  
- Estimation Stage:
  - "Estimation: Material Costs Entered"
  - "Estimation: Labor Costs Calculated"
  
- Review Stage:
  - "Review: Ready for QC"
  - "Review: Final Bid Prepared"

**By Version/Revision:**
- "Version 1: Initial Estimate"
- "Version 2: Client Feedback Applied"
- "Version 3: Final Approved"

**By Client Request:**
- "Client Request: Material Upgrade v1"
- "Client Request: Cost Reduction Options"
- "Client Approval: Final Bid Accepted"

## FAQ

**Q: Can I edit a milestone?**
A: No, milestones are read-only. If you want to make changes, copy the milestone to a new workbook.

**Q: What happens if I delete a workbook with milestones?**
A: Milestones are stored inside the workbook folder, so they're deleted with the workbook.

**Q: Can I export a milestone?**
A: Milestones are stored in the `.milestones` folder within your workbook. You can manually copy them for backup.

**Q: How much disk space do milestones use?**
A: Each milestone is a complete copy of your workbook. Plan accordingly if your workbooks are large.

**Q: Can I rename a milestone?**
A: Currently, you can't rename milestones. Create a new one with the desired name and delete the old one.

**Q: Can I restore a single file from a milestone?**
A: Currently, revert restores the entire workbook. Future updates may add selective restore.

**Q: How many milestones can I create?**
A: As many as you want, limited by available disk space.

**Q: Are milestones backed up?**
A: Milestones are stored locally in the `.milestones` folder. Use your normal backup process.

## Troubleshooting

### "Failed to create milestone"
- Make sure the workbook location is writable
- Check that you have enough disk space
- The workbook may be locked by another process

### "Revert didn't work"
- Make sure the workbook is not locked
- Check that the `.milestones` folder still exists
- Try creating a new milestone from your current work first

### Can't find the milestone I created
- Milestones are listed in the Manage Milestones dialog
- They're created with a timestamp, so newest ones appear first
- If it doesn't appear, the creation may have failed

## Getting Started

1. **Create your first milestone** after completing your initial takeoff
2. **Make some edits** to get familiar with the system
3. **Compare** to see what changed
4. **Copy to new workbook** to create a test version
5. **Explore** the other features

Once you're comfortable, integrate milestones into your regular workflow!
