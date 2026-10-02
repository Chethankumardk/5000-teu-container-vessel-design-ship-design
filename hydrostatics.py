#! python 3
# r: numpy
# requirements: numpy

import rhinoscriptsyntax as rs
import numpy as np
import csv
import os

# ---------------------------------------------------------------------
# USER VARIABLES
# ---------------------------------------------------------------------

# Assumed rudder axis center position (default is 0) for Lpp calculation
rudder_pos = 0

# ---------------------------------------------------------------------
# USER VARIABLES
# ---------------------------------------------------------------------

def main():
    # Let user pick the closed polysurface (the hull)
    brep_id = rs.GetObject("Select closed polysurface (the hull)", rs.filter.polysurface)
    if not brep_id or not rs.IsObjectSolid(brep_id):
        rs.MessageBox("Selected object is not a closed polysurface. Aborting.")
        return
    
    # --- Ask for draft ---
    draft = rs.GetReal("Enter draft (distance from keel upward)", 1.0, 0.0)
    if draft is None: return

    # --- Compute bounding box and waterplane ---
    bbox = rs.BoundingBox(brep_id)
    z_min = min(p.Z for p in bbox)
    z_water = z_min + draft

    xmin_loa = min(p.X for p in bbox)
    xmax_loa = max(p.X for p in bbox)

    LOA = xmax_loa - xmin_loa

    # --- Split hull with a waterplane ---
    plane = rs.WorldXYPlane()
    plane.OriginZ = z_water
    waterplane = rs.AddPlaneSurface(plane, 1000, 1000)
    rs.MoveObject(waterplane, (-500, -500, 0))
    extrudeCrv = rs.AddLine((plane.OriginX, plane.OriginY, plane.OriginZ), (plane.OriginX, plane.OriginY, 500))
    watercube = rs.ExtrudeSurface(waterplane, extrudeCrv)

    rs.DeleteObject(extrudeCrv)
    
    # Keep only the submerged part (below waterline)
    submerged = rs.BooleanDifference([brep_id], [watercube], False)
    vol = rs.SurfaceVolume(submerged)[0]
    centroid = rs.SurfaceVolumeCentroid(submerged)[0][0]

    sub_bbox = rs.BoundingBox(submerged)
    

    xmin = min(p.X for p in sub_bbox)
    xmax = max(p.X for p in sub_bbox)

    ymin = min(p.Y for p in sub_bbox)
    ymax = max(p.Y for p in sub_bbox)

    beam = ymax - ymin
    
    # --- Compute waterplane area ---
    interCurves = rs.IntersectBreps(brep_id, waterplane)[0]
    interSurf = rs.AddPlanarSrf(interCurves)
    rs.DeleteObject(interCurves)

    wpa = rs.SurfaceArea(interSurf)[0]

    centroid_F = rs.SurfaceAreaCentroid(interSurf)[0]
    LCF = centroid_F[0]
    rs.MoveObject(interSurf,[-LCF,0,0])
    wp_moments = rs.SurfaceAreaMoments(interSurf)
    IL = wp_moments[2][0]
    IT = wp_moments[2][1]
    rs.MoveObject(interSurf, [LCF, 0,0])

    centroid_B = rs.SurfaceVolumeCentroid(submerged)[0]

    LCB = centroid_B[0]
    VCB = centroid_B[2]

    wetSrf = rs.SurfaceArea(submerged)[0] - wpa
    cf = rs.SurfaceAreaCentroid(interSurf)[0][0]

    L_submerged = xmax - xmin

    cB = calcBlockCoeff(vol, L_submerged, beam, draft)

    # centroid formatting
    wp_bbox = rs.BoundingBox(interSurf)
    xmin_l = min(p.X for p in wp_bbox)
    xmax_l = max(p.X for p in wp_bbox)

    Lpp = xmax_l - rudder_pos

    mainFramePos = Lpp / 2
    B = ((centroid - mainFramePos) / Lpp) * 100

    # --- Compute sectional area curve ---
    bbox = rs.BoundingBox(brep_id)
    x_min, x_max = bbox[0].X, bbox[6].X - 0.1
    print(x_max)
    print(Lpp)
    n_stations = 250
    xs = np.linspace(x_min, x_max, n_stations)
    sec_areas = []

    for x in xs:
        plane = rs.PlaneFromNormal((x, 0, 0), (1, 0, 0))
        plane_srf = rs.AddPlaneSurface(plane, 1000, 1000)
        rs.MoveObject(plane_srf, (0, -500, -500))
        crvs = rs.IntersectBreps(submerged, plane_srf)
        # print("Station position: " + str(x))
        if crvs:
            # crvs = crvs[0]
            print("Number of intersection curves: " + str(len(crvs)))
            area = 0
            for cr in crvs:
                print(rs.ObjectType(cr))
                # if not cr.IsCurveClosed():
                #     print("Curve not closed..")
                #     continue
                surf = rs.AddPlanarSrf(cr)
                if not surf:
                    rs.DeleteObject(plane_srf)
                    rs.DeleteObject(cr)
                    print("Warning Message #111")
                    continue
                else:
                    if not rs.SurfaceArea(surf):
                        rs.DeleteObject(cr)
                        rs.DeleteObject(surf)
                        rs.DeleteObject(plane_srf)
                        print("Warning Message #222")
                        continue
                    else: 
                        area = area + np.round(rs.SurfaceArea(surf)[0], 3)
                        rs.DeleteObject(cr)
                        rs.DeleteObject(surf)
                        rs.DeleteObject(plane_srf)
                if not area == 0:
                    sec_areas.append((float(x), np.round(float(x) / Lpp, 3), area, area / (beam * draft)))
        else:
            area = 0
            sec_areas.append((float(x), np.round(float(x) / Lpp, 3), area, area / (beam * draft)))

        rs.DeleteObject(plane_srf)


    # print(sec_areas)

    # Ask for CSV file location
    csv_path = rs.SaveFileName("Save sectional area CSV", "CSV files (*.csv)|*.csv||")
    if not csv_path:
        print("No file selected.")
        return

    # Write CSV
    with open(csv_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Station_X", "Station_X_nondim", "Area_absolute", "Area_nondim"])
        for row in sec_areas:
            writer.writerow(row)

    print("Sectional areas exported to CSV:", csv_path)

    split_path = csv_path.split("\\")
    split_path[-1] = "hydrostatics_result.txt"
    print(split_path)
    joined = "\\".join(split_path)
    print(joined)

    BM_T = IT / vol

    # --- Output results ---
    msg = [
        f"T (from keel): {draft:.3f} (model units)",
        f"LOA : {LOA:.3f} (model units)",
        f"LPP : {Lpp:.3f} (model units)",
        f"Displaced Volume: {vol:.6f} (model units³)",
        f"C_B : {cB:.3f} (non dimensional)",
        f"LCB: {B:.3f} | {centroid:.3f} (percent of Lpp, from midships | model units)",
        f"Waterplane Area: {wpa:.6f} (model units²)",
        f"I_T: {IT:.6f} (model units^4)",
        f"KB: {VCB:.3f} (model units)",
        f"BM: {BM_T:.3f} (model units)",
        f"Wetted Area: {wetSrf:.6f} (model units²)"
    ]

    disp = [
        "Results exported to:",
        "   " + csv_path,
        "   " + joined
    ]

    rs.MessageBox("\n".join(disp), 0, "Hydrostatics Summary Exported")

    with open(joined, mode='w', newline='') as hydrofile:
        hydrofile.write("\n".join(msg))
    
    print("Hydrostatics result exported as :", joined)
    
    # Cleanup
    rs.DeleteObject(interSurf)
    rs.DeleteObject(surf)
    rs.DeleteObject(waterplane)
    rs.DeleteObject(watercube)
    rs.DeleteObject(submerged)
    rs.DeleteObject(surf)

def calcBlockCoeff(subVol, l, b, t):
    return subVol / (l * b * t)

if __name__ == "__main__":
    rs.EnableRedraw(False)
    main()
    rs.EnableRedraw(True)
