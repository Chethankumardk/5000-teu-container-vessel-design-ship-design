#! python 3
# r: numpy
# requirements: numpy

import rhinoscriptsyntax as rs
import numpy as np
import csv
import os

# draughtStep = 0.2
maxDraughtStep = 3
minDraughtStep = 0.001

def calcSubmergedVol(hull, draught):
    geom = rs.CopyObject(hull)
    plane = rs.WorldXYPlane()
    waterplane = rs.AddPlaneSurface(plane, 1000, 1000)
    bbox = rs.BoundingBox(geom)
    z_min = min(p.Z for p in bbox)
    rs.MoveObject(waterplane, (0, 0, z_min + 0.01))
    rs.MoveObject(waterplane, (-500, -500, draught))
    extrudeCrv = rs.AddLine((0, 0, 0), (0, 0, 300))
    watercube = rs.ExtrudeSurface(waterplane, extrudeCrv)

    rs.DeleteObject(waterplane)
    rs.DeleteObject(extrudeCrv)

    # Keep only the submerged part (below waterline)
    submerged = rs.BooleanDifference([geom], [watercube], False)
    if not submerged:
        rs.DeleteObject(watercube)
        rs.DeleteObject(geom)
        return 0, 0
    vol = rs.SurfaceVolume(submerged)[0]
    centroid = rs.SurfaceVolumeCentroid(submerged)[0][1]
    rs.DeleteObject(watercube)
    rs.DeleteObject(submerged)
    rs.DeleteObject(geom)
    return vol, centroid

def iterateDraught(displ, hull):
    dpl = 0
    currDraught = 0
    currKN = 0
    localDraughtStep = 0.001
    while dpl < displ:
        currDraught = currDraught + localDraughtStep #+ draughtStep
        displacement, KN = calcSubmergedVol(hull, currDraught)
        if (currDraught > 0) and (displacement == 0):
            print("Retrying...")
            currDraught = currDraught + minDraughtStep
        else:
            dpl = displacement
            localDraughtStep = ((displ - dpl) / displ) * maxDraughtStep
            if localDraughtStep < minDraughtStep:
                localDraughtStep = minDraughtStep
            print("New draught step: " + str(localDraughtStep))
            currKN = KN
        print(dpl)
    return np.abs(currKN)

def main():
    # Let user pick the closed polysurface (the hull)
    brep_id = rs.GetObject("Select closed polysurface (the hull)", rs.filter.polysurface)
    if not brep_id or not rs.IsObjectSolid(brep_id):
        rs.MessageBox("Selected object is not a closed polysurface. Aborting.")
        return

    target_displ = rs.GetReal("Enter displacement (volume)", 1000.0, 0.0)
    if target_displ is None: return

    maxInc = rs.GetReal("Enter maximum inclination (deg)", 4, 0.0)
    if maxInc is None: return


    rs.EnableRedraw(False)
    angles = np.arange(0, maxInc, 1)
    kn_array = []
    for angle in angles:
        print(angle)
        rotated_hull = rs.RotateObject(brep_id, (0, 0, 0), angle, (1, 0, 0), copy=True)
        kn = iterateDraught(target_displ, rotated_hull)
        rs.DeleteObject(rotated_hull)
        print("KN = " + str(kn))
        kn_array.append((angle, kn))
    rs.EnableRedraw(True)

        # Ask for CSV file location
    csv_path = rs.SaveFileName("Save KN CSV", "CSV files (*.csv)|*.csv||")
    if not csv_path:
        print("No file selected.")
        return

    # Write CSV
    with open(csv_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["angle", "kn"])
        for row in kn_array:
            writer.writerow(row)
    

if __name__ == "__main__":
    main()
    