# Depth Test
# depth_test.py

import bpy
import bmesh
import blf
import bgl
from mathutils import geometry, Euler, Quaternion, Vector
from bpy_extras import view3d_utils
from bpy_extras.view3d_utils import location_3d_to_region_2d as loc3d_to_reg2d
from bpy_extras.view3d_utils import region_2d_to_vector_3d as reg2d_to_vec3d
from bpy_extras.view3d_utils import region_2d_to_location_3d as reg2d_to_loc3d
from bpy_extras.view3d_utils import region_2d_to_origin_3d as reg2d_to_org3d

print("\nadd-on loaded.")

'''
class Colr:
    red    = 1.0,  0.0,  0.0,  0.6
    green  = 0.0,  1.0,  0.0,  0.6
    blue   = 0.0,  0.0,  1.0,  0.6
    white  = 1.0,  1.0,  1.0,  1.0
    grey   = 1.0,  1.0,  1.0,  0.4
    black  = 0.0,  0.0,  0.0,  1.0
    yellow = 1.0,  1.0,  0.5,  0.5
    brown  = 0.15, 0.15, 0.15, 0.20
'''
class Colr:
    red    = 1.0,  0.0,  0.0,  1.0
    green  = 0.0,  1.0,  0.0,  1.0
    blue   = 0.0,  0.0,  1.0,  1.0
    lblue  = 0.1,  1.0,  1.0,  1.0
    white  = 1.0,  1.0,  1.0,  1.0
    grey   = 1.0,  1.0,  1.0,  1.0
    black  = 0.0,  0.0,  0.0,  1.0
    yellow = 1.0,  1.0,  0.5,  1.0
    #yellow = 1.0,  0.95, 0.35, 1.0
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


class GeoTracker:
    def __init__(self):
        self.faces = []
        self.edges = []
        self.verts = []


class ObjectTracker:
    def __init__(self, rgn_rv3d):
        self.rgn_rv3d = rgn_rv3d
        self.object_list = {}
        self.face_colr = Colr.yellow
        self.edge_colr = Colr.red
        self.vert_colr = Colr.green
        self.txt_colr = Colr.white
        self.txt_size = 16
        self.txt_pos = 0, 0
        self.title = ""
        
    def chg_txt_sett(self, colr, size, pos, test_str):
        self.txt_colr = colr
        self.txt_size = size
        def_pos = 4, 6
        dpi = 72
        font_id = 0
        #test_str = "9"
        blf.size(font_id, self.txt_size, dpi)
        if   pos == "TL":
            tdims = blf.dimensions(font_id, test_str)
            self.txt_pos = -def_pos[0] - tdims[0], def_pos[1]
        elif pos == "TR":
            #tdims = blf.dimensions(font_id, test_str)
            self.txt_pos = def_pos
        elif pos == "BR":
            tdims = blf.dimensions(font_id, test_str)
            self.txt_pos = def_pos[0], -def_pos[1] - tdims[1]
        elif pos == "BL":
            tdims = blf.dimensions(font_id, test_str)
            self.txt_pos = -def_pos[0] - tdims[0], -def_pos[1] - tdims[1]
        #print(colr, size, pos, ' :', self.txt_colr, self.txt_size, self.txt_pos)
        
    def add_obj(self, obj):
        if obj not in self.object_list:
            self.object_list.update( {obj:GeoTracker()} )

    def add_vert(self, obj, vert):
        self.add_obj(obj)
        item = self.object_list[obj]
        if vert not in item.verts:
            item.verts.append(vert)

    def add_edge(self, obj, edge):
        self.add_obj(obj)
        item = self.object_list[obj]
        if edge not in item.edges:
            item.edges.append(edge)

    def add_face(self, obj, face):
        self.add_obj(obj)
        item = self.object_list[obj]
        if face not in item.faces:
            item.faces.append(face)

    def add_verts(self, obj, verts):
        self.add_obj(obj)
        item = self.object_list[obj]
        for v in verts:
            if v not in item.verts:
                item.verts.append(v)

    def add_edges(self, obj, edges):
        self.add_obj(obj)
        item = self.object_list[obj]
        for e in edges:
            if e not in item.edges:
                item.edges.append(e)

    def add_faces(self, obj, faces):
        self.add_obj(obj)
        item = self.object_list[obj]
        for f in faces:
            if f not in item.faces:
                item.faces.append(f)

    def draw_verts(self):
        return

    def draw_edges(self):
        return

    def draw_faces(self, obj, face):
        self.add_obj(obj)
        item = self.object_list[obj]
        if face not in item.faces:
            item.faces.append(face)
        return

    def draw(self):
        #draw_text(text, size, colr, pos
        draw_text(self.title, 18, Colr.white, (70, 50))
        reg, rv3d = self.rgn_rv3d
        for o in self.object_list:
            ob = bpy.context.scene.objects[o]
            obdat = self.object_list[o]

            # draw faces
            for f in obdat.faces:
                inval = False
                v2d = []
                verts = ob.data.polygons[f].vertices
                for v in verts:
                    vlocal = ob.data.vertices[v].co
                    co3d = ob.matrix_world * vlocal
                    co2d = loc3d_to_reg2d(reg, rv3d, co3d)
                    if co2d is None:
                        inval = True
                        break
                    v2d.append(co2d)
                if inval is False:
                    bgl.glEnable(bgl.GL_BLEND)
                    bgl.glColor4f(*self.face_colr)
                    bgl.glBegin(bgl.GL_POLYGON)
                    for p in v2d:
                        bgl.glVertex2f(*p)
                    bgl.glEnd()

            # draw edges
            for e in obdat.edges:
                inval = False
                v2d = []
                verts = ob.data.edges[e].vertices
                for v in verts:
                    vlocal = ob.data.vertices[v].co
                    co3d = ob.matrix_world * vlocal
                    co2d = loc3d_to_reg2d(reg, rv3d, co3d)
                    if co2d is None:
                        inval = True
                        break
                    v2d.append(co2d)
                if inval is False:
                    bgl.glEnable(bgl.GL_BLEND)
                    bgl.glLineWidth(3)
                    bgl.glColor4f(*self.edge_colr)
                    bgl.glBegin(bgl.GL_LINE_STRIP)
                    for p in v2d:
                        bgl.glVertex2f(*p)
                    bgl.glEnd()

            # draw verts
            bgl.glEnable(bgl.GL_BLEND)
            bgl.glPointSize(10)
            bgl.glColor4f(*self.vert_colr)
            bgl.glBegin(bgl.GL_POINTS)
            for v in obdat.verts:
                vlocal = ob.data.vertices[v].co
                co3d = ob.matrix_world * vlocal
                co2d = loc3d_to_reg2d(reg, rv3d, co3d)
                if co2d is not None:
                    bgl.glVertex2f(*co2d)
            bgl.glEnd()

    def draw_1st_pt(self):
        reg, rv3d = self.rgn_rv3d
        bgl.glEnable(bgl.GL_BLEND)
        bgl.glPointSize(sz)
        bgl.glColor4f(*colr)
        bgl.glBegin(bgl.GL_POINTS)
        for o in self.object_list:
            ob = bpy.context.scene.objects[o]
            obdat = self.object_list[o]
            v = obdat.verts[0]
            vlocal = ob.data.vertices[v].co
            co3d = ob.matrix_world * vlocal
            co2d = loc3d_to_reg2d(reg, rv3d, co3d)
            if co2d is not None:
                bgl.glVertex2f(*co2d)
        bgl.glEnd()

    def draw_depths(self):
        reg, rv3d = self.rgn_rv3d
        tcolr = self.txt_colr
        tsize = self.txt_size
        toff = self.txt_pos  # text offset
        dpi = 72
        font_id = 0
        blf.size(font_id, tsize, dpi)
        bgl.glColor4f(*tcolr)
        for o in self.object_list:
            ob = bpy.context.scene.objects[o]
            obdat = self.object_list[o]
            for v in obdat.verts:
                vlocal = ob.data.vertices[v].co
                co3d = ob.matrix_world * vlocal
                co2d = loc3d_to_reg2d(reg, rv3d, co3d)
                if co2d is not None:
                    blf.position(font_id, co2d[0]+toff[0], co2d[1]+toff[1], 0)
                    blf.draw(font_id, self.title)


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
    #draw_text(str(self.active), 20, Colr.white, (70, 30))
    #self.objects[self.active].draw()
    draw_pts(self)
    for ob in self.objects:
        ob.draw_depths()


class SimpleViewOperator(bpy.types.Operator):
    bl_idname = "object.simp_view_operator"
    bl_label = "Simple View Operator"

    def modal(self, context, event):
        context.area.tag_redraw()
        
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            # allow navigation
            return {'PASS_THROUGH'}

        if event.type == 'D' and event.value == 'RELEASE':
            # call debugger
            #self.debug_flag = True
            __import__('code').interact(local=dict(globals(), **locals()))

        if event.type in {'ESC', 'RIGHTMOUSE'}:
            print("add-on stopped.\n")
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'CANCELLED'}

        elif event.type == 'UP_ARROW' and event.value == 'RELEASE':
            self.active = (self.active + 1) % len(self.objects)

        elif event.type == 'DOWN_ARROW' and event.value == 'RELEASE':
            self.active = (self.active - 1) % len(self.objects)

        elif self.force_quit is True:
            print("add-on stopped.\n")
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':
            args = (self, context)
            self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px,
                    args, 'WINDOW', 'POST_PIXEL')

            if context.mode not in ('EDIT', 'EDIT_MESH'):
                self.report({'WARNING'}, "Must be in edit mode.")
                return {'CANCELLED'}
            print("add-on running.")  # debug
            
            bm = bmesh.from_edit_mesh(bpy.context.edit_object.data)
            if len(bm.select_history) < 1:
                self.report({'WARNING'}, "Must select part of mesh.")
                return {'CANCELLED'}

            self.debug_flag = False
            self.force_quit = False
            self.pts = []
            self.active = 0
            self.objects = []

            self.rgn_rv3d = context.region, context.region_data
            #colrs = Colr.white, Colr.green, Colr.red, Colr.blue
            colrs = Colr.white, Colr.green, Colr.pink, Colr.lblue
            tlocs = "BL", "BR", "TR", "TL"
            tsize = 16
            # get obj scene index
            obj = bpy.context.scene.objects.find(bpy.context.edit_object.name)
            print("obj", obj)
            for s in range(len(bm.select_history)):
                if s == 4:
                    break
                ele_src = bm.select_history[s]  # reversed order
                #v_depths = get_depths(ele_src, other_edges_over_face)
                v_depths = get_depths(ele_src, other_edges_over_edge)
                geom = [[str(i), "vert"] + v_depths[i] for i in range(len(v_depths))]
                #for gd in geom: print(gd)
                colr = colrs[s]
                tloc = tlocs[s]
                self.pts.append([ele_src.co, colr])
                for g in range(len(geom)):
                    self.objects.append(ObjectTracker(self.rgn_rv3d))
                    if   geom[g][0] is not None:
                        self.objects[-1].title = geom[g][0]
                        self.objects[-1].chg_txt_sett(colr, tsize, tloc, str(g))
                    else:
                        self.objects[-1].chg_txt_sett(colr, tsize, tloc, str('9'))
                    
                    if   geom[g][1] == "vert":
                        self.objects[-1].add_verts(obj, geom[g][2:])
                    elif geom[g][1] == "edge":
                        self.objects[-1].add_edges(obj, geom[g][2:])
                    elif geom[g][1] == "face":
                        self.objects[-1].add_faces(obj, geom[g][2:])
                    else:
                        self.objects[-1].add_obj(obj)

            #self.objects[6].object_list[0].verts
            #self.objects[1].txt_pos

            ''' 
            cnt = 0
            for ob in self.objects:
                #obls = ob.object_list[obj]
                #print('%2d' % cnt, ob.txt_colr, ob.txt_size, ob.txt_pos, obls.verts)
                print('%2d' % cnt, ob.txt_colr, ob.txt_size, ob.txt_pos)
                cnt += 1
            '''

            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}


def register():
    bpy.utils.register_class(SimpleViewOperator)

def unregister():
    bpy.utils.unregister_class(SimpleViewOperator)

if __name__ == "__main__":
    register()
