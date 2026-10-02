# Engineering Results

This directory summarizes selected results from the conceptual design of a 5000 TEU container vessel.

## Principal Design Parameters

- Container capacity: 5000 TEU
- Design speed: 21 knots
- Design range: 6500 nautical miles
- Length between perpendiculars (Lpp): 280 m
- Length overall (LOA): 294 m
- Beam: 34.8 m
- Design draught: 14.5 m
- Depth: 23.925 m
- Block coefficient (CB): 0.63
- Midship coefficient (CM): 0.985
- Prismatic coefficient (CP): 0.64
- Estimated displacement: 91,236.73 t

## Hull Geometry

A station-based 3D hull geometry was developed from the preliminary principal dimensions and sectional-area distribution.

The actual sectional-area curve extracted from the faired hull was compared with the initial design curve. The overall longitudinal volume distribution was retained, with deviations mainly around the bow and stern associated with hull-form refinement.

## Hydrostatics

The retained Rhino Python workflow supports calculation of quantities including:

- Submerged volume
- Block coefficient
- Waterplane area
- Longitudinal and vertical centers of buoyancy
- Transverse metacentric radius
- Wetted surface area
- Sectional-area distribution

## Preliminary Stability Analysis

A KN curve was evaluated at approximately constant displacement volume over the investigated heel-angle range.

The project report presents a limiting vertical center of gravity:

**KGmax = 13.064 m**

Using this value, the reported GZ curve reaches approximately:

**GZmax ≈ 0.85 m at about 30° heel**

and remains positive through the investigated range up to 60°.

## Scope

These results belong to a conceptual university ship-design project and should be interpreted as preliminary engineering results rather than detailed production-design or classification documentation.

Selected visual results are available in the `images/` directory.
