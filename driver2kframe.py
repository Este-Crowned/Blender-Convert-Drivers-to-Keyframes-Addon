bl_info = {
    "name" : "Convert Drivers 2 Keyframes",
    "author" : "Crowned", 
    "description" : "Convert all driven properties to keyframes",
    "blender" : (3, 0, 0),
    "version" : (1, 0, 0),
    "location" : "N panel",
    "warning" : "",
    "doc_url": "", 
    "tracker_url": "", 
    "category" : "Property" 
}

import bpy
data = bpy.data
import itertools

class ConvertObjectDriversToKeyframesOperator(bpy.types.Operator):
    bl_idname = "object.convert_object_drivers_to_keyframes"
    bl_label = "Convert All"
    
    range_start: bpy.props.IntProperty(name="Frame Start", default=1)
    range_end: bpy.props.IntProperty(name="Frame End", default=250)

    def execute(self, context):

        #first convert object keyframes
        self.convert_object_drivers_to_keyframes(context)

        #get all the nodetrees
        shader_nodetrees = (material.node_tree for material in data.materials if hasattr(material, "node_tree") and (material.node_tree is not None))
        geo_nodetrees = (group for group in data.node_groups if hasattr(group, "nodes"))
        all_nodetrees = itertools.chain(shader_nodetrees, geo_nodetrees)

        #processes the convertion for all nodetrees
        for tree in all_nodetrees:

            # Set the frame range
            frame_start = context.scene.frame_start
            frame_end = context.scene.frame_end

            # Iterate through all nodes in the tree
            for node in tree.nodes:
                if hasattr(node.inputs, 'inputs'):
                    # Geometry Node
                    for input_socket in node.inputs.inputs:
                        # Create a dictionary to store input values for each frame
                        frame_values = {}

                        # Iterate through frames to store input values, only if a change is detected
                        if hasattr(input_socket, "default_value"):
                            context.scene.frame_set(frame_start)
                            startval = input_socket.default_value
                            context.scene.frame_set(frame_end-3)
                            if input_socket.default_value != startval:
                                for frame in range(frame_start, frame_end + 1):
                                    context.scene.frame_set(frame)
                                    value = input_socket.default_value
                                    frame_values[frame] = value

                                # Remove the driver
                                if input_socket.is_linked:
                                    input_socket.driver_remove("default_value")

                                # Insert keyframes based on the stored values
                                if frame_values[frame_start] != frame_values[frame_end - 3]:
                                    for frame, value in frame_values.items():
                                        context.scene.frame_set(frame)
                                        input_socket.default_value = value
                                        input_socket.keyframe_insert(data_path="default_value")
                else:
                    # Shader Node
                    for input_socket in node.inputs:
                        # Create a dictionary to store input values for each frame
                        frame_values = {}

                        # Iterate through frames to store input values, only if a change is detected
                        if hasattr(input_socket, "default_value"):
                            context.scene.frame_set(frame_start)
                            startval = input_socket.default_value
                            context.scene.frame_set(frame_end-3)
                            if input_socket.default_value != startval:
                                for frame in range(frame_start, frame_end + 1):
                                    context.scene.frame_set(frame)
                                    value = input_socket.default_value
                                    frame_values[frame] = value

                                # Remove the driver
                                if input_socket.is_linked:
                                    input_socket.driver_remove("default_value")

                                # Insert keyframes based on the stored values
                                if frame_values[frame_start] != frame_values[frame_end - 3]:
                                    for frame, value in frame_values.items():
                                        context.scene.frame_set(frame)
                                        input_socket.default_value = value
                                        input_socket.keyframe_insert(data_path="default_value")

        # Reset the scene frame to the start
        context.scene.frame_set(frame_start)
        return {'FINISHED'}

    def convert_object_drivers_to_keyframes(self, context):
        # Process all selected objects
        for obj in context.selected_objects:
            self.convert_object_drivers(obj, context)

    def convert_object_drivers(self, obj, context):
        if obj.animation_data and obj.animation_data.drivers:
            for driver in obj.animation_data.drivers:
                self.convert_driver_to_keyframes(driver, context)

    def convert_driver_to_keyframes(self, driver, context):
        data_path = driver.data_path

        if not driver.keyframe_points:
            return

        obj = driver.id_data

        # Ensure that the frame range is within the valid range
        frame_start = max(self.range_start, context.scene.frame_start)
        frame_end = min(self.range_end, context.scene.frame_end)

        for frame in range(frame_start, frame_end + 1):
            bpy.context.scene.frame_set(frame)
            value = driver.evaluate(frame)
            # Insert keyframes for object properties
            obj[data_path] = value
            obj.keyframe_insert(data_path)

class DriversToKeyframesPanel(bpy.types.Panel):
    bl_label = "Drivers to Keyframes"
    bl_idname = "PT_DriversToKeyframesPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'

    def draw(self, context):
        layout = self.layout
        layout.label(text="Convert drivers to keyframes")
        layout.prop(context.scene, "frame_start")
        layout.prop(context.scene, "frame_end")
        layout.operator(ConvertObjectDriversToKeyframesOperator.bl_idname)

def register():
    bpy.utils.register_class(ConvertObjectDriversToKeyframesOperator)
    bpy.utils.register_class(DriversToKeyframesPanel)

def unregister():
    bpy.utils.unregister_class(ConvertObjectDriversToKeyframesOperator)
    bpy.utils.unregister_class(DriversToKeyframesPanel)

if __name__ == "__main__":
    register()
