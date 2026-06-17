"""
Simple Terrain Generator addon for Blender.

This addon generates procedural terrain with hills using noise and
fractal algorithms.
"""

import math
import random
import bpy
from bpy.utils import register_class, unregister_class
from bpy.props import IntProperty, FloatProperty, BoolProperty

# Basic info of this addon
bl_info = {
    "name": "Simple Terrain Generator",
    "author": "Zdenek Galuska",
    "version": (1, 3),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > Make Terrain",
    "description": "Generate procedural terrain with hills",
    "category": "Add Mesh",
}


def register_properties():
    """Define and register all terrain properties."""
    bpy.types.Scene.terrain_subdivisions = IntProperty(
        name="Subdivisions",
        description="Number of grid divisions (higher = more detail)",
        default=150,
        min=10,
        max=500,
        step=1
    )

    bpy.types.Scene.terrain_size = FloatProperty(
        name="Size",
        description="Size of the terrain",
        default=10,
        min=1.0,
        max=500.0,
        step=1.0
    )

    bpy.types.Scene.terrain_seed = IntProperty(
        name="Seed",
        description="Change for different terrain",
        default=0,
        min=0,
        max=10000,
    )

    bpy.types.Scene.terrain_base_height = FloatProperty(
        name="Base Height",
        description="Height of the flat base terrain",
        default=0.0,
        min=-5.0,
        max=5.0,
        step=0.1
    )

    # Noise Settings
    bpy.types.Scene.terrain_noise_strength = FloatProperty(
        name="Noise Strength",
        description="Overall terrain roughness/detail",
        default=1.0,
        min=0.0,
        max=5.0,
        step=0.1
    )

    bpy.types.Scene.terrain_octaves = IntProperty(
        name="Noise Detail",
        description="Level of detail in terrain noise",
        default=6,
        min=1,
        max=10,
    )

    bpy.types.Scene.terrain_frequency = FloatProperty(
        name="Noise Frequency",
        description="How zoomed in/out the noise is",
        default=1.1,
        min=0.01,
        max=10.0,
        step=0.1
    )

    bpy.types.Scene.terrain_persistence = FloatProperty(
        name="Noise Persistence",
        description="How much detail layers blend together",
        default=0.5,
        min=0.01,
        max=1.0,
        step=0.01
    )

    # Hill Settings
    bpy.types.Scene.terrain_num_hills = IntProperty(
        name="Number of Hills",
        description="How many hills to generate",
        default=6,
        min=0,
        max=50,
    )

    bpy.types.Scene.terrain_hill_height_min = FloatProperty(
        name="Hill Height Min",
        description="Minimum height of hills",
        default=0.2,
        min=0.1,
        max=10.0,
        step=0.1
    )

    bpy.types.Scene.terrain_hill_height_max = FloatProperty(
        name="Hill Height Max",
        description="Maximum height of hills",
        default=0.7,
        min=0.1,
        max=10.0,
        step=0.1
    )

    bpy.types.Scene.terrain_hill_radius_min = FloatProperty(
        name="Hill Radius Min",
        description="Minimum radius of hills",
        default=0.35,
        min=0.1,
        max=10.0,
        step=0.1
    )

    bpy.types.Scene.terrain_hill_radius_max = FloatProperty(
        name="Hill Radius Max",
        description="Maximum radius of hills",
        default=1.0,
        min=0.1,
        max=10.0,
        step=0.1
    )

    bpy.types.Scene.terrain_hill_smoothness = FloatProperty(
        name="Hill Smoothness",
        description="How smooth the hills blend into terrain (higher = smoother)",
        default=3,
        min=1.0,
        max=5.0,
        step=0.1
    )

    bpy.types.Scene.terrain_smooth_shading = BoolProperty(
        name="Smooth Shading",
        description="Enable smooth shading on terrain",
        default=True
    )


def unregister_properties():
    """Unregister all terrain properties from scene."""
    del bpy.types.Scene.terrain_subdivisions
    del bpy.types.Scene.terrain_size
    del bpy.types.Scene.terrain_seed
    del bpy.types.Scene.terrain_base_height
    del bpy.types.Scene.terrain_noise_strength
    del bpy.types.Scene.terrain_octaves
    del bpy.types.Scene.terrain_frequency
    del bpy.types.Scene.terrain_persistence
    del bpy.types.Scene.terrain_num_hills
    del bpy.types.Scene.terrain_hill_height_min
    del bpy.types.Scene.terrain_hill_height_max
    del bpy.types.Scene.terrain_hill_radius_min
    del bpy.types.Scene.terrain_hill_radius_max
    del bpy.types.Scene.terrain_hill_smoothness
    del bpy.types.Scene.terrain_smooth_shading


def noise(coord_x, coord_y, seed):
    """
    Generate hashed noise value for coordinates.

    Args:
        coord_x: X coordinate
        coord_y: Y coordinate
        seed: Random seed value

    Returns:
        Random float value between 0 and 1
    """
    random.seed(int((coord_x * 12.9898 + coord_y * 78.233 + seed) * 43758.5453))
    return random.random()


def smooth_noise(coord_x, coord_y, seed):
    """
    Interpolate noise values between neighboring points.

    Args:
        coord_x: X coordinate
        coord_y: Y coordinate
        seed: Random seed value

    Returns:
        Interpolated noise value
    """
    int_x = int(coord_x)
    int_y = int(coord_y)

    frac_x = coord_x - int_x
    frac_y = coord_y - int_y

    # Getting values of neighbour vertices
    v1 = noise(int_x, int_y, seed)
    v2 = noise(int_x + 1, int_y, seed)
    v3 = noise(int_x, int_y + 1, seed)
    v4 = noise(int_x + 1, int_y + 1, seed)

    # Cosine interpolation for smooth blending (horizontally)
    i1 = v1 + (v2 - v1) * (1 - math.cos(frac_x * math.pi)) * 0.5
    i2 = v3 + (v4 - v3) * (1 - math.cos(frac_x * math.pi)) * 0.5

    # Cosine interpolation to complete 2D noise
    return i1 + (i2 - i1) * (1 - math.cos(frac_y * math.pi)) * 0.5


def fractal_noise(coord_x, coord_y, frequency, seed, octaves, persistence):
    """
    Generate fractal noise by layering multiple octaves of noise.

    Args:
        coord_x: X coordinate
        coord_y: Y coordinate
        frequency: Noise frequency
        seed: Random seed value
        octaves: Number of noise layers
        persistence: How much detail layers blend together

    Returns:
        Normalized fractal noise value
    """
    total = 0
    amplitude = 1.0
    max_value = 0

    # Loop for each layer of noise, (big bumps, average bumps,...)
    for _ in range(octaves):
        total += smooth_noise(coord_x * frequency, coord_y * frequency, seed) * amplitude
        max_value += amplitude
        amplitude *= persistence
        frequency *= 2

    return total / max_value


def smooth_hill_bump(distance, radius, height, smoothness):
    """
    Calculate smooth hill based on distance from center of hill.

    Args:
        distance: Distance from hill center
        radius: Hill radius
        height: Hill height
        smoothness: Smoothness factor

    Returns:
        Height contribution from hill at given distance
    """
    # We ignore coordinates that won't be affected
    if distance > radius * smoothness:
        return 0

    # Normalize distance
    normalized_dist = distance / (radius * smoothness)

    # Make sure on float value
    value_t = max(0.0, min(1.0, 1.0 - normalized_dist))

    # Smoothstep formula
    smooth_t = value_t * value_t * (3.0 - 2.0 * value_t)

    return height * smooth_t


class TERRAIN_OT_generate(bpy.types.Operator):
    """Main operator for creating terrain."""

    bl_idname = "terrain.generate"
    bl_label = "Generate Terrain"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        """
        Execute terrain generation.

        Args:
            context: Blender context

        Returns:
            Dict with execution status
        """
        # Get all parameter values from UI properties
        scene = context.scene
        subdivisions = scene.terrain_subdivisions
        size = scene.terrain_size
        seed = scene.terrain_seed
        base_height = scene.terrain_base_height
        smooth_shading = scene.terrain_smooth_shading

        # Noise parameters
        noise_strength = scene.terrain_noise_strength
        octaves = scene.terrain_octaves
        frequency = scene.terrain_frequency
        persistence = scene.terrain_persistence

        # Hill parameters
        num_hills = scene.terrain_num_hills
        hill_height_min = scene.terrain_hill_height_min
        hill_height_max = scene.terrain_hill_height_max
        hill_radius_min = scene.terrain_hill_radius_min
        hill_radius_max = scene.terrain_hill_radius_max
        hill_smoothness = scene.terrain_hill_smoothness

        # Set the seed for random
        random.seed(seed)

        hills = []  # List of (x, y, radius, height)

        # Create coordinates for each center of hill
        for _ in range(num_hills):
            hill_x = random.uniform(-size/2, size/2)
            hill_y = random.uniform(-size/2, size/2)
            radius = random.uniform(hill_radius_min, hill_radius_max)
            height = random.uniform(hill_height_min, hill_height_max)
            hills.append((hill_x, hill_y, radius, height))

        # Set the object for scene
        mesh = bpy.data.meshes.new("TerrainMesh")
        obj = bpy.data.objects.new("Terrain", mesh)
        bpy.context.collection.objects.link(obj)

        verts = []
        faces = []
        grid_size = subdivisions + 1

        # Put every vertice into his place
        for coord_y in range(grid_size):
            for coord_x in range(grid_size):
                pos_x = (coord_x / subdivisions) * size - size / 2
                pos_y = (coord_y / subdivisions) * size - size / 2

                # Calculate noise coordinates
                noise_x = coord_x / subdivisions * 3
                noise_y = coord_y / subdivisions * 3
                noise_height = fractal_noise(
                    noise_x,
                    noise_y,
                    frequency,
                    seed,
                    octaves,
                    persistence
                )
                # Add the noise height into pos_z
                pos_z = base_height + (noise_height * noise_strength)

                # Add the hill height into pos_z
                for (hill_x, hill_y, radius, height) in hills:
                    distance = math.sqrt((pos_x - hill_x)**2 + (pos_y - hill_y)**2)
                    pos_z += smooth_hill_bump(distance, radius, height, hill_smoothness)

                # Put the vertex into list
                verts.append((pos_x, pos_y, pos_z))

        # Connects vertices by faces
        for coord_y in range(subdivisions):
            for coord_x in range(subdivisions):
                v1 = coord_y * grid_size + coord_x
                v2 = v1 + 1
                v3 = v1 + grid_size
                v4 = v3 + 1

                faces.append([v1, v2, v4, v3])

        # Is used to update the data and push it to the mesh into the scene
        mesh.from_pydata(verts, [], faces)
        mesh.update()

        # Smooth vertices if set true
        if smooth_shading:
            for poly in mesh.polygons:
                poly.use_smooth = True

        # Report for system
        self.report({'INFO'}, f"Terrain created: {len(verts)} vertices, {num_hills} hills")
        return {'FINISHED'}


class TERRAIN_PT_panel(bpy.types.Panel):
    """UI Panel for terrain generator."""

    bl_label = "Terrain Generator"
    bl_idname = "TERRAIN_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Make Terrain"

    def draw(self, context):
        """
        Draw the UI panel.

        Args:
            context: Blender context
        """
        layout = self.layout
        scene = context.scene

        # Basic settings
        box = layout.box()
        box.label(text="Basic Settings:", icon='SETTINGS')
        box.prop(scene, "terrain_subdivisions")
        box.prop(scene, "terrain_size")
        box.prop(scene, "terrain_seed")
        box.prop(scene, "terrain_base_height")
        box.prop(scene, "terrain_smooth_shading")

        # Noise settings
        box = layout.box()
        box.label(text="Terrain Detail (Noise):", icon='RNDCURVE')
        box.prop(scene, "terrain_noise_strength")
        box.prop(scene, "terrain_octaves")
        box.prop(scene, "terrain_frequency")
        box.prop(scene, "terrain_persistence")

        # Hill settings
        box = layout.box()
        box.label(text="Hills:", icon='SURFACE_NCIRCLE')
        box.prop(scene, "terrain_num_hills")
        box.prop(scene, "terrain_hill_height_min")
        box.prop(scene, "terrain_hill_height_max")
        box.prop(scene, "terrain_hill_radius_min")
        box.prop(scene, "terrain_hill_radius_max")
        box.prop(scene, "terrain_hill_smoothness")

        # Generate button
        layout.separator()
        row = layout.row()
        row.scale_y = 2.0
        row.operator("terrain.generate", text="Generate Terrain", icon='MESH_GRID')


# Registers for code to know how to start and end
classes = [
    TERRAIN_OT_generate,
    TERRAIN_PT_panel,
]


def register():
    """Register all classes and properties."""
    for cls in classes:
        register_class(cls)
    register_properties()


def unregister():
    """Unregister all classes and properties."""
    for cls in classes:
        unregister_class(cls)
    unregister_properties()


if __name__ == "__main__":
    register()