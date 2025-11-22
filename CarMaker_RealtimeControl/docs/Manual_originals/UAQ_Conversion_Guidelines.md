# UAQ Text to Markdown Conversion Guidelines

## Overview
Convert CarMaker UAQ reference manual text files to clean, structured Markdown format while preserving all technical information.

## File Structure

### 1. Main Title
- Use `# User Accessible Quantities: [Category Name]`
- Example: `# User Accessible Quantities: General & Control`

### 2. Section Headers
- Use `## [Section Number] [Section Name]` for major sections
- Example: `## 26.1 General`
- Use `### [Subsection Number] [Subsection Name]` for subsections
- Example: `### 26.1.1 TCPU`

### 3. Table Format
All UAQ data should be in 4-column tables:
```markdown
| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
```

## Conversion Rules

### 1. Page Markers
- Remove all `--- Page X ---` markers
- Merge content that spans across pages

### 2. Column Handling
- **UAQ Name**: The primary UAQ variable name (use backticks for code formatting)
- **C-Code**: The corresponding C-code variable name (use backticks, use `-` if empty)
- **Unit**: The measurement unit (e.g., s, m/s, rad, Nm)
- **Info**: Description and additional information

### 3. Data Type Handling

#### Vectors and Arrays
- For 3D vectors, use slash notation: `x/y/z`
- Example: `Vhcl.Fr1.x/y/z` instead of separate rows
- For arrays: `DM.DigitalSelectorCtrl[0]`

#### Template Variables
- Preserve template variables: `<pos>`, `<pre>`, `<kind>`, `<i>`
- Add explanations in the Info column where needed
- Example: `<pos> := FL, FR, RL, RR` (for wheel positions)

### 4. Text Formatting

#### Variable Names
- Wrap all variable names in backticks: `Variable.Name`
- Keep dot notation: `DM.Lights.FogFront`

#### Special Characters
- Fix ligatures: "ﬂ" → "fl", "ﬁ" → "fi"
- Fix spacing issues and line breaks within cells

#### Multi-line Cell Content
- Keep related information in single cells
- Use commas or semicolons to separate values
- Example: `0: Initial, 1: Standby, 2: Running, 3: Complete, 4: Final`

### 5. Complex Data Structures

#### Multiple Related Variables
- Combine when logical (e.g., left/right pairs)
- Example: `VC.Lights.FogFrontL/R`

#### C-Code Arrays
- Show array notation: `Vehicle.WindVel_ext[0]` for x component
- Or use simplified notation if multiple: `Vehicle.Fr1A.t_0`

### 6. Info Column Guidelines

#### Value Ranges
- Specify ranges clearly: `(0..1)`, `(-18..16)`
- Boolean values: note as `(boolean)`
- Integer values: note as `(integer)`

#### Enumerated Values
- List options inline with separators
- Example: `0=Off, 1=On, 2=Automatic`

#### Multi-state Variables
- Format: `0: State1, 1: State2, 2: State3`
- Keep on single line if reasonable

### 7. Section Organization

#### Maintain Original Structure
- Keep section numbers from original document
- Preserve hierarchical organization
- Don't skip empty sections if they exist in original

#### Group Related Items
- Keep related UAQs together (e.g., all `DM.Lights.*` variables)
- Maintain logical flow from original document

## Quality Checks

1. **Completeness**: All UAQs from original file must be present
2. **Accuracy**: No merged or split data that changes meaning
3. **Readability**: Clean formatting without unnecessary line breaks
4. **Consistency**: Same formatting style throughout document
5. **Technical Precision**: Units and data types preserved exactly

## Common Issues to Avoid

1. **Don't split vector components** into separate rows unnecessarily
2. **Don't lose C-Code mappings** - preserve all technical references
3. **Don't merge unrelated cells** - keep distinct information separate
4. **Don't remove data type information** (float, integer, boolean, etc.)
5. **Don't skip template variable definitions** (`<pos>`, `<kind>`, etc.)

## Example Conversion

### Original:
```
Name UAQ Name C-CodeName CarMaker for
SimulinkUnit Info (data type, if not double)
DM.Brake DrivMan.Brake DrivMan Brake - Brake/decelerator activity, relative pedal force (0..1)
```

### Converted:
```markdown
| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `DM.Brake` | `DrivMan.Brake` | - | Brake/decelerator activity, relative pedal force (0..1) |
```

## Final Notes
- When in doubt, preserve more information rather than less
- Maintain technical accuracy over aesthetic preferences
- Check the final output against the original for completeness