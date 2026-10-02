# Project Documentation

## Project Context

This repository documents a conceptual design study for a 5000 TEU container vessel completed as a university team project.

The design workflow covered:

- Principal-dimension definition
- Preliminary sectional-area distribution
- 3D hull modelling
- Lines-plan generation
- Comparison of initial and actual sectional-area curves
- Conceptual general arrangement
- Hydrostatic calculations
- Preliminary intact-stability analysis

## Design Requirements

The project considered the following principal requirements:

- Container capacity: 5000 TEU
- Design speed: 21 knots
- Design range: 6500 nautical miles
- Maximum beam: 35 m
- Maximum draught: 15 m

## Engineering Workflow

### 1. Preliminary Design

Principal dimensions and hydrostatic coefficients were established and used to develop an initial sectional-area distribution.

### 2. Hull Geometry

Station-based hull geometry was developed using Onshape. The hull was subsequently reviewed and processed in Rhino for geometric analysis and lines-plan generation.

### 3. Geometry Verification

Sectional areas were extracted from the developed 3D hull and compared with the initial sectional-area curve to assess preservation of the intended longitudinal volume distribution.

### 4. General Arrangement

A conceptual general arrangement was developed to examine the allocation of container bays, machinery spaces, fuel tanks, accommodation, and navigation spaces.

### 5. Hydrostatics and Stability

Hydrostatic properties were evaluated from the hull geometry. KN values were used in a preliminary stability workflow to construct a GZ curve and investigate transverse stability.

## Python and Rhino Automation

The repository contains retained Python scripts intended for use within the Rhino environment.

They support:

- Hydrostatic-property extraction
- Sectional-area extraction
- KN calculations
- Lines-plan generation

These scripts use Rhino-specific APIs and are not intended to run as standalone Python programs without the Rhino environment.

## Team Project Attribution

This was a three-person university team project.

The retained project documentation does not provide a reliable task-by-task breakdown of each team member's individual contribution.

**Individual contribution: Not confirmed from the uploaded files.**

Accordingly, this repository documents the engineering work as a team project rather than assigning specific work packages to an individual team member.

## Repository Scope

The original academic report is not published because it contains student identification and administrative information.

The public repository instead contains selected engineering scripts, visual results, numerical summaries, and project documentation suitable for portfolio presentation.
