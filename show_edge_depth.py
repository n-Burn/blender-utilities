"""
# Edge Depth Test
# show_edge_depth.py

Description:
Shows "depth" for each vertex in a mesh. The "depth" is calculated in terms of 
the minimum number of edges needed to reach each vertex starting from the 
selected geometry elements (verts, edges, or faces). Edge depths are shown 
for up to 4 selected elements starting with the most recently selected element 
and counting backwards.

Note: must be run in Edit Mode
"""

import bpy
import bmesh
import blf
import bgl
from mathutils import Vector
from bpy_extras import view3d_utils
from bpy_extras.view3d_utils import location_3d_to_region_2d as loc3d_to_reg2d

print("\nadd-on loaded.")


class Colr:
    red    = 1.0,  0.0,  0.0,  1.0
    green  = 0.0,  1.0,  0.0,  1.0
    blue   = 0.0,  0.0,  1.0,  1.0
    lblue  = 0.1,  1.0,  1.0,  1.0
    white  = 1.0,  1.0,  1.0,  1.0
    grey   = 1.0,  1.0,  1.0,  1.0
    black  = 0.0,  0.0,  0.0,  1.0
    yellow = 1.0,  1.0,  0.5,  1.0
    pink   = 1.0,  0.6,  0.6,  1.0
    brown  = 0.15, 0.15, 0.15, 1.0


def draw_text(text, size, colr, pos):
    # draw text
    dpi = 72
    font_id = 0
    blf.size(font_id, size, dpi)
    bgl.glColor4f(*colr)
    blf.position(font_id, pos[0], pos[1], 0)
    blf.draw(font_id, text)


class DepthData:
    def __init__( self, dep=None, verts=(), pos=(0,0) ):
        self.depth = dep
        self.faces = []
        self.edges = []
        self.verts = verts
        self.pos = pos


class DepthTracker:
    def __init__(self, rgn_rv3d, tcolr=Colr.white, tsiz=12, tloc=None):
        self.rgn_rv3d = rgn_rv3d
        self.depth_list = []
        self.txt_colr = tcolr
        self.txt_size = tsiz
        self.txt_loc = tloc  # "TL"
        
    def chg_sett(self, colr, sz, loc):
        self.txt_colr = colr
        self.txt_size = sz
        self.txt_loc = loc

    def add_depths(self, depths):
        def_pos = 4, 6
        dpi = 72
        font_id = 0
        blf.size(font_id, self.txt_size, dpi)

        for d in range(len(depths)):
            d_str = str(d)
            if   self.txt_loc == "TL":
                tdims = blf.dimensions(font_id, d_str)
                txt_pos = -def_pos[0] - tdims[0], def_pos[1]
            elif self.txt_loc == "TR":
                #tdims = blf.dimensions(font_id, d_str)
                txt_pos = def_pos
            elif self.txt_loc == "BR":
                tdims = blf.dimensions(font_id, d_str)
                txt_pos = def_pos[0], -def_pos[1] - tdims[1]
            elif self.txt_loc == "BL":
                tdims = blf.dimensions(font_id, d_str)
                txt_pos = -def_pos[0] - tdims[0], -def_pos[1] - tdims[1]
        
            self.depth_list.append(DepthData(d_str, depths[d], txt_pos))

    def draw_depths(self):
        reg, rv3d = self.rgn_rv3d
        tcolr = self.txt_colr
        tsize = self.txt_size
        #toff = self.txt_pos  # text offset
        dpi = 72
        font_id = 0
        blf.size(font_id, tsize, dpi)
        bgl.glColor4f(*tcolr)
        ob = bpy.context.edit_object
        for d in self.depth_list:
            for v in d.verts:
                vlocal = ob.data.vertices[v].co
                co3d = ob.matrix_world * vlocal
                co2d = loc3d_to_reg2d(reg, rv3d, co3d)
                if co2d is not None:
                    pos = co2d[0]+d.pos[0], co2d[1]+d.pos[1]
                    blf.position(font_id, pos[0], pos[1], 0)
                    blf.draw(font_id, d.depth)


# returns all edges in faces that edge arg 'e' is part of
# and shares verts with
def other_edges_over_face(e):
    # Can yield same edge multiple times, its fine.
    for l in e.link_loops:
        yield l.link_loop_next.edge
        yield l.link_loop_prev.edge


# returns all edges that edge arg 'e' shares verts with
def other_edges_over_edge(e):
    # Can yield same edge multiple times, its fine.
    for v in e.verts:
        for e_other in v.link_edges:
            if e_other is not e:
                if not e.is_wire:
                    yield e_other


# returns verts that form provided element arg
def verts_from_elem(ele):
    ele_type = type(ele)
    if ele_type is bmesh.types.BMFace:
        return [l.vert for l in ele.loops]
    elif ele_type is bmesh.types.BMEdge:
        return [v for v in ele.verts]
    elif ele_type is bmesh.types.BMVert:
        return [ele]
    else:
        raise TypeError("wrong type")


# returns edges that form provided element arg (or are connected to it if vert)
def edges_from_elem(ele):
    ele_type = type(ele)
    if ele_type is bmesh.types.BMFace:
        return [l.edge for l in ele.loops]
    elif ele_type is bmesh.types.BMEdge:
        return [ele]
    elif ele_type is bmesh.types.BMVert:
        return [e for e in ele.link_edges]
    else:
        raise TypeError("wrong type")


def get_depths(ele_src, other_edges_over_cb):
    stack_old_src_edges = edges_from_elem(ele_src)
    test_depths = []
    stack_new_edges = []
    vert_stack_visit = set()
    edge_stack_visit = set(stack_old_src_edges)
    curr_depth = []
    while stack_old_src_edges:
        for edg_ele in stack_old_src_edges:
            for v in verts_from_elem(edg_ele):
                len_pre_add = len(vert_stack_visit)
                vert_stack_visit.add(v.index)
                if len_pre_add != len(vert_stack_visit):
                    curr_depth.append(v.index)
            for ele_other in other_edges_over_cb(edg_ele):
                e_stack_visit_len = len(edge_stack_visit)
                edge_stack_visit.add(ele_other)
                if e_stack_visit_len != len(edge_stack_visit):
                    stack_new_edges.append(ele_other)
        test_depths.append(curr_depth.copy())
        #test_depths.append(curr_depth)
        curr_depth[:] = []
        stack_new_edges, stack_old_src_edges = stack_old_src_edges, stack_new_edges
        stack_new_edges[:] = []

    return test_depths


def draw_pts(self):
    mat_w = bpy.context.edit_object.matrix_world
    sz = 10
    reg, rv3d = self.rgn_rv3d
    bgl.glEnable(bgl.GL_BLEND)
    bgl.glPointSize(sz)
    bgl.glBegin(bgl.GL_POINTS)
    for pd in self.pts:
        vlocal, colr = pd
        bgl.glColor4f(*colr)
        co3d = mat_w * vlocal
        co2d = loc3d_to_reg2d(reg, rv3d, co3d)
        if co2d is not None:
            bgl.glVertex2f(*co2d)
    bgl.glEnd()


def draw_callback_px(self, context):
    draw_pts(self)
    for ob in self.objects:
        ob.draw_depths()


class ShowEdgeDepth(bpy.types.Operator):
    bl_idname = "mesh.show_edge_depth"
    bl_label = "Show Edge Depth"

    def modal(self, context, event):
        context.area.tag_redraw()
        
        # allow navigation
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            return {'PASS_THROUGH'}

        # open debug console
        '''
        if event.type == 'D' and event.value == 'RELEASE':
            #self.debug_flag = True
            __import__('code').interact(local=dict(globals(), **locals()))
        '''

        if event.type in {'ESC', 'RIGHTMOUSE'}:
            print("add-on stopped.\n")
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'CANCELLED'}

        elif self.force_quit is True:
            print("add-on stopped.\n")
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':
            if context.mode not in ('EDIT', 'EDIT_MESH'):
                self.report({'WARNING'}, "Must be in edit mode.")
                return {'CANCELLED'}
            
            bm = bmesh.from_edit_mesh(bpy.context.edit_object.data)
            if len(bm.select_history) < 1:
                self.report({'WARNING'}, "Must select part of mesh.")
                return {'CANCELLED'}

            args = (self, context)
            self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px,
                    args, 'WINDOW', 'POST_PIXEL')

            print("add-on running.")  # debug
            self.debug_flag = False
            self.force_quit = False
            self.pts = []
            self.objects = []

            self.rgn_rv3d = context.region, context.region_data
            colrs = Colr.pink, Colr.green, Colr.white, Colr.lblue
            tlocs = "BR", "BL", "TR", "TL"
            tsize = 16
            # get obj scene index (debug)
            #obj = bpy.context.scene.objects.find(bpy.context.edit_object.name)
            #print("obj", obj)
            for r in range(len(bm.select_history)):
                if r == 4:
                    break
                colr = colrs[r]
                tloc = tlocs[r]
                self.objects.append(DepthTracker(self.rgn_rv3d, colr, tsize, tloc))
                ele_src = bm.select_history[-r - 1]  # reversed order
                #v_depths = get_depths(ele_src, other_edges_over_face)
                v_depths = get_depths(ele_src, other_edges_over_edge)
                self.objects[-1].add_depths(v_depths)
                ele_type = type(ele_src)
                if ele_type is bmesh.types.BMFace:
                    tot, vcnt = Vector(), len(ele_src.verts)
                    for v in ele_src.verts:
                        tot += v.co
                    self.pts.append([(tot / vcnt), colr])
                elif ele_type is bmesh.types.BMEdge:
                    tot, vcnt = Vector(), len(ele_src.verts)
                    for v in ele_src.verts:
                        tot += v.co
                    self.pts.append([(tot / vcnt), colr])
                elif ele_type is bmesh.types.BMVert:
                    self.pts.append([ele_src.co, colr])

            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}


def register():
    bpy.utils.register_class(ShowEdgeDepth)

def unregister():
    bpy.utils.unregister_class(ShowEdgeDepth)

if __name__ == "__main__":
    register()
