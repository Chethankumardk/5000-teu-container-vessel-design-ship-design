#! python 3
# r: numpy
# requirements: numpy


import rhinoscriptsyntax as rs
import Rhino
import scriptcontext as sc
import System.Drawing as sd

# Debug Modifier for moving the first station position towards the front perpendicular.
debug_modifier = 0.01

# Sometimes the script fails to cut the hull geometry in half for processing the linesplan using the conventions (front right side, aft left side of the lines plan station view). This modifier allows the user to disable half mode and generate the linesplan for both sides. ATTENTION! To correctly follow the conventions, postprocessing is then needed in a software of your choice.
halfMode = True

def generate_linesplan_conventional():
    hull = rs.GetObject("Select closed polysurface (the hull)", rs.filter.polysurface)
    if not hull or not rs.IsObjectSolid(hull):
        rs.MessageBox("Selected object is not a closed polysurface. Aborting.")
        return
    # mesh_geom = rs.coercemesh(mesh_id)
    
    # --- Bounding box ---
    bbox = rs.BoundingBox(hull)
    ymin = bbox[0][1]
    ymax = bbox[3][1]
    zmin = bbox[0][2]
    zmax = bbox[4][2]
    xmin = bbox[0][0]
    xmax = bbox[1][0]

    loa = xmax - xmin
    
    # --- Number of slices ---
    num_stations = rs.GetInteger("Number of stations", 10, 2)
    if not num_stations:
        return
    num_buttocks = rs.GetInteger("Number of buttocks", 5, 2)
    if not num_buttocks:
        return
    num_waterlines = rs.GetInteger("Number of waterlines", 8, 2)
    if not num_waterlines:
        return
    
    # --- Create layers with correct colors ---
    def create_layer(name, color):
        if not rs.IsLayer(name):
            rs.AddLayer(name, color)
        return name
    
    layer_stations = create_layer("Stations", sd.Color.Blue)
    layer_buttocks = create_layer("Buttocks", sd.Color.Red)
    layer_waterlines = create_layer("Waterlines", sd.Color.Green)
    
    # --- Helper: project and assign to layer ---
    def project_and_assign(crv_id, surf_id, direction, layer):
        print(crv_id)
        print(surf_id)
        proj = rs.ProjectCurveToSurface(crv_id, surf_id, direction)
        rs.DeleteObject(crv_id)
        if proj:
            for pid in proj:
                rs.ObjectLayer(pid, layer)
        return proj

    # cutting hull in half
    plane = rs.WorldZXPlane()
    cutPlane = rs.AddPlaneSurface(plane, 1000, 1000)
    rs.MoveObject(cutPlane, (-500, 0, -500))
    extrudeCrv = rs.AddLine((0, 0, 0), (0, 2*ymin, 0))
    cutHelper = rs.ExtrudeSurface(cutPlane, extrudeCrv)
    rs.DeleteObject(extrudeCrv)
    rs.DeleteObject(cutPlane)

    if halfMode:
        hull_half = rs.BooleanDifference(hull, cutHelper, False)
    else:
        hull_half = hull
    rs.DeleteObject(cutHelper)

    print(hull_half)

    # ==========================================================
    # 1. STATIONS  (frames, side view) — project from starboard (+Y)
    # ==========================================================
    x_slices = [xmin + i*(xmax - xmin)/num_stations for i in range(num_stations+1)]
    x_slices = x_slices[::-1]  # aft → left, forward → right in profile view
    x_slices[0] = x_slices[0] - (debug_modifier * x_slices[0])
    print(x_slices)
    
    for x in x_slices:
        print("X = " + str(x))
        # vertical line in Z, located at Y=0 (centerline)
        start = Rhino.Geometry.Point3d(x, ymin - 3, zmin)
        end   = Rhino.Geometry.Point3d(x, ymin - 3, zmax)
        crv_id = rs.AddLine(start, end)
        # project from starboard to port
        projection = project_and_assign(crv_id, hull_half, (0, 1, 0), layer_stations)
        if x <= (loa / 2):
            rs.MirrorObject(projection, (0, 0, 0), (1, 0, 0))

    # ==========================================================
    # 2. BUTTOCKS (longitudinal verticals, body plan)
    # ==========================================================
    # Port half on left, starboard half on right → project from aft to bow (+X)
    y_slices = [0 + i*(ymax - 0)/num_buttocks for i in range(num_buttocks+1)]
    for y in y_slices:
        print("Y = " + str(y))
        start = Rhino.Geometry.Point3d(0, y, zmin)
        end   = Rhino.Geometry.Point3d(0, y, zmax)
        crv_id = rs.AddLine(start, end)
        # Project from aft (–X direction) toward forward (+X)
        projection = project_and_assign(crv_id, hull_half, Rhino.Geometry.Vector3d.XAxis, layer_buttocks)
        rs.MirrorObject(projection, (0, 0, 0), (1, 0, 0))

    # ==========================================================
    # 3. WATERLINES (horizontal planes, top view)
    # ==========================================================
    z_slices = [zmin + i*(zmax - zmin)/num_waterlines for i in range(num_waterlines+1)]
    for z in z_slices:
        print("Z = " + str(z))
        start = Rhino.Geometry.Point3d(xmin, 0, z)
        end   = Rhino.Geometry.Point3d(xmax, 0, z)
        crv_id = rs.AddLine(start, end)
        # Project downward (–Z) to get top view
        project_and_assign(crv_id, hull_half, -Rhino.Geometry.Vector3d.YAxis, layer_waterlines)

    rs.DeleteObject(hull)
    

generate_linesplan_conventional()