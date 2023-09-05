# Nikita Akimov
# interplanety@interplanety.org
#
# GitHub
#    https://github.com/Korchy/1d_height_painter

from math import ceil
import bpy
from bpy.props import FloatProperty
from bpy.types import Operator, Panel, Scene
import bmesh

bl_info = {
    "name": "Height Painter",
    "description": "Colors each polygon with first 2 colors of object material by height",
    "author": "Nikita Akimov, Paul Kotelevets",
    "version": (1, 0, 4),
    "blender": (2, 79, 0),
    "location": "View3D > Tool panel > 1D > DrewingsSplit",
    "doc_url": "https://github.com/Korchy/1d_height_painter",
    "tracker_url": "https://github.com/Korchy/1d_height_painter",
    "category": "All"
}


# MAIN CLASS

class HeightPainter:

    @classmethod
    def paint_polygons(cls, context, obj, height, threshold):
        # paint selected polygons with colors by height
        # edit/object mode
        mode = context.active_object.mode
        if context.active_object.mode == 'EDIT':
            bpy.ops.object.mode_set(mode='OBJECT')

        # use bmesh to filter polygons (their vertices) by height
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bm.verts.ensure_lookup_table()
        bm.faces.ensure_lookup_table()

        p0 = []     # polygon indices for first color (odd lines)
        p1 = []     # polygon indices for second color (even lines)
        p2 = []     # polygon indices for third color (horizontally flat polygons)
        p3 = []     # polygon indices for forth color (all other polygons)

        selected_faces = (face for face in bm.faces if face.select)

        for face in selected_faces:
            # get line indices on which face lies
            face_index = cls._face_line_index(
                face=face,
                height=height,
                threshold=threshold
            )
            if face_index[2] is True:
                # horizontally flat polygon
                p2.append(face.index)
            else:
                # by line indexes on which face lies - check in what group it should be
                if face_index[0] == face_index[1]:
                    # all indices are equal
                    if face_index[0] % 2 == 0:
                        # if even - first color group
                        p0.append(face.index)
                    else:
                        # if odd - second color group
                        p1.append(face.index)
                else:
                    # if indices are different - face lies on several lines, third color group
                    p3.append(face.index)
        print(p2)
        # color polygons by getted lists
        for polygon in obj.data.polygons:
            if polygon.index in p0:
                polygon.material_index = 0
            elif polygon.index in p1:
                polygon.material_index = 1
            elif polygon.index in p2:
                polygon.material_index = 2
            elif polygon.index in p3:
                polygon.material_index = 3

        # return mode back
        bpy.ops.object.mode_set(mode=mode)

    @classmethod
    def _face_line_index(cls, face, height: float, threshold: float):
        # get line index (by height) for face
        co_z = [v.co.z for v in face.verts]     # face points z-coordinates
        min_z = min(co_z) + threshold       # with threshold
        max_z = max(co_z) - threshold       # with threshold
        min_z_index = ceil(min_z / height)  # line index for min face point
        max_z_index = ceil(max_z / height)  # line index for max face point
        is_horizontally_flat = True if abs(max(co_z) - min(co_z)) <= threshold else False  # face is horizontally flat
        return min_z_index, max_z_index, is_horizontally_flat


# OPERATORS

class HeightPainter_OT_paint_polygons(Operator):
    bl_idname = 'height_painter.paint_polygons'
    bl_label = 'Paint polygons'
    bl_options = {'REGISTER', 'UNDO'}

    height = FloatProperty(
        default=0.5,
        min=0.0001,
        subtype='UNSIGNED',
        step=10
    )

    threshold = FloatProperty(
        default=0.02,
        min=0.0,
        subtype='UNSIGNED',
        step=1
    )

    def execute(self, context):
        HeightPainter.paint_polygons(
            context=context,
            obj=context.active_object,
            height=self.height,
            threshold=self.threshold
        )
        return {'FINISHED'}


# PANELS

class HeightPainter_PT_panel(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_label = "Height Painter"
    bl_category = '1D'

    def draw(self, context):
        layout = self.layout
        layout.prop(
            data=context.scene,
            property='height_painter_height'
        )
        layout.prop(
            data=context.scene,
            property='height_painter_threshold'
        )
        op = layout.operator(
            operator='height_painter.paint_polygons',
            text='Paint Polygons',
            icon='VPAINT_HLT'
        )
        op.height = context.scene.height_painter_height
        op.threshold = context.scene.height_painter_threshold


# REGISTER

def register():
    Scene.height_painter_height = FloatProperty(
        name='Height',
        default=0.5,
        min=0.0001,
        subtype='UNSIGNED',
        step=10
    )
    Scene.height_painter_threshold = FloatProperty(
        name='Height threshold',
        default=0.02,
        min=0.0,
        subtype='UNSIGNED',
        step=1
    )
    bpy.utils.register_class(HeightPainter_OT_paint_polygons)
    bpy.utils.register_class(HeightPainter_PT_panel)


def unregister():
    bpy.utils.unregister_class(HeightPainter_PT_panel)
    bpy.utils.unregister_class(HeightPainter_OT_paint_polygons)
    del Scene.height_painter_height
    del Scene.height_painter_threshold


if __name__ == "__main__":
    register()
