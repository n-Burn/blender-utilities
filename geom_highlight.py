"""
Mesh Object Geometry Highlighter
geom_highlight.py

Description:
Highlights and/or outlines geometry (vertices, edges, or faces) using geometry 
indexes listed in the GeometryHighlighter class's "invoke" method. Originally 
developed to see what geometry was being affected by mesh related functions.

Notes: 
Must be run in Edit Mode
Launched from space bar menu by typing in: Geometry Highlighter
UP and DOWN arrow keys used to cycle through indexed geometry
Exited with Escape key or right mouse click
"""

import bpy
import blf
import bgl
from bpy_extras import view3d_utils
from bpy_extras.view3d_utils import location_3d_to_region_2d as loc3d_to_reg2d

bl_info = {
    "name": "Geometry Highlighter",
    "author": "nBurn",
    "location": "View3D > Spacebar Menu",
    "version": (0, 0, 0),
    "blender": (2, 77, 0),
    "description": "Highlights listed mesh geometry indexes",
    "wiki_url": "",
    "category": "Mesh"}

print("\nadd-on loaded.")  # debug


class Colr:
    red    = 1.0, 0.0, 0.0, 0.6
    green  = 0.0, 1.0, 0.0, 0.6
    blue   = 0.0, 0.0, 1.0, 0.6
    white  = 1.0, 1.0, 1.0, 1.0
    grey   = 1.0, 1.0, 1.0, 0.4
    black  = 0.0, 0.0, 0.0, 1.0
    yellow = 1.0, 1.0, 0.5, 0.5
    brown  = 0.15, 0.15, 0.15, 0.20


def draw_text(text, size, colr, pos):
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
    def __init__(self, rgn, rv3d):
        self.object_list = {}
        self.face_colr = Colr.yellow
        self.edge_colr = Colr.red
        self.vert_colr = Colr.green
        self.rgn_rv3d = rgn, rv3d
        self.title = ""
        
    def add_obj(self, obj):
        if obj not in self.object_list:
            self.object_list.update( {obj:GeoTracker()} )

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

    def draw(self):
        draw_text(self.title, 18, Colr.white, (70, 50))
        reg, rv3d = self.rgn_rv3d
        for o in self.object_list:
            ob = bpy.context.scene.objects[o]
            obdat = self.object_list[o]

            # draw faces
            for f in obdat.faces:
                visible = True
                v2d = []
                verts = ob.data.polygons[f].vertices
                for v in verts:
                    vlocal = ob.data.vertices[v].co
                    co3d = ob.matrix_world * vlocal
                    co2d = loc3d_to_reg2d(reg, rv3d, co3d)
                    if co2d is None:
                        visible = False
                        break
                    v2d.append(co2d)
                if visible:
                    bgl.glEnable(bgl.GL_BLEND)
                    bgl.glColor4f(*self.face_colr)
                    bgl.glBegin(bgl.GL_POLYGON)
                    for p in v2d:
                        bgl.glVertex2f(*p)
                    bgl.glEnd()

            # draw edges
            for e in obdat.edges:
                visible = True
                v2d = []
                verts = ob.data.edges[e].vertices
                for v in verts:
                    vlocal = ob.data.vertices[v].co
                    co3d = ob.matrix_world * vlocal
                    co2d = loc3d_to_reg2d(reg, rv3d, co3d)
                    if co2d is None:
                        visible = False
                        break
                    v2d.append(co2d)
                if visible:
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


def draw_callback_px(self, context):
    draw_text(str(self.active), 20, Colr.white, (70, 30))
    self.objects[self.active].draw()


class GeometryHighlighter(bpy.types.Operator):
    bl_idname = "object.simp_view_operator"
    bl_label = "Geometry Highlighter"

    def modal(self, context, event):
        context.area.tag_redraw()
        
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            # allow navigation
            return {'PASS_THROUGH'}

        # call debugger
        '''
        if event.type == 'D' and event.value == 'RELEASE':
            #self.debug_flag = True
            __import__('code').interact(local=dict(globals(), **locals()))
        '''

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
            print("add-on running.")  # debug
            args = (self, context)
            self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px,
                    args, 'WINDOW', 'POST_PIXEL')

            self.debug_flag = False
            self.force_quit = False
            self.active = 0
            self.objects = []

            obj_idx = 6
            geom = (
                # ("TITLE", "GEOMETRY_TYPE", GEOMETRY_INDEXES),
                ("ele_dst", "face", 73,),
                ("ele_src", "face", 48,),
                ("function: other_edges_over_edge", None,),
                ("stack_old_src_edges", "edge", 215,88,216,76,),
                ("stack_visit", "edge", 215,76,216,88,),
                ("other_edges_over_cb: function other_edges_over_face", None,),
                ("all_verts_in_dst", "vert", 97,109,98,108,),
                ("ele", "face", 98,),
                (None, None),  # None values to indicate end of geometry tuple
                (None, None),
            )

            for g in range(len(geom)):
                self.objects.append(ObjectTracker(context.region, context.region_data))
                if   geom[g][0] is not None:
                    self.objects[-1].title = geom[g][0]

                if   geom[g][1] == "vert":
                    self.objects[-1].add_verts(obj_idx, geom[g][2:])
                elif geom[g][1] == "edge":
                    self.objects[-1].add_edges(obj_idx, geom[g][2:])
                elif geom[g][1] == "face":
                    self.objects[-1].add_faces(obj_idx, geom[g][2:])
                else:
                    self.objects[-1].add_obj(obj_idx)
                #if   geom[g][1] is None:
                #    self.objects[g].add_obj(obj_idx)

            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}


def register():
    bpy.utils.register_class(GeometryHighlighter)

def unregister():
    bpy.utils.unregister_class(GeometryHighlighter)

if __name__ == "__main__":
    register()
